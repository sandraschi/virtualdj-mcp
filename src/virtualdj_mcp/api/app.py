"""
FastAPI application for VirtualDJ-MCP

Provides REST API endpoints alongside MCP interface.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..config import VDJConfig
from ..core.vdj_client import VDJError, VirtualDJClient
from ..services.audio_analysis import AudioAnalyzer
from ..services.library_scanner import LibraryScanner


# Pydantic models for API requests/responses
class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: str
    version: str = "1.0.0"
    service: str = "VirtualDJ-MCP"


class DeckStatusResponse(BaseModel):
    deck_id: int
    is_playing: bool
    track_path: Optional[str] = None
    track_title: Optional[str] = None
    track_artist: Optional[str] = None
    position: float
    duration: float
    bpm: Optional[float] = None
    key: Optional[str] = None
    volume: int
    pitch: float


class TrackSearchRequest(BaseModel):
    query: str = ""
    limit: int = 50
    artist: Optional[str] = None
    genre: Optional[str] = None
    bpm_min: Optional[float] = None
    bpm_max: Optional[float] = None
    key: Optional[str] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    duration_min: Optional[float] = None
    duration_max: Optional[float] = None
    energy_min: Optional[float] = None
    energy_max: Optional[float] = None
    sort_by: str = "relevance"
    sort_desc: bool = True


class AudioAnalysisResponse(BaseModel):
    bpm: Optional[float] = None
    key: Optional[str] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None
    loudness: Optional[float] = None
    spectral_centroid: Optional[float] = None
    zero_crossing_rate: Optional[float] = None
    onset_strength: Optional[float] = None
    beats: List[float] = []
    analysis_successful: bool


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title="VirtualDJ-MCP API",
        description="REST API for VirtualDJ automation and control",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global services
    config = VDJConfig.from_env()
    vdj_client = None
    library_scanner = LibraryScanner()
    audio_analyzer = AudioAnalyzer()

    async def get_vdj_client():
        """Get initialized VirtualDJ client"""
        nonlocal vdj_client
        if vdj_client is None:
            if not config.validate_paths():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="VirtualDJ path validation failed"
                )

            vdj_client = VirtualDJClient(config)

            # Start VirtualDJ if needed
            async with vdj_client:
                if not await vdj_client.start_virtualdj():
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to start VirtualDJ"
                    )

        return vdj_client

    # Health endpoint
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        return HealthResponse(
            timestamp=datetime.utcnow().isoformat(),
            version="1.0.0",
            service="VirtualDJ-MCP"
        )

    # API v1 endpoints
    @app.get("/api/v1/deck/{deck_id}/status", response_model=DeckStatusResponse)
    async def get_deck_status_api(deck_id: int):
        """
        Get current status of a specific deck

        Args:
            deck_id: Deck number (1-8)

        Returns:
            Current deck status and track information
        """
        try:
            client = await get_vdj_client()

            async with client:
                # Get deck variables (VirtualDJ variable names)
                commands = [
                    f"get_var 'deck{deck_id}_play'",
                    f"get_var 'deck{deck_id}_title'",
                    f"get_var 'deck{deck_id}_artist'",
                    f"get_var 'deck{deck_id}_position'",
                    f"get_var 'deck{deck_id}_duration'",
                    f"get_var 'deck{deck_id}_bpm'",
                    f"get_var 'deck{deck_id}_key'",
                    f"get_var 'deck{deck_id}_volume'",
                    f"get_var 'deck{deck_id}_pitch'"
                ]

                results = {}
                for cmd in commands:
                    result = await client.send_command(cmd)
                    if result["status"] == "success":
                        var_name = cmd.split("'")[1]
                        results[var_name] = result["result"]

                # Parse results into DeckStatusResponse
                return DeckStatusResponse(
                    deck_id=deck_id,
                    is_playing=results.get(f'deck{deck_id}_play', '0') == '1',
                    track_title=results.get(f'deck{deck_id}_title', 'No Track'),
                    track_artist=results.get(f'deck{deck_id}_artist', 'Unknown Artist'),
                    position=float(results.get(f'deck{deck_id}_position', 0)),
                    duration=float(results.get(f'deck{deck_id}_duration', 0)),
                    bpm=float(results.get(f'deck{deck_id}_bpm', 0)) if results.get(f'deck{deck_id}_bpm') else None,
                    key=results.get(f'deck{deck_id}_key'),
                    volume=int(results.get(f'deck{deck_id}_volume', 100)),
                    pitch=float(results.get(f'deck{deck_id}_pitch', 0))
                )

        except VDJError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}"
            )

    @app.post("/api/v1/deck/{deck_id}/play_pause")
    async def play_pause_deck_api(deck_id: int, action: str = "toggle"):
        """
        Control playback on a specific deck

        Args:
            deck_id: Deck number (1-8)
            action: Action to perform (play, pause, toggle)

        Returns:
            Success status
        """
        try:
            client = await get_vdj_client()

            if action == "play":
                cmd = f"deck {deck_id} play"
            elif action == "pause":
                cmd = f"deck {deck_id} pause"
            else:  # toggle
                cmd = f"deck {deck_id} play_pause"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] != "success":
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to {action} deck {deck_id}"
                    )

                return {"status": "success", "message": f"Deck {deck_id} {action}ed"}

        except VDJError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post("/api/v1/deck/{deck_id}/load")
    async def load_track_api(deck_id: int, track_path: str):
        """
        Load a track to a specific deck

        Args:
            deck_id: Deck number (1-8)
            track_path: Path to audio file

        Returns:
            Success status
        """
        from pathlib import Path
        try:
            if not Path(track_path).exists():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Track file not found: {track_path}"
                )

            client = await get_vdj_client()

            cmd = f"deck {deck_id} load '{track_path}'"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] != "success":
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to load track to deck {deck_id}"
                    )

                return {"status": "success", "message": f"Track loaded to deck {deck_id}"}

        except VDJError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post("/api/v1/library/search")
    async def search_tracks_api(request: TrackSearchRequest):
        """
        Search the music library with advanced filtering

        Returns:
            List of matching tracks
        """
        try:
            # Validate inputs
            limit = max(1, min(1000, request.limit))

            # Scan library (in production, you'd use a cached database)
            tracks = await library_scanner.scan_directory(recursive=True)

            # Convert to dict format for JSON serialization
            track_infos = []
            for track in tracks:
                track_infos.append({
                    "path": track.file_path,
                    "title": track.title or Path(track.file_path).stem,
                    "artist": track.artist or "Unknown Artist",
                    "album": track.album,
                    "genre": track.genre,
                    "bpm": track.bpm,
                    "key": track.key,
                    "duration": track.duration,
                    "year": track.year,
                    "bitrate": track.bitrate,
                    "sample_rate": track.sample_rate,
                    "channels": track.channels,
                    "file_size": track.file_size,
                    "last_modified": track.last_modified,
                    "play_count": track.play_count,
                    "rating": track.rating,
                    "tags": track.tags
                })

            # Apply filters
            filtered_tracks = []
            for track in track_infos:
                # Skip if any filter doesn't match
                if request.query and request.query.lower() not in (track["title"] + " " + track["artist"]).lower():
                    continue
                if request.artist and request.artist.lower() not in (track["artist"] or "").lower():
                    continue
                if request.genre and request.genre.lower() not in (track["genre"] or "").lower():
                    continue
                if request.bpm_min is not None and (track["bpm"] is None or track["bpm"] < request.bpm_min):
                    continue
                if request.bpm_max is not None and (track["bpm"] is None or track["bpm"] > request.bpm_max):
                    continue
                if request.key and track["key"] and request.key.upper() != track["key"].upper():
                    continue
                if request.year_min is not None and (track["year"] is None or track["year"] < request.year_min):
                    continue
                if request.year_max is not None and (track["year"] is None or track["year"] > request.year_max):
                    continue
                if request.duration_min is not None and track["duration"] < request.duration_min:
                    continue
                if request.duration_max is not None and track["duration"] > request.duration_max:
                    continue
                if request.energy_min is not None and (track.get("energy") is None or track["energy"] < request.energy_min):
                    continue
                if request.energy_max is not None and (track.get("energy") is None or track["energy"] > request.energy_max):
                    continue

                filtered_tracks.append(track)

            # Sort results
            if request.sort_by == "relevance" and request.query:
                def relevance_score(track: Dict[str, Any]) -> int:
                    score = 0
                    if request.query.lower() in (track.get("title") or "").lower():
                        score += 3
                    if request.query.lower() in (track.get("artist") or "").lower():
                        score += 2
                    if request.query.lower() in (track.get("album") or "").lower():
                        score += 1
                    return score

                filtered_tracks.sort(key=relevance_score, reverse=not request.sort_desc)
            elif request.sort_by == "title":
                filtered_tracks.sort(key=lambda x: (x.get("title") or "").lower(), reverse=request.sort_desc)
            elif request.sort_by == "artist":
                filtered_tracks.sort(key=lambda x: (x.get("artist") or "").lower(), reverse=request.sort_desc)
            elif request.sort_by == "bpm":
                filtered_tracks.sort(key=lambda x: x.get("bpm") or 0, reverse=request.sort_desc)
            elif request.sort_by == "year":
                filtered_tracks.sort(key=lambda x: x.get("year") or 0, reverse=request.sort_desc)
            elif request.sort_by == "duration":
                filtered_tracks.sort(key=lambda x: x.get("duration") or 0, reverse=request.sort_desc)
            elif request.sort_by == "energy":
                filtered_tracks.sort(key=lambda x: x.get("energy") or 0, reverse=request.sort_desc)

            # Apply limit
            result_tracks = filtered_tracks[:limit]

            return {"status": "success", "tracks": result_tracks, "total": len(result_tracks)}

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Search failed: {str(e)}"
            )

    @app.post("/api/v1/audio/analyze")
    async def analyze_audio_api(track_path: str):
        """
        Analyze an audio file to extract BPM, key, and other features

        Args:
            track_path: Path to the audio file to analyze

        Returns:
            Audio analysis results
        """
        try:
            features = await audio_analyzer.analyze_file(track_path)

            # Convert to a serializable format
            result = AudioAnalysisResponse(
                bpm=features.bpm,
                key=str(features.key) if features.key else None,
                energy=features.energy,
                danceability=features.danceability,
                loudness=features.loudness,
                spectral_centroid=features.spectral_centroid,
                zero_crossing_rate=features.zero_crossing_rate,
                onset_strength=features.onset_strength,
                beats=features.beats[:100],  # Limit number of beats to return
                analysis_successful=True
            )

            return result

        except Exception:
            return AudioAnalysisResponse(
                analysis_successful=False
            )

    return app


