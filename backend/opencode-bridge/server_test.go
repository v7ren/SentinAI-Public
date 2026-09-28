package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestShouldRejectPermission(t *testing.T) {
	cases := []struct {
		in   string
		want bool
	}{
		{"bash", true},
		{"Bash", true},
		{"shell", true},
		{"edit", true},
		{"write", true},
		{"read", false},
		{"glob", false},
		{"", false},
		{"  EDIT ", true},
	}
	for _, tc := range cases {
		if got := shouldRejectPermission(tc.in); got != tc.want {
			t.Fatalf("shouldRejectPermission(%q)=%v want %v", tc.in, got, tc.want)
		}
	}
}

func TestParseListenAddr(t *testing.T) {
	cases := map[string]string{
		"":             "127.0.0.1:5010",
		":8080":        "127.0.0.1:8080",
		"5010":         "127.0.0.1:5010",
		"0.0.0.0:5010": "0.0.0.0:5010",
	}
	for in, want := range cases {
		if got := parseListenAddr(in); got != want {
			t.Fatalf("parseListenAddr(%q)=%q want %q", in, got, want)
		}
	}
}

func TestHealthHandler(t *testing.T) {
	bridge := NewBridge(BridgeConfig{
		BaseURL:   "http://127.0.0.1:9", // closed port
		WorkDir:   t.TempDir(),
		Autostart: false,
	})
	srv := &Server{Bridge: bridge}
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()
	srv.Handler().ServeHTTP(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("status=%d body=%s", rec.Code, rec.Body.String())
	}
	var body healthResponse
	if err := json.Unmarshal(rec.Body.Bytes(), &body); err != nil {
		t.Fatal(err)
	}
	if body.Model != modelID {
		t.Fatalf("model=%q", body.Model)
	}
	if body.Opencode != "unreachable" {
		t.Fatalf("opencode status=%q", body.Opencode)
	}
}

func TestCompleteRejectsMissingFields(t *testing.T) {
	bridge := NewBridge(BridgeConfig{
		BaseURL:   "http://127.0.0.1:9",
		WorkDir:   t.TempDir(),
		Autostart: false,
	})
	srv := &Server{Bridge: bridge}

	payload, _ := json.Marshal(map[string]string{"scan_id": "", "user": "hi"})
	req := httptest.NewRequest(http.MethodPost, "/complete", bytes.NewReader(payload))
	rec := httptest.NewRecorder()
	srv.Handler().ServeHTTP(rec, req)
	if rec.Code != http.StatusBadRequest {
		t.Fatalf("status=%d body=%s", rec.Code, rec.Body.String())
	}
}

func TestCompleteUnreachableDoesNotCallOpenRouter(t *testing.T) {
	bridge := NewBridge(BridgeConfig{
		BaseURL:   "http://127.0.0.1:9",
		WorkDir:   t.TempDir(),
		Autostart: false,
	})
	t.Setenv("DEEPSEEK_API_KEY", "test-key")

	ctx := context.Background()
	_, _, err := bridge.Complete(ctx, "scan-1", "sys", "user prompt")
	if err == nil {
		t.Fatal("expected error")
	}
	if !errors.Is(err, ErrOpenCodeUnreachable) && !isUnreachable(err) && !strings.Contains(err.Error(), "unreachable") {
		t.Fatalf("expected unreachable error, got %v", err)
	}
	if strings.Contains(strings.ToLower(err.Error()), "openrouter") {
		t.Fatalf("must not mention OpenRouter: %v", err)
	}

	srv := &Server{Bridge: bridge}
	payload, _ := json.Marshal(completeRequest{ScanID: "scan-1", System: "s", User: "u"})
	req := httptest.NewRequest(http.MethodPost, "/complete", bytes.NewReader(payload))
	rec := httptest.NewRecorder()
	srv.Handler().ServeHTTP(rec, req)
	if rec.Code != http.StatusServiceUnavailable {
		t.Fatalf("status=%d body=%s", rec.Code, rec.Body.String())
	}
	var body errorResponse
	if err := json.Unmarshal(rec.Body.Bytes(), &body); err != nil {
		t.Fatal(err)
	}
	if body.Error == "" {
		t.Fatal("expected error message")
	}
	if strings.Contains(strings.ToLower(body.Error), "openrouter") {
		t.Fatalf("must not mention OpenRouter: %q", body.Error)
	}
}
