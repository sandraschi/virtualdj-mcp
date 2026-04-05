"""
Performance Monitoring for VirtualDJ-MCP

This module provides tools for monitoring and analyzing DJ performance metrics
including BPM stability, transition quality, and energy flow.
"""
import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from rich.console import Console

from ..core.vdj_client import VirtualDJClient


@dataclass
class TrackAnalysis:
    """Analysis of a single track's performance."""
    track_id: str
    title: str
    artist: str
    bpm: float
    key: str
    energy: float  # 0.0 to 1.0
    start_time: datetime
    end_time: datetime | None = None
    bpm_variance: float = 0.0
    peak_volume: float = 0.0
    avg_volume: float = 0.0
    volume_samples: list[float] = field(default_factory=list)
    bpm_samples: list[float] = field(default_factory=list)

    def add_sample(self, volume: float, bpm: float):
        """Add a volume and BPM sample."""
        self.volume_samples.append(volume)
        self.bpm_samples.append(bpm)

        # Update peak volume
        if volume > self.peak_volume:
            self.peak_volume = volume

        # Update BPM variance
        if len(self.bpm_samples) > 1:
            self.bpm_variance = sum(
                (bpm - (sum(self.bpm_samples) / len(self.bpm_samples))) ** 2
                for bpm in self.bpm_samples
            ) / len(self.bpm_samples)

def calculate_energy_level(bpm: float, key: str) -> float:
    """Calculate an energy level (0.0 to 1.0) based on BPM and key."""
    # Base energy from BPM (normalized 70-180 BPM to 0.0-1.0)
    bpm_energy = min(max((bpm - 70) / 110, 0.0), 1.0)

    # Adjust based on key (Camelot wheel position)
    key_energy = 0.5  # Default
    if key:
        try:
            key_num = int(key[:-1])  # Extract number (e.g., 5A -> 5)
            key_energy = key_num / 12.0  # 1-12 to 0.08-1.0
        except (ValueError, AttributeError):
            pass

    # Weighted average (70% BPM, 30% key)
    return (bpm_energy * 0.7) + (key_energy * 0.3)

class PerformanceMonitor:
    """Monitors and analyzes DJ performance metrics."""

    def __init__(self, vdj_client: VirtualDJClient):
        """Initialize the performance monitor."""
        self.vdj = vdj_client
        self.console = Console()

        # Track history
        self.track_history: list[TrackAnalysis] = []
        self.current_track: TrackAnalysis | None = None
        self.last_update = datetime.now()

        # Performance metrics
        self.metrics = {
            'bpm_stability': 1.0,  # 0.0 to 1.0
            'beat_match_quality': 1.0,  # 0.0 to 1.0
            'energy_flow': 'steady',  # 'increasing', 'decreasing', 'erratic', 'steady'
            'transition_quality': 1.0,  # 0.0 to 1.0
            'alerts': []
        }

        # Background task for monitoring
        self._monitor_task: asyncio.Task | None = None
        self._running = False

    async def start_monitoring(self):
        """Start the background monitoring task."""
        if self._running:
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self):
        """Stop the background monitoring task."""
        if not self._running:
            return

        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self):
        """Background task that monitors performance metrics."""
        while self._running:
            try:
                await self._update_metrics()
                await asyncio.sleep(2)  # Update every 2 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.console.print(f"[red]Error in monitor loop: {e}[/]")
                await asyncio.sleep(5)  # Wait before retrying

    async def _update_metrics(self):
        """Update performance metrics based on current state."""
        now = datetime.now()

        # Get current deck status using CLI variables
        try:
            # Get track information from VirtualDJ variables
            track_title = await self.vdj.get_variable('deck1_title')
            track_artist = await self.vdj.get_variable('deck1_artist')
            track_bpm = float(await self.vdj.get_variable('deck1_bpm') or 0)
            float(await self.vdj.get_variable('deck1_position') or 0)
            track_volume = float(await self.vdj.get_variable('deck1_volume') or 0)

            # Skip if no track loaded
            if not track_title or track_title == '':
                return

            # Create a simple track representation
            track_id = f"{track_title}_{track_artist}_{track_bpm}"

            # Check if track has changed
            if not self.current_track or self.current_track.track_id != track_id:
                # Finalize previous track
                if self.current_track:
                    self.current_track.end_time = now
                    self.track_history.append(self.current_track)

                # Start new track analysis
                self.current_track = TrackAnalysis(
                    track_id=track_id,
                    title=track_title,
                    artist=track_artist,
                    bpm=track_bpm,
                    key='',  # We don't have key info from CLI variables
                    energy=calculate_energy_level(track_bpm, ''),
                    start_time=now
                )

            # Add current sample to track analysis
            if self.current_track:
                self.current_track.add_sample(
                    volume=track_volume,
                    bpm=track_bpm
                )

                # Update BPM stability (1.0 = perfect stability)
                if len(self.current_track.bpm_samples) > 1:
                    bpm_std = (sum((x - self.current_track.bpm) ** 2 for x in self.current_track.bpm_samples) /
                              len(self.current_track.bpm_samples)) ** 0.5
                    self.metrics['bpm_stability'] = max(0, 1 - (bpm_std / 5.0))  # 5 BPM std dev = 0 stability

                # Update beat match quality (if we have multiple decks)
                # This is a simplified example - in a real implementation, you'd analyze
                # the phase alignment between decks
                self.metrics['beat_match_quality'] = 0.9  # Placeholder

                # Update energy flow
                if len(self.track_history) >= 2:
                    prev_energy = self.track_history[-1].energy
                    current_energy = self.current_track.energy
                    energy_diff = current_energy - prev_energy

                    if energy_diff > 0.1:
                        self.metrics['energy_flow'] = 'increasing'
                    elif energy_diff < -0.1:
                        self.metrics['energy_flow'] = 'decreasing'
                    else:
                        self.metrics['energy_flow'] = 'steady'

                # Check for alerts
                self._check_alerts()

            self.last_update = now

        except Exception as e:
            self.console.print(f"[red]Error updating metrics: {e}[/]")

    def _check_alerts(self):
        """Check for performance issues and generate alerts."""
        if not self.current_track:
            return

        # Check for BPM drift
        if self.metrics['bpm_stability'] < 0.7:  # 30% or more BPM variance
            self.metrics['alerts'].append(
                f"BPM stability low ({self.metrics['bpm_stability']:.0%}) - check beatmatching"
            )

        # Check for clipping
        if self.current_track.peak_volume > 0.95:  # 95% of max volume
            self.metrics['alerts'].append("Warning: Audio clipping detected!")

    async def get_current_metrics(self) -> dict[str, Any]:
        """Get current performance metrics."""
        metrics = self.metrics.copy()

        # Add current track info
        if self.current_track:
            metrics['current_track'] = {
                'title': self.current_track.title,
                'artist': self.current_track.artist,
                'bpm': self.current_track.bpm,
                'key': self.current_track.key,
                'energy': self.current_track.energy
            }

        # Add track history
        metrics['track_history'] = [
            {
                'title': t.title,
                'artist': t.artist,
                'bpm': t.bpm,
                'key': t.key,
                'energy': t.energy,
                'duration': (t.end_time - t.start_time).total_seconds() if t.end_time else 0
            }
            for t in self.track_history[-10:]  # Last 10 tracks
        ]

        return metrics

    async def generate_report(self, output_path: Path | None = None) -> dict[str, Any]:
        """Generate a performance report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'session_duration': 0.0,  # Will be calculated
            'tracks_played': len(self.track_history) + (1 if self.current_track else 0),
            'avg_bpm_stability': 0.0,
            'avg_transition_quality': 0.0,
            'tracks': [],
            'alerts': self.metrics['alerts'].copy()
        }

        # Calculate session duration
        if self.track_history:
            start_time = self.track_history[0].start_time
            end_time = self.current_track.start_time if self.current_track else self.track_history[-1].end_time

            if end_time and start_time:
                report['session_duration'] = (end_time - start_time).total_seconds() / 60  # in minutes

        # Calculate average metrics
        if self.track_history:
            report['avg_bpm_stability'] = sum(
                t.bpm_variance for t in self.track_history
            ) / len(self.track_history)

            # This would be calculated based on transition analysis in a real implementation
            report['avg_transition_quality'] = 0.85  # Placeholder

        # Add track details
        for track in self.track_history:
            report['tracks'].append({
                'title': track.title,
                'artist': track.artist,
                'bpm': track.bpm,
                'key': track.key,
                'energy': track.energy,
                'duration': (track.end_time - track.start_time).total_seconds() if track.end_time else 0,
                'bpm_stability': 1 - (track.bpm_variance / 25.0) if track.bpm_variance > 0 else 1.0,
                'peak_volume': track.peak_volume
            })

        # Save to file if path is provided
        if output_path:
            try:
                with open(output_path, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
            except Exception as e:
                self.console.print(f"[red]Error saving report: {e}[/]")

        return report

    async def get_recommendations(self) -> dict[str, Any]:
        """Generate AI-powered recommendations for improving DJ performance."""
        recommendations = {
            'timestamp': datetime.now().isoformat(),
            'bpm_adjustments': [],
            'energy_suggestions': [],
            'transition_tips': [],
            'crowd_engagement': []
        }

        # BPM adjustments based on current track stability
        if self.metrics['bpm_stability'] < 0.8:
            recommendations['bpm_adjustments'].append({
                'type': 'bpm_stabilization',
                'message': f"BPM stability is low ({self.metrics['bpm_stability']:.0%}). Consider using VirtualDJ's beat grid to stabilize the beat detection.",
                'severity': 'high'
            })

        # Energy suggestions based on flow
        if self.metrics['energy_flow'] == 'erratic':
            recommendations['energy_suggestions'].append({
                'type': 'energy_flow',
                'message': "Energy flow is erratic. Try to maintain a more consistent energy progression throughout the set.",
                'severity': 'medium'
            })

        # Transition tips based on recent tracks
        if len(self.track_history) >= 2:
            recent_tracks = self.track_history[-2:]
            bpm_diff = abs(recent_tracks[1].bpm - recent_tracks[0].bpm)

            if bpm_diff > 10:
                recommendations['transition_tips'].append({
                    'type': 'bpm_transition',
                    'message': f"Large BPM change detected ({bpm_diff:.0f} BPM). Consider using VirtualDJ's pitch bend or tempo controls for smoother transitions.",
                    'severity': 'high'
                })

        # Crowd engagement tips
        if self.metrics['beat_match_quality'] < 0.8:
            recommendations['crowd_engagement'].append({
                'type': 'beat_matching',
                'message': "Beat matching quality could be improved. Perfect beat alignment helps maintain crowd energy.",
                'severity': 'medium'
            })

        # General recommendations
        if not recommendations['bpm_adjustments'] and not recommendations['energy_suggestions'] and not recommendations['transition_tips']:
            recommendations['general'] = [{
                'type': 'general',
                'message': "Performance looks good! Keep monitoring BPM stability and energy flow.",
                'severity': 'low'
            }]

        return recommendations

    async def get_session_stats(self, start_time: datetime, end_time: datetime) -> dict[str, Any]:
        """Get session statistics for a time period."""
        session_tracks = [
            track for track in self.track_history
            if start_time <= track.start_time <= end_time
        ]

        if not session_tracks:
            return {
                'tracks_played': 0,
                'avg_bpm': 0.0,
                'energy_range': [0.0, 0.0],
                'session_duration': 0.0,
                'timestamp': datetime.now().isoformat()
            }

        # Calculate session statistics
        bpms = [track.bpm for track in session_tracks]
        energies = [track.energy for track in session_tracks]

        return {
            'tracks_played': len(session_tracks),
            'avg_bpm': sum(bpms) / len(bpms) if bpms else 0.0,
            'energy_range': [min(energies), max(energies)] if energies else [0.0, 0.0],
            'session_duration': (end_time - start_time).total_seconds() / 60,  # minutes
            'timestamp': datetime.now().isoformat()
        }

    async def analyze_trends(self, hours: int, metric: str) -> dict[str, Any]:
        """Analyze performance trends over time."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filter track history
        recent_tracks = [
            track for track in self.track_history
            if track.start_time >= cutoff_time
        ]

        if not recent_tracks:
            return {
                'trend': 'insufficient_data',
                'data_points': 0,
                'analysis': 'Not enough data for trend analysis',
                'timestamp': datetime.now().isoformat()
            }

        # Analyze trend based on metric
        if metric == 'bpm':
            values = [track.bpm for track in recent_tracks]
            trend = 'increasing' if values[-1] > values[0] else 'decreasing'
        elif metric == 'energy':
            values = [track.energy for track in recent_tracks]
            trend = 'increasing' if values[-1] > values[0] else 'decreasing'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'data_points': len(recent_tracks),
            'start_value': values[0],
            'end_value': values[-1],
            'change': values[-1] - values[0],
            'analysis': f"{metric} is trending {trend} over the last {hours} hours",
            'timestamp': datetime.now().isoformat()
        }

    async def export_data(self, format: str, filename: str) -> dict[str, Any]:
        """Export performance data in specified format."""
        data = {
            'timestamp': datetime.now().isoformat(),
            'current_metrics': await self.get_current_metrics(),
            'track_history': [
                {
                    'title': t.title,
                    'artist': t.artist,
                    'bpm': t.bpm,
                    'key': t.key,
                    'energy': t.energy,
                    'start_time': t.start_time.isoformat(),
                    'duration': (t.end_time - t.start_time).total_seconds() if t.end_time else 0
                }
                for t in self.track_history
            ],
            'recommendations': await self.get_recommendations()
        }

        if format.lower() == 'json':
            import json
            try:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                return {
                    'status': 'success',
                    'format': 'json',
                    'filename': filename,
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }

        return {
            'status': 'error',
            'error': f'Unsupported format: {format}',
            'timestamp': datetime.now().isoformat()
        }
