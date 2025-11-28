"""
Shared exceptions for VirtualDJ MCP tools

Re-exports VDJError from core module for convenient imports.
"""

from ...core.vdj_client import VDJError

__all__ = ["VDJError"]
