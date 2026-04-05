"""
Library tools for VirtualDJ MCP
"""

from typing import Any

from fastmcp import FastMCP
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .models import TrackInfo

# Initialize console for logging
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


def setup_library_tools(mcp: FastMCP):
    """
    Set up library related MCP tools.

    Args:
        mcp: MCP instance to register tools with
    """

    @mcp.tool()
    async def search_tracks(
        query: str = "",
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
    ) -> list[dict[str, Any]]:
        """
        Search the music library with advanced filtering and sorting.

        Args:
            query: Text search query (searches in title, artist, album, and tags)
            limit: Maximum number of results to return (1-1000)
            artist: Filter by artist name (partial match, case-insensitive)
            genre: Filter by genre (partial match, case-insensitive)
            bpm_min: Minimum BPM (beats per minute)
            bpm_max: Maximum BPM (beats per minute)
            key: Filter by musical key (e.g., 'C', 'A#m')
            year_min: Minimum release year
            year_max: Maximum release year
            duration_min: Minimum duration in seconds
            duration_max: Maximum duration in seconds
            energy_min: Minimum energy level (0.0-1.0)
            energy_max: Maximum energy level (0.0-1.0)
            sort_by: Field to sort by (relevance, title, artist, bpm, year, duration, energy)
            sort_desc: Sort in descending order (True) or ascending (False)

        Returns:
            List of matching tracks with metadata
        """
        # Validate inputs
        limit = max(1, min(1000, limit))  # Clamp limit to 1-1000

        # Get scanner instance
        scanner = await get_library_scanner()

        # Scan library if needed (in a real app, you'd have a pre-scanned database)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            transient=True,
            console=console
        ) as progress:
            task = progress.add_task("Searching library...", total=None)

            try:
                # In a real implementation, you'd query a database here
                # For now, we'll scan the directory on each search (not recommended for production)
                tracks = await scanner.scan_directory(recursive=True)

                # Convert to TrackInfo objects
                track_infos = [TrackInfo.from_scanner_track(track) for track in tracks]

                # Apply filters
                filtered_tracks = []
                for track in track_infos:
                    # Skip if any filter doesn't match
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
                    # Simple relevance sort based on query matches
                    def relevance_score(track: TrackInfo) -> int:
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

                # Apply limit
                result_tracks = filtered_tracks[:limit]

                # Convert to dictionaries for JSON serialization
                return [track.to_dict() for track in result_tracks]

            except Exception as e:
                console.print(f"[red]Error during search: {str(e)}[/red]")
                return []
            finally:
                progress.update(task, completed=1, visible=False)


    @mcp.tool()
    async def analyze_track_audio(track_path: str) -> dict[str, Any]:
        """
        Analyze an audio file to extract BPM, key, and other audio features.

        Args:
            track_path: Path to the audio file to analyze

        Returns:
            Dictionary containing audio analysis results
        """
        try:
            analyzer = await get_audio_analyzer()
            features = await analyzer.analyze_file(track_path)

            # Convert to a serializable format
            result = {
                "bpm": features.bpm,
                "key": str(features.key) if features.key else None,
                "energy": features.energy,
                "danceability": features.danceability,
                "loudness": features.loudness,
                "spectral_centroid": features.spectral_centroid,
                "zero_crossing_rate": features.zero_crossing_rate,
                "onset_strength": features.onset_strength,
                "beats": features.beats[:100],  # Limit number of beats to return
                "analysis_successful": True
            }

            return result

        except Exception as e:
            console.print(f"[red]Error analyzing audio: {str(e)}[/red]")
            return {
                "analysis_successful": False,
                "error": str(e)
            }
