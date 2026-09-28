package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"net"
	"net/url"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/sst/opencode-sdk-go"
	"github.com/sst/opencode-sdk-go/option"
)

const (
	providerID = "deepseek"
	modelID    = "deepseek-flash"
)

// ErrOpenCodeUnreachable is returned when the OpenCode server cannot be reached.
// Callers must surface this to HTTP clients and must not fall back to OpenRouter.
var ErrOpenCodeUnreachable = errors.New("opencode server unreachable")

// Bridge talks to a local OpenCode server (attach or autostart) and keeps one
// OpenCode session per scan_id for sequential /complete prompts.
type Bridge struct {
	client    opencode.Client
	baseURL   string
	workDir   string
	autostart bool

	mu       sync.Mutex
	sessions map[string]string // scan_id -> opencode session id
	serveCmd *exec.Cmd

	permOnce sync.Once
	permStop context.CancelFunc
}

// BridgeConfig configures the OpenCode client side of the bridge.
type BridgeConfig struct {
	BaseURL   string
	WorkDir   string
	Autostart bool
}

// NewBridge builds a Bridge pointed at OPENCODE_BASE_URL (or cfg.BaseURL).
func NewBridge(cfg BridgeConfig) *Bridge {
	base := strings.TrimRight(cfg.BaseURL, "/")
	client := opencode.NewClient(
		option.WithBaseURL(base),
		option.WithMaxRetries(0),
	)
	return &Bridge{
		client:    client,
		baseURL:   base,
		workDir:   cfg.WorkDir,
		autostart: cfg.Autostart,
		sessions:  make(map[string]string),
	}
}

// Close stops the permission watcher and any OpenCode process we started.
func (b *Bridge) Close() {
	if b.permStop != nil {
		b.permStop()
	}
	b.mu.Lock()
	defer b.mu.Unlock()
	if b.serveCmd != nil && b.serveCmd.Process != nil {
		_ = b.serveCmd.Process.Kill()
		_, _ = b.serveCmd.Process.Wait()
		b.serveCmd = nil
	}
}

// Reachable reports whether the OpenCode HTTP API responds.
func (b *Bridge) Reachable(ctx context.Context) bool {
	ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
	defer cancel()
	_, err := b.client.Session.List(ctx, opencode.SessionListParams{
		Directory: opencode.F(b.workDir),
	})
	return err == nil
}

// EnsureOpenCode attaches to an existing server or starts `opencode serve`.
func (b *Bridge) EnsureOpenCode(ctx context.Context) error {
	if b.Reachable(ctx) {
		b.startPermissionWatcher()
		return nil
	}
	if !b.autostart {
		return fmt.Errorf("%w at %s (set OPENCODE_BASE_URL or enable OPENCODE_AUTOSTART)", ErrOpenCodeUnreachable, b.baseURL)
	}
	if err := b.startServe(ctx); err != nil {
		return err
	}
	deadline := time.Now().Add(30 * time.Second)
	for time.Now().Before(deadline) {
		if b.Reachable(ctx) {
			b.startPermissionWatcher()
			return nil
		}
		select {
		case <-ctx.Done():
			return fmt.Errorf("%w at %s: %w", ErrOpenCodeUnreachable, b.baseURL, ctx.Err())
		case <-time.After(250 * time.Millisecond):
		}
	}
	return fmt.Errorf("%w at %s after starting opencode serve", ErrOpenCodeUnreachable, b.baseURL)
}

func (b *Bridge) startServe(ctx context.Context) error {
	b.mu.Lock()
	defer b.mu.Unlock()
	if b.serveCmd != nil {
		return nil
	}
	u, err := url.Parse(b.baseURL)
	if err != nil {
		return fmt.Errorf("invalid OPENCODE_BASE_URL %q: %w", b.baseURL, err)
	}
	host := u.Hostname()
	if host == "" {
		host = "127.0.0.1"
	}
	port := u.Port()
	if port == "" {
		if u.Scheme == "https" {
			port = "443"
		} else {
			port = "4096"
		}
	}
	if err := waitForPortFree(host, port, 5*time.Second); err != nil {
		// Port in use — maybe another process is the server; caller will re-check Reachable.
		log.Printf("opencode-bridge: port %s:%s not free (%v); will retry attach", host, port, err)
	}

	cmd := exec.Command("opencode", "serve", "--hostname", host, "--port", port)
	cmd.Dir = b.workDir
	cmd.Env = os.Environ()
	cmd.Stdout = os.Stderr
	cmd.Stderr = os.Stderr
	if err := cmd.Start(); err != nil {
		return fmt.Errorf("%w: failed to start opencode serve: %v", ErrOpenCodeUnreachable, err)
	}
	b.serveCmd = cmd
	log.Printf("opencode-bridge: started opencode serve pid=%d at %s (cwd=%s)", cmd.Process.Pid, b.baseURL, b.workDir)

	go func() {
		err := cmd.Wait()
		b.mu.Lock()
		if b.serveCmd == cmd {
			b.serveCmd = nil
		}
		b.mu.Unlock()
		if err != nil {
			log.Printf("opencode-bridge: opencode serve exited: %v", err)
		}
	}()

	_ = ctx // reserved for future cancel-on-shutdown wiring
	return nil
}

func waitForPortFree(host, port string, timeout time.Duration) error {
	deadline := time.Now().Add(timeout)
	addr := net.JoinHostPort(host, port)
	for time.Now().Before(deadline) {
		ln, err := net.Listen("tcp", addr)
		if err == nil {
			_ = ln.Close()
			return nil
		}
		time.Sleep(100 * time.Millisecond)
	}
	return fmt.Errorf("address %s still in use", addr)
}

func (b *Bridge) startPermissionWatcher() {
	b.permOnce.Do(func() {
		ctx, cancel := context.WithCancel(context.Background())
		b.permStop = cancel
		go b.watchPermissions(ctx)
	})
}

func (b *Bridge) watchPermissions(ctx context.Context) {
	for {
		if ctx.Err() != nil {
			return
		}
		stream := b.client.Event.ListStreaming(ctx, opencode.EventListParams{
			Directory: opencode.F(b.workDir),
		})
		for stream.Next() {
			ev := stream.Current()
			union := ev.AsUnion()
			permEv, ok := union.(opencode.EventListResponseEventPermissionUpdated)
			if !ok {
				continue
			}
			perm := permEv.Properties
			if !shouldRejectPermission(perm.Type) {
				continue
			}
			log.Printf("opencode-bridge: rejecting permission type=%q session=%s id=%s", perm.Type, perm.SessionID, perm.ID)
			_, err := b.client.Session.Permissions.Respond(
				ctx,
				perm.SessionID,
				perm.ID,
				opencode.SessionPermissionRespondParams{
					Response:  opencode.F(opencode.SessionPermissionRespondParamsResponseReject),
					Directory: opencode.F(b.workDir),
				},
			)
			if err != nil {
				log.Printf("opencode-bridge: permission reject failed: %v", err)
			}
		}
		if err := stream.Err(); err != nil && ctx.Err() == nil {
			log.Printf("opencode-bridge: event stream ended: %v (reconnecting)", err)
			time.Sleep(500 * time.Millisecond)
			continue
		}
		return
	}
}

// Complete runs one prompt on the OpenCode session for scanID and returns assistant text.
func (b *Bridge) Complete(ctx context.Context, scanID, system, user string) (text string, sessionID string, err error) {
	if err := b.EnsureOpenCode(ctx); err != nil {
		return "", "", err
	}
	apiKey := strings.TrimSpace(os.Getenv("OPENCODE_API_KEY"))
	if apiKey == "" {
		apiKey = strings.TrimSpace(os.Getenv("DEEPSEEK_API_KEY"))
	}
	if apiKey == "" {
		return "", "", errors.New("OPENCODE_API_KEY or DEEPSEEK_API_KEY is required")
	}

	sessionID, err = b.sessionForScan(ctx, scanID)
	if err != nil {
		if isUnreachable(err) {
			return "", "", fmt.Errorf("%w at %s: %v", ErrOpenCodeUnreachable, b.baseURL, err)
		}
		return "", "", err
	}

	params := opencode.SessionPromptParams{
		Parts: opencode.F([]opencode.SessionPromptParamsPartUnion{
			opencode.TextPartInputParam{
				Text: opencode.F(user),
				Type: opencode.F(opencode.TextPartInputTypeText),
			},
		}),
		Directory: opencode.F(b.workDir),
		Model: opencode.F(opencode.SessionPromptParamsModel{
			ProviderID: opencode.F(providerID),
			ModelID:    opencode.F(modelID),
		}),
		// Defensive: never enable shell/edit tools even if config drifts.
		Tools: opencode.F(map[string]bool{
			"bash":  false,
			"shell": false,
			"edit":  false,
			"write": false,
		}),
	}
	if strings.TrimSpace(system) != "" {
		params.System = opencode.F(system)
	}

	resp, err := b.client.Session.Prompt(ctx, sessionID, params)
	if err != nil {
		if isUnreachable(err) {
			return "", sessionID, fmt.Errorf("%w at %s: %v", ErrOpenCodeUnreachable, b.baseURL, err)
		}
		return "", sessionID, err
	}
	return extractAssistantText(resp), sessionID, nil
}

func (b *Bridge) sessionForScan(ctx context.Context, scanID string) (string, error) {
	b.mu.Lock()
	if id, ok := b.sessions[scanID]; ok {
		b.mu.Unlock()
		return id, nil
	}
	b.mu.Unlock()

	session, err := b.client.Session.New(ctx, opencode.SessionNewParams{
		Directory: opencode.F(b.workDir),
		Title:     opencode.F("sentinai-scan-" + scanID),
	})
	if err != nil {
		return "", err
	}

	b.mu.Lock()
	defer b.mu.Unlock()
	if id, ok := b.sessions[scanID]; ok {
		// Another request created one first; keep the first mapping.
		return id, nil
	}
	b.sessions[scanID] = session.ID
	return session.ID, nil
}

func extractAssistantText(resp *opencode.SessionPromptResponse) string {
	if resp == nil {
		return ""
	}
	var b strings.Builder
	for _, part := range resp.Parts {
		switch p := part.AsUnion().(type) {
		case opencode.TextPart:
			b.WriteString(p.Text)
		}
	}
	return b.String()
}

func isUnreachable(err error) bool {
	if err == nil {
		return false
	}
	if errors.Is(err, ErrOpenCodeUnreachable) {
		return true
	}
	var netErr net.Error
	if errors.As(err, &netErr) {
		return true
	}
	var opErr *net.OpError
	if errors.As(err, &opErr) {
		return true
	}
	var urlErr *url.Error
	if errors.As(err, &urlErr) {
		return true
	}
	msg := strings.ToLower(err.Error())
	return strings.Contains(msg, "connection refused") ||
		strings.Contains(msg, "no such host") ||
		strings.Contains(msg, "i/o timeout") ||
		strings.Contains(msg, "actively refused")
}

// parseListenAddr returns host:port for the bridge HTTP server.
func parseListenAddr(raw string) string {
	raw = strings.TrimSpace(raw)
	if raw == "" {
		return "127.0.0.1:5010"
	}
	if strings.HasPrefix(raw, ":") {
		return "127.0.0.1" + raw
	}
	if _, err := strconv.Atoi(raw); err == nil {
		return "127.0.0.1:" + raw
	}
	return raw
}
