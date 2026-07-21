"""
VDJ Library Portmanteau Tool

Consolidates library operations into a single interface.
Operations: search, analyze
"""

from typing import Any, Literal

from fastmcp import FastMCP
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import Card, CardContent, CardHeader, CardTitle, Text
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

console = Console(file=__import__('sys').stderr)

# Global scanner and analyzer instances
_library_scanner = None
_audio_analyzer = None


async def get_library_scanner():
    """Get initialized library scanner"""
    global _library_scanner
    if _library_scanner is None:
        from ...services.library_scanner import LibraryScanner
        _library_scanner = LibraryScanner()
    return _library_scanner


async def get_audio_analyzer():
    """Get initialized audio analyzer"""
    global _audio_analyzer
    if _audio_analyzer is None:
        from ...services.audio_analysis import AudioAnalyzer
        _audio_analyzer = AudioAnalyzer()
    return _audio_analyzer


def setup_library_portmanteau(mcp: FastMCP):
    """Register vdj_library portmanteau tool."""

    @mcp.tool()
    async def vdj_library(
        operation: Literal["search", "analyze"],
        query: str = "",
        track_path: str | None = None,
        limit: int = 50,
        artist: str | None = None,
        genre: str | None = None,
        bpm_min: float | None = None,
        bpm_max: float | None = None,
        key: str | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
        duration_min: float | None = None,
        duration_max: float | None = None,
        energy_min: float | None = None,
        energy_max: float | None = None,
        sort_by: str = "relevance",
        sort_desc: bool = True
    ) -> Any:
        """
        VirtualDJ library management and audio analysis.

        PORTMANTEAU PATTERN: Consolidates library tools into 1 unified interface.

        SUPPORTED OPERATIONS:
        - search: Search music library with advanced filtering
        - analyze: Analyze audio file for BPM, key, energy

        Args:
            operation: The library operation to perform
            query: Search query text
            track_path: Path to audio file (required for analyze)
            limit: Maximum results (1-1000, default: 50)
            artist: Filter by artist name
            genre: Filter by genre
            bpm_min/bpm_max: BPM range filter
            key: Filter by musical key (e.g., 'C', 'Am')
            year_min/year_max: Year range filter
            duration_min/duration_max: Duration range in seconds
            energy_min/energy_max: Energy level range (0.0-1.0)
            sort_by: Sort field (relevance, title, artist, bpm, year, duration, energy)
            sort_desc: Sort descending (default: True)

        Returns:
            Dict with search results or analysis data

        Examples:
            vdj_library("search", query="ABBA")
            vdj_library("search", query="rock", bpm_min=120, bpm_max=140)
            vdj_library("search", artist="Pink Floyd", sort_by="year")
            vdj_library("analyze", track_path="C:/Music/track.mp3")
        """
        try:
            if operation == "search":
                from ..library.models import TrackInfo

                limit = max(1, min(1000, limit))
                scanner = await get_library_scanner()

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    TimeElapsedColumn(),
                    transient=True,
                    console=console
                ) as progress:
                    task = progress.add_task("Searching library...", total=None)

                    try:
                        tracks = await scanner.scan_directory(recursive=True)
                        track_infos = [TrackInfo.from_scanner_track(track) for track in tracks]

                        # Apply filters
                        filtered_tracks = []
                        for track in track_infos:
                            if query and query.lower() not in (track.title + " " + track.artist).lower():
                                continue
                            if artist and artist.lower() not in (track.artist or "").lower():
                                continue
                            if genre and genre.lower() not in (track.genre or "").lower():
                                continue
                            if bpm_min is not None and (track.bpm is None or track.bpm < bpm_min):
                                continue
                            if bpm_max is not None and (track.bpm is None or track.bpm > bpm_max):
                                continue
                            if key and track.key and key.upper() != track.key.upper():
                                continue
                            if year_min is not None and (track.year is None or track.year < year_min):
                                continue
                            if year_max is not None and (track.year is None or track.year > year_max):
                                continue
                            if duration_min is not None and track.duration < duration_min:
                                continue
                            if duration_max is not None and track.duration > duration_max:
                                continue
                            if energy_min is not None and (track.energy is None or track.energy < energy_min):
                                continue
                            if energy_max is not None and (track.energy is None or track.energy > energy_max):
                                continue

                            filtered_tracks.append(track)

                        # Sort results
                        if sort_by == "relevance" and query:
                            def relevance_score(track):
                                score = 0
                                if query.lower() in (track.title or "").lower():
                                    score += 3
                                if query.lower() in (track.artist or "").lower():
                                    score += 2
                                if query.lower() in (track.album or "").lower():
                                    score += 1
                                return score
                            filtered_tracks.sort(key=relevance_score, reverse=not sort_desc)
                        elif sort_by == "title":
                            filtered_tracks.sort(key=lambda x: (x.title or "").lower(), reverse=sort_desc)
                        elif sort_by == "artist":
                            filtered_tracks.sort(key=lambda x: (x.artist or "").lower(), reverse=sort_desc)
                        elif sort_by == "bpm":
                            filtered_tracks.sort(key=lambda x: x.bpm or 0, reverse=sort_desc)
                        elif sort_by == "year":
                            filtered_tracks.sort(key=lambda x: x.year or 0, reverse=sort_desc)
                        elif sort_by == "duration":
                            filtered_tracks.sort(key=lambda x: x.duration or 0, reverse=sort_desc)
                        elif sort_by == "energy":
                            filtered_tracks.sort(key=lambda x: x.energy or 0, reverse=sort_desc)

                        result_tracks = filtered_tracks[:limit]

                        with Card(css_class="max-w-lg border border-neutral-700 bg-neutral-900 rounded-lg shadow-lg p-4") as view:
                            with CardHeader():
                                CardTitle(f"🔍 Search Results for: {query or 'All'}", css_class="text-lg font-bold text-white")
                            with CardContent(css_class="mt-2 space-y-2"):
                                Text(f"Found {len(filtered_tracks)} tracks, showing top {len(result_tracks)}:")
                                for i, track in enumerate(result_tracks):
                                    t_title = track.title or "Unknown Title"
                                    t_artist = track.artist or "Unknown Artist"
                                    t_bpm = f"{track.bpm:.1f} BPM" if track.bpm else "N/A BPM"
                                    t_key = track.key or "N/A"
                                    Text(f"{i+1}. {t_title} - {t_artist} [{t_bpm} | {t_key}]", css_class="text-sm text-neutral-200")
                                if not result_tracks:
                                    Text("No matching tracks found in library.", css_class="text-sm text-neutral-400 italic")

                        text_summary = f"Library search completed. Found {len(filtered_tracks)} tracks (showing {len(result_tracks)})."

                        return ToolResult(
                            content=text_summary,
                            structured_content=PrefabApp(view=view, title="Library Search")
                        )

                    except Exception as e:
                        console.print(f"[red]Error during search: {e!s}[/red]")
                        return {"success": False, "error": str(e)}
                    finally:
                        progress.update(task, completed=1, visible=False)

            elif operation == "analyze":
                if not track_path:
                    return {"success": False, "error": "track_path required for analyze operation"}

                try:
                    analyzer = await get_audio_analyzer()
                    features = await analyzer.analyze_file(track_path)

                    return {
                        "success": True,
                        "operation": "analyze",
                        "track_path": track_path,
                        "bpm": features.bpm,
                        "key": str(features.key) if features.key else None,
                        "energy": features.energy,
                        "danceability": features.danceability,
                        "loudness": features.loudness,
                        "spectral_centroid": features.spectral_centroid,
                        "zero_crossing_rate": features.zero_crossing_rate,
                        "onset_strength": features.onset_strength,
                        "beats": features.beats[:100] if features.beats else []
                    }

                except Exception as e:
                    console.print(f"[red]Error analyzing audio: {e!s}[/red]")
                    return {"success": False, "error": str(e)}

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_library: {e}[/red]")
            return {"success": False, "error": str(e)}

