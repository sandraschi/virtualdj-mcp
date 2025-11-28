'''MCP server entry point for VirtualDJ-MCP.

This is the MCPB-compliant server wrapper that launches the VirtualDJ-MCP server.
FastMCP 2.13+
'''

import sys
from pathlib import Path

# Add src directory to path to import main server
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run main server
from virtualdj_mcp.server import main

if __name__ == '__main__':
    main()

