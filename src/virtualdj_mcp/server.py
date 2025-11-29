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
from pathlib import Path

# Add current directory to path for proper imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from rich.console import Console

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
    openapi_url="/api/openapi.json"
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
        console.print("[green]Portmanteau tools: vdj_deck, vdj_mixer, vdj_library, vdj_automation,[/green]")
        console.print("[green]  vdj_recording, vdj_performance, vdj_stems, vdj_beatgrid,[/green]")
        console.print("[green]  vdj_skin, vdj_video, vdj_plex, vdj_system[/green]")
        
    else:
        # INDIVIDUAL MODE: 62+ individual tools
        # For backward compatibility or fine-grained control
        console.print("[blue]Using INDIVIDUAL tool mode (62+ tools)[/blue]")
        
        from .tools.deck_control.tools import setup_deck_control_tools
        setup_deck_control_tools(mcp)

        from .tools.mixing.tools import setup_mixing_tools
        setup_mixing_tools(mcp)

        from .tools.library.tools import setup_library_tools
        setup_library_tools(mcp)

        from .tools.automation.tools import setup_auto_dj_tools
        setup_auto_dj_tools(mcp)

        from .tools.recording.tools import setup_recording_tools
        setup_recording_tools(mcp)

        from .tools.performance.tools import setup_performance_tools
        setup_performance_tools(mcp)

        from .tools.shared.help_tools import setup_help_tools
        setup_help_tools(mcp)

        from .tools.skin.tools import setup_skin_tools
        setup_skin_tools(mcp)

        from .tools.stems.tools import setup_stem_tools
        setup_stem_tools(mcp)

        from .tools.beatgrid.tools import setup_beatgrid_tools
        setup_beatgrid_tools(mcp)

        from .tools.video.tools import setup_video_tools
        setup_video_tools(mcp)
        
        tools_loaded = 62

    # Initialize system status
    from .tools.shared.dependencies import update_system_status
    update_system_status("server_started", True)
    update_system_status("tools_loaded", tools_loaded)
    update_system_status("tool_mode", TOOL_MODE)

    console.print(f"[green]VirtualDJ-MCP: {tools_loaded} tools registered successfully[/green]")

except Exception as e:
    console.print(f"[red]Error registering tools: {e}[/red]")
    raise

# Import FastAPI routes
from .api.app import create_app

# Create FastAPI app instance
api_app = create_app()

# Mount FastAPI routes
fastapi_app.mount("/api/v1", api_app, name="api")

# Add health endpoint to FastAPI
@fastapi_app.get("/health")
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "VirtualDJ-MCP"
    }

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
    console.print("[blue]Available at: http://localhost:8000/api/docs[/blue]")

    try:
        config = uvicorn.Config(
            fastapi_app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
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
__all__ = ["mcp", "main", "run_fastapi"]

if __name__ == "__main__":
    # When run directly, start the MCP server
    main()
