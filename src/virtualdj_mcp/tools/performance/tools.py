"""
Performance monitoring tools for VirtualDJ MCP
"""

from datetime import datetime
from typing import Any, Dict, Optional

from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_performance_monitor

# Initialize console for logging
console = Console(file=__import__('sys').stderr)


def setup_performance_tools(mcp: FastMCP):
    """
    Set up performance monitoring related MCP tools.

    Args:
        mcp: MCP instance to register tools with
    """

    @mcp.tool()
    async def get_performance_metrics() -> Dict[str, Any]:
        """
        Get current performance metrics.

        Returns:
            Dict containing current performance metrics including:
            - bpm_stability: Float (0.0 to 1.0) indicating BPM stability
            - beat_match_quality: Float (0.0 to 1.0) indicating beat matching quality
            - crowd_energy: Float (0.0 to 1.0) estimated crowd energy level
            - transition_smoothness: Float (0.0 to 1.0) transition quality
            - timestamp: ISO format timestamp
        """
        try:
            monitor = await get_performance_monitor()
            return await monitor.get_current_metrics()
        except Exception as e:
            console.print(f"[red]Error getting performance metrics: {e}[/red]")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    @mcp.tool()
    async def get_session_statistics(
        session_start: Optional[str] = None,
        session_end: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get DJ session statistics and analytics.

        Args:
            session_start: ISO format datetime for session start (optional)
            session_end: ISO format datetime for session end (optional)

        Returns:
            Dict containing session statistics including:
            - total_tracks: Number of tracks played
            - avg_bpm: Average BPM of session
            - energy_trend: Energy level progression
            - crowd_response: Estimated crowd response metrics
            - top_genres: Most played genres
            - timestamp: ISO format timestamp
        """
        try:
            monitor = await get_performance_monitor()
            return await monitor.get_session_stats(session_start, session_end)
        except Exception as e:
            console.print(f"[red]Error getting session statistics: {e}[/red]")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    @mcp.tool()
    async def analyze_performance_trends(
        hours: int = 24,
        metric: str = "energy"
    ) -> Dict[str, Any]:
        """
        Analyze performance trends over time.

        Args:
            hours: Number of hours to analyze (default: 24)
            metric: Metric to analyze ('energy', 'bpm_stability', 'crowd_response')

        Returns:
            Dict containing trend analysis including:
            - trend_direction: 'increasing', 'decreasing', 'stable'
            - average_value: Average value over the period
            - peak_value: Highest value in the period
            - data_points: List of timestamped data points
            - timestamp: ISO format timestamp
        """
        try:
            monitor = await get_performance_monitor()
            return await monitor.analyze_trends(hours, metric)
        except Exception as e:
            console.print(f"[red]Error analyzing performance trends: {e}[/red]")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    @mcp.tool()
    async def get_recommendations() -> Dict[str, Any]:
        """
        Get AI-powered recommendations for improving DJ performance.

        Returns:
            Dict containing recommendations including:
            - bpm_adjustments: Suggested BPM changes for better matching
            - energy_suggestions: When to increase/decrease energy
            - transition_tips: Specific transition improvement suggestions
            - crowd_engagement: Tips for better crowd response
            - timestamp: ISO format timestamp
        """
        try:
            monitor = await get_performance_monitor()
            return await monitor.get_recommendations()
        except Exception as e:
            console.print(f"[red]Error getting recommendations: {e}[/red]")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    @mcp.tool()
    async def export_performance_data(
        format: str = "json",
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export performance data for analysis or backup.

        Args:
            format: Export format ('json', 'csv', 'xml')
            filename: Optional custom filename (without extension)

        Returns:
            Dict containing export results including:
            - file_path: Path to exported file
            - record_count: Number of records exported
            - file_size: Size of exported file in bytes
            - timestamp: ISO format timestamp
        """
        try:
            monitor = await get_performance_monitor()
            return await monitor.export_data(format, filename)
        except Exception as e:
            console.print(f"[red]Error exporting performance data: {e}[/red]")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
