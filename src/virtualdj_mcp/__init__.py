"""
VirtualDJ-MCP - FastMCP 2.10 Server for Professional DJ Automation

Austrian efficiency for Sandra's music mixing and DJ automation needs.
"""

__version__ = "1.0.0"
__author__ = "Sandra (sandraschi)"
__description__ = "FastMCP server for VirtualDJ automation and control"

from .config import VDJConfig
from .server import mcp

__all__ = ["VDJConfig", "mcp"]
