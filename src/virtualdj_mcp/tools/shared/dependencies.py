"""
Shared dependencies and utilities for VirtualDJ MCP tools
"""

from datetime import datetime
from typing import Any, Dict, Optional

from ...config import VDJConfig

# Import from core modules
from ...core.vdj_client import VDJError, VirtualDJClient
from ...services.performance_monitor import PerformanceMonitor

# Global managers (initialized on startup)
vdj_client: Optional[VirtualDJClient] = None
config: Optional[VDJConfig] = None
performance_monitor: Optional[PerformanceMonitor] = None


async def get_vdj_client() -> VirtualDJClient:
    """Get initialized VirtualDJ client"""
    global vdj_client, config

    if vdj_client is None:
        config = VDJConfig.from_env()
        if not config.validate_paths():
            raise VDJError("VirtualDJ path validation failed")

        vdj_client = VirtualDJClient(config)

        # Start VirtualDJ if needed
        async with vdj_client:
            if not await vdj_client.start_virtualdj():
                raise VDJError("Failed to start VirtualDJ")

    return vdj_client


async def get_performance_monitor() -> PerformanceMonitor:
    """Get initialized PerformanceMonitor instance"""
    global performance_monitor, vdj_client

    if performance_monitor is None:
        if vdj_client is None:
            # Initialize VDJ client first
            await get_vdj_client()

        performance_monitor = PerformanceMonitor(vdj_client)

    return performance_monitor


# System status tracking
_system_status = {
    "server_started": False,
    "vdj_connected": False,
    "last_health_check": None,
    "tools_loaded": 0,
    "uptime_seconds": 0
}


def update_system_status(key: str, value: Any):
    """Update system status"""
    _system_status[key] = value
    if key == "server_started" and value:
        _system_status["last_health_check"] = datetime.now().isoformat()
        import time
        _system_status["start_time"] = time.time()


def get_system_status() -> Dict[str, Any]:
    """Get current system status"""
    return _system_status.copy()
