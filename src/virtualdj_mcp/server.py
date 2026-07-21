"""
VirtualDJ-MCP Server - FastMCP 2.13+ Implementation

Thin server file that imports and registers all tools.
Supports both MCP and FastAPI interfaces as required.

TOOL MODES:
- PORTMANTEAU (default): 13 consolidated tools for cleaner AI interface
- INDIVIDUAL: 62+ individual tools for fine-grained control

Set VDJ_TOOL_MODE=individual to use individual tools instead of portmanteau.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import psutil
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastmcp import FastMCP
from rich.console import Console

from .api.app import create_app
from .config import VDJConfig
from .tools.shared.dependencies import update_system_status

# Add current directory to path for proper imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Initialize console for logging (redirect to stderr for MCP compatibility)
console = Console(file=sys.stderr)

# Tool mode: "portmanteau" (default) or "individual"
TOOL_MODE = os.getenv("VDJ_TOOL_MODE", "portmanteau").lower()

# Initialize FastMCP server
mcp = FastMCP("VirtualDJ-MCP 🎵")

# Create FastAPI app
fastapi_app = FastAPI(
    title="VirtualDJ-MCP API",
    description="REST API for VirtualDJ automation and control",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS for FastAPI
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and setup all tool categories
try:
    if TOOL_MODE == "portmanteau":
        # PORTMANTEAU MODE (default): 13 consolidated tools
        # Better for AI assistants - fewer tools, cleaner interface
        console.print("[blue]Using PORTMANTEAU tool mode (13 tools)[/blue]")

        from .tools.portmanteau import setup_all_portmanteau_tools

        setup_all_portmanteau_tools(mcp)

        tools_loaded = 13
        console.print(
            "[green]Portmanteau tools: vdj_deck, vdj_mixer, vdj_library, vdj_automation,[/green]"
        )
        console.print(
            "[green]  vdj_recording, vdj_performance, vdj_stems, vdj_beatgrid,[/green]"
        )
        console.print("[green]  vdj_skin, vdj_video, vdj_plex, vdj_system[/green]")

    else:
        # INDIVIDUAL MODE: Legacy tools (archived in _legacy/)
        # Use portmanteau mode for new development
        console.print(
            "[yellow]INDIVIDUAL mode deprecated - using PORTMANTEAU instead[/yellow]"
        )
        console.print("[yellow]Legacy tools archived in tools/_legacy/[/yellow]")

        from .tools.portmanteau import setup_all_portmanteau_tools

        setup_all_portmanteau_tools(mcp)

        tools_loaded = 12

    # Initialize system status
    update_system_status("server_started", True)
    update_system_status("tools_loaded", tools_loaded)
    update_system_status("tool_mode", TOOL_MODE)

    console.print(
        f"[green]VirtualDJ-MCP: {tools_loaded} tools registered successfully[/green]"
    )

except Exception as e:
    console.print(f"[red]Error registering tools: {e}[/red]")
    raise

# Create FastAPI app instance
api_app = create_app()

# Mount FastAPI routes
fastapi_app.mount("/api/v1", api_app, name="api")


# Add health endpoint to FastAPI
@fastapi_app.get("/health")
async def health_check():
    """Health check endpoint with system metrics"""
    # Get system metrics
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "VirtualDJ-MCP",
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "percent": memory.percent,
                "used": memory.used,
                "total": memory.total,
            },
            "disk": {"percent": disk.percent, "used": disk.used, "total": disk.total},
        },
    }


@fastapi_app.get("/")
async def api_root():
    """Standard root endpoint for cross-repo discovery."""
    return {
        "service": "virtualdj-mcp",
        "status": "healthy",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "api_root": "/api",
        "api_v1": "/api/v1",
        "health": "/health",
    }


@fastapi_app.get("/api")
async def api_index():
    """Standard API index endpoint."""
    return {
        "service": "virtualdj-mcp",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "settings": "/api/settings",
            "deck_status": "/api/v1/deck/{deck_id}/status",
            "deck_load": "/api/v1/deck/{deck_id}/load",
            "deck_play_pause": "/api/v1/deck/{deck_id}/play_pause",
            "deck_sync": "/api/v1/deck/{deck_id}/sync",
            "deck_cue": "/api/v1/deck/{deck_id}/cue",
            "library_search": "/api/v1/library/search",
            "audio_analyze": "/api/v1/audio/analyze",
        },
    }


@fastapi_app.get("/api/health")
async def api_health_alias():
    return await health_check()


@fastapi_app.get("/api/settings")
async def api_settings_alias():
    cfg = VDJConfig.from_env()
    return {
        "osc_port": cfg.osc_port,
        "http_host": cfg.http_host,
        "http_port": cfg.http_port,
    }


@fastapi_app.get("/docs")
async def docs_alias():
    return RedirectResponse(url="/api/docs", status_code=307)


@fastapi_app.get("/openapi.json")
async def openapi_alias():
    return RedirectResponse(url="/api/openapi.json", status_code=307)


# Uvicorn expects an ASGI callable named "app" when using `module:app`.
# `web_sota\start.ps1` launches `uvicorn virtualdj_mcp.server:app`.
app = fastapi_app


def main():
    """Main application entry point for MCP server"""
    console.print("[green]VirtualDJ-MCP MCP Server starting...[/green]")
    console.print("[blue]Running in MCP stdio mode for Claude Desktop[/blue]")

    try:
        # Run MCP server with stdio transport for Claude Desktop
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        console.print("[yellow]MCP Server shutdown requested[/yellow]")
    except Exception as e:
        console.print(f"[red]MCP Server error: {e}[/red]")
        raise
    finally:
        console.print("[green]VirtualDJ-MCP MCP Server stopped[/green]")


async def run_fastapi():
    """Run FastAPI server"""
    console.print("[green]VirtualDJ-MCP FastAPI Server starting...[/green]")
    console.print("[blue]Available at: http://localhost:10877/api/docs[/blue]")

    try:
        config = uvicorn.Config(
            fastapi_app, host="127.0.0.1", port=10877, log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        console.print("[yellow]FastAPI Server shutdown requested[/yellow]")
    except Exception as e:
        console.print(f"[red]FastAPI Server error: {e}[/red]")
        raise
    finally:
        console.print("[green]VirtualDJ-MCP FastAPI Server stopped[/green]")


# For Claude Desktop MCP integration, just export the MCP instance
# Claude Desktop will handle running the server
__all__ = ["app", "main", "mcp", "run_fastapi"]

if __name__ == "__main__":
    # When run directly, start the MCP server
    main()
