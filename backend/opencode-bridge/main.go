package main

import (
	"context"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"syscall"
	"time"
)

func main() {
	workDir, err := os.Getwd()
	if err != nil {
		log.Fatalf("getcwd: %v", err)
	}
	// Prefer the directory that contains this binary's opencode.json when run via `go run`.
	if _, err := os.Stat(filepath.Join(workDir, "opencode.json")); err != nil {
		if exe, e := os.Executable(); e == nil {
			candidate := filepath.Dir(ex)
			if _, err := os.Stat(filepath.Join(candidate, "opencode.json")); err == nil {
				workDir = candidate
			}
		}
	}

	baseURL := envOr("OPENCODE_BASE_URL", "http://127.0.0.1:4096")
	listen := parseListenAddr(envOr("BRIDGE_LISTEN", "127.0.0.1:5010"))
	autostart := envOr("OPENCODE_AUTOSTART", "1") != "0"

	if os.Getenv("DEEPSEEK_API_KEY") == "" {
		log.Printf("opencode-bridge: warning: DEEPSEEK_API_KEY is unset; /complete will fail until it is set")
	}

	bridge := NewBridge(BridgeConfig{
		BaseURL:   baseURL,
		WorkDir:   workDir,
		Autostart: autostart,
	})
	defer bridge.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 45*time.Second)
	if err := bridge.EnsureOpenCode(ctx); err != nil {
		log.Printf("opencode-bridge: OpenCode not ready at startup: %v (will retry on /complete)", err)
	}
	cancel()

	srv := &Server{Bridge: bridge}
	httpServer := newHTTPServer(listen, srv.Handler())

	go func() {
		log.Printf("opencode-bridge listening on http://%s (opencode=%s model=%s)", listen, baseURL, modelID)
		if err := httpServer.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Printf("opencode-bridge: server stopped: %v", err)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop

	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer shutdownCancel()
	_ = httpServer.Shutdown(shutdownCtx)
	bridge.Close()
}

func envOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
