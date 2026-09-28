#!/usr/bin/env python3
"""
Start the Agent Log Server.

This script starts the WebSocket-based log server for real-time monitoring
of AI agent activities during security scans.

Usage:
    python -m backend.worker.core.start_log_server
    python backend/worker/core/start_log_server.py

Environment Variables:
    LOG_SERVER_PORT: Port to run the server on (default: 5003)
    LOG_SERVER_HOST: Host to bind to (default: 0.0.0.0)
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.worker.core.log_server import run_server


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start the SentinAI Agent Log Server")
    parser.add_argument("--port", "-p", type=int, default=None, help="Port to run the server on (default: 5003)")
    parser.add_argument("--host", "-H", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    
    args = parser.parse_args()
    
    run_server(port=args.port, host=args.host)