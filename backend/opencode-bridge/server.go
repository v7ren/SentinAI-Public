package main

import (
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"strings"
	"time"
)

type completeRequest struct {
	ScanID string `json:"scan_id"`
	System string `json:"system"`
	User   string `json:"user"`
}

type completeResponse struct {
	ScanID    string `json:"scan_id"`
	Text      string `json:"text"`
	SessionID string `json:"session_id,omitempty"`
	Model     string `json:"model"`
}

type errorResponse struct {
	Error string `json:"error"`
}

type healthResponse struct {
	OK       bool   `json:"ok"`
	Opencode string `json:"opencode"`
	Model    string `json:"model"`
	BaseURL  string `json:"opencode_base_url"`
}

// Server is the localhost HTTP surface for the Python worker.
type Server struct {
	Bridge *Bridge
}

func (s *Server) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", s.handleHealth)
	mux.HandleFunc("POST /complete", s.handleComplete)
	return mux
}

func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	reachable := s.Bridge.Reachable(r.Context())
	status := "unreachable"
	if reachable {
		status = "reachable"
	}
	writeJSON(w, http.StatusOK, healthResponse{
		OK:       true,
		Opencode: status,
		Model:    modelID,
		BaseURL:  s.Bridge.baseURL,
	})
}

func (s *Server) handleComplete(w http.ResponseWriter, r *http.Request) {
	var req completeRequest
	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()
	if err := dec.Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, errorResponse{Error: "invalid JSON body: " + err.Error()})
		return
	}
	req.ScanID = strings.TrimSpace(req.ScanID)
	req.User = strings.TrimSpace(req.User)
	if req.ScanID == "" {
		writeJSON(w, http.StatusBadRequest, errorResponse{Error: "scan_id is required"})
		return
	}
	if req.User == "" {
		writeJSON(w, http.StatusBadRequest, errorResponse{Error: "user is required"})
		return
	}

	ctx := r.Context()
	text, sessionID, err := s.Bridge.Complete(ctx, req.ScanID, req.System, req.User)
	if err != nil {
		status := http.StatusBadGateway
		if errors.Is(err, ErrOpenCodeUnreachable) || isUnreachable(err) {
			status = http.StatusServiceUnavailable
		}
		log.Printf("opencode-bridge: /complete failed scan_id=%s: %v", req.ScanID, err)
		writeJSON(w, status, errorResponse{Error: err.Error()})
		return
	}

	writeJSON(w, http.StatusOK, completeResponse{
		ScanID:    req.ScanID,
		Text:      text,
		SessionID: sessionID,
		Model:     modelID,
	})
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	enc := json.NewEncoder(w)
	enc.SetEscapeHTML(false)
	_ = enc.Encode(v)
}

// newHTTPServer builds the stdlib server with long timeouts for model waits.
func newHTTPServer(addr string, handler http.Handler) *http.Server {
	return &http.Server{
		Addr:              addr,
		Handler:           handler,
		ReadHeaderTimeout: 10 * time.Second,
		ReadTimeout:       30 * time.Second,
		WriteTimeout:      10 * time.Minute,
		IdleTimeout:       2 * time.Minute,
	}
}
