"""PyInstaller entry point — HTTP/uvicorn server for Tauri backend.

Reads PORT and HOST from environment (set by backend.rs), starts the
FastAPI application. Supports dual transport: when PORT is set, runs
as HTTP server; otherwise falls through to stdio MCP mode.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

port = os.environ.get("PORT") or os.environ.get("MCP_PORT")
if port:
    host = os.environ.get("HOST", "127.0.0.1")
    import uvicorn
    from virtualdj_mcp.server import app
    uvicorn.run(app, host=host, port=int(port), log_level="info")
else:
    from virtualdj_mcp.server import main
    main()
