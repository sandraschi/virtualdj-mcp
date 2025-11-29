"""
VDJ Plex Portmanteau Tool - NEW!

Integrates Plex Media Server with VirtualDJ for seamless music library access.
Operations: search, get_path, load_from_plex
"""

import os
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from ..shared.exceptions import VDJError

console = Console(file=__import__('sys').stderr)

# Environment config for Plex
PLEX_SERVER_URL = os.getenv("PLEX_SERVER_URL", "http://localhost:32400")
PLEX_TOKEN = os.getenv("PLEX_TOKEN", "")


def setup_plex_portmanteau(mcp: FastMCP):
    """Register vdj_plex portmanteau tool."""

    @mcp.tool()
    async def vdj_plex(
        operation: Literal["search", "get_path", "load_from_plex", "list_libraries"],
        query: Optional[str] = None,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        library_id: Optional[str] = None,
        media_id: Optional[str] = None,
        deck_id: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Plex Media Server integration for VirtualDJ.

        Enables seamless access to your Plex music libraries from VirtualDJ.
        Search Plex, get file paths, and load tracks directly to decks.

        PORTMANTEAU PATTERN: Provides unified Plex integration interface.

        SUPPORTED OPERATIONS:
        - search: Search Plex music library
        - get_path: Get file path for a Plex media item
        - load_from_plex: Search and load track directly to VDJ deck
        - list_libraries: List available Plex music libraries

        PREREQUISITES:
        - PlexMCP must be running and configured
        - Environment variables: PLEX_SERVER_URL, PLEX_TOKEN

        Args:
            operation: The Plex operation to perform
            query: Search query text
            artist: Filter by artist name
            album: Filter by album name
            library_id: Plex library ID to search within
            media_id: Plex media item ID (for get_path)
            deck_id: VirtualDJ deck to load to (1-8, default: 1)
            limit: Maximum search results (default: 10)

        Returns:
            Dict with operation result and data

        Examples:
            # Search for ABBA tracks
            vdj_plex("search", query="ABBA", limit=10)
            
            # Search specific artist
            vdj_plex("search", artist="Pink Floyd")
            
            # Get file path for a track
            vdj_plex("get_path", media_id="12345")
            
            # Search and load directly to deck
            vdj_plex("load_from_plex", query="Dancing Queen", deck_id=1)
            
            # List music libraries
            vdj_plex("list_libraries")
        """
        try:
            # Check Plex configuration
            if not PLEX_TOKEN:
                return {
                    "success": False,
                    "error": "PLEX_TOKEN not configured. Set environment variable.",
                    "hint": "Add PLEX_TOKEN to your environment or .env file"
                }

            if operation == "list_libraries":
                try:
                    import httpx
                    
                    headers = {
                        "X-Plex-Token": PLEX_TOKEN,
                        "Accept": "application/json"
                    }
                    
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.get(
                            f"{PLEX_SERVER_URL}/library/sections",
                            headers=headers,
                            timeout=30.0
                        )
                        
                        if response.status_code != 200:
                            return {"success": False, "error": f"Plex API error: {response.status_code}"}
                        
                        data = response.json()
                        directories = data.get("MediaContainer", {}).get("Directory", [])
                        
                        # Filter to music libraries
                        music_libraries = [
                            {
                                "id": lib.get("key"),
                                "title": lib.get("title"),
                                "type": lib.get("type"),
                                "count": lib.get("count", 0)
                            }
                            for lib in directories
                            if lib.get("type") in ("artist", "track")
                        ]
                        
                        return {
                            "success": True,
                            "operation": "list_libraries",
                            "libraries": music_libraries,
                            "total": len(music_libraries)
                        }
                        
                except ImportError:
                    return {"success": False, "error": "httpx not installed. Run: pip install httpx"}
                except Exception as e:
                    return {"success": False, "error": f"Failed to connect to Plex: {e}"}

            elif operation == "search":
                if not query and not artist and not album:
                    return {"success": False, "error": "query, artist, or album required for search"}
                
                try:
                    import httpx
                    
                    headers = {
                        "X-Plex-Token": PLEX_TOKEN,
                        "Accept": "application/json"
                    }
                    
                    # Build search query
                    search_term = query or artist or album
                    params = {"query": search_term, "limit": limit}
                    
                    if library_id:
                        url = f"{PLEX_SERVER_URL}/library/sections/{library_id}/search"
                    else:
                        url = f"{PLEX_SERVER_URL}/search"
                    
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.get(
                            url,
                            headers=headers,
                            params=params,
                            timeout=30.0
                        )
                        
                        if response.status_code != 200:
                            return {"success": False, "error": f"Plex API error: {response.status_code}"}
                        
                        data = response.json()
                        results = data.get("MediaContainer", {}).get("Metadata", [])
                        
                        # Filter to audio tracks and extract relevant info
                        tracks = []
                        for item in results:
                            if item.get("type") in ("track", "album", "artist"):
                                track_info = {
                                    "id": item.get("ratingKey"),
                                    "title": item.get("title"),
                                    "artist": item.get("grandparentTitle") or item.get("parentTitle"),
                                    "album": item.get("parentTitle"),
                                    "type": item.get("type"),
                                    "duration": item.get("duration"),
                                    "year": item.get("year"),
                                }
                                
                                # Try to get file path from Media/Part
                                media = item.get("Media", [])
                                if media:
                                    parts = media[0].get("Part", [])
                                    if parts:
                                        track_info["file_path"] = parts[0].get("file")
                                
                                tracks.append(track_info)
                        
                        console.print(f"[green]Found {len(tracks)} tracks in Plex[/green]")
                        return {
                            "success": True,
                            "operation": "search",
                            "query": search_term,
                            "tracks": tracks[:limit],
                            "total": len(tracks)
                        }
                        
                except ImportError:
                    return {"success": False, "error": "httpx not installed. Run: pip install httpx"}
                except Exception as e:
                    return {"success": False, "error": f"Search failed: {e}"}

            elif operation == "get_path":
                if not media_id:
                    return {"success": False, "error": "media_id required for get_path operation"}
                
                try:
                    import httpx
                    
                    headers = {
                        "X-Plex-Token": PLEX_TOKEN,
                        "Accept": "application/json"
                    }
                    
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.get(
                            f"{PLEX_SERVER_URL}/library/metadata/{media_id}",
                            headers=headers,
                            timeout=30.0
                        )
                        
                        if response.status_code != 200:
                            return {"success": False, "error": f"Plex API error: {response.status_code}"}
                        
                        data = response.json()
                        metadata = data.get("MediaContainer", {}).get("Metadata", [])
                        
                        if not metadata:
                            return {"success": False, "error": f"Media not found: {media_id}"}
                        
                        item = metadata[0]
                        media = item.get("Media", [])
                        
                        if not media:
                            return {"success": False, "error": "No media file found for this item"}
                        
                        parts = media[0].get("Part", [])
                        if not parts:
                            return {"success": False, "error": "No file parts found"}
                        
                        file_path = parts[0].get("file")
                        
                        return {
                            "success": True,
                            "operation": "get_path",
                            "media_id": media_id,
                            "title": item.get("title"),
                            "artist": item.get("grandparentTitle") or item.get("parentTitle"),
                            "file_path": file_path,
                            "exists": Path(file_path).exists() if file_path else False
                        }
                        
                except ImportError:
                    return {"success": False, "error": "httpx not installed. Run: pip install httpx"}
                except Exception as e:
                    return {"success": False, "error": f"Failed to get path: {e}"}

            elif operation == "load_from_plex":
                if not query and not artist:
                    return {"success": False, "error": "query or artist required for load_from_plex"}
                
                # First search
                search_result = await vdj_plex(
                    operation="search",
                    query=query,
                    artist=artist,
                    album=album,
                    library_id=library_id,
                    limit=1
                )
                
                if not search_result.get("success"):
                    return search_result
                
                tracks = search_result.get("tracks", [])
                if not tracks:
                    return {"success": False, "error": f"No tracks found for: {query or artist}"}
                
                track = tracks[0]
                file_path = track.get("file_path")
                
                if not file_path:
                    # Try to get path via media_id
                    path_result = await vdj_plex(
                        operation="get_path",
                        media_id=track.get("id")
                    )
                    if path_result.get("success"):
                        file_path = path_result.get("file_path")
                
                if not file_path:
                    return {"success": False, "error": "Could not determine file path for track"}
                
                if not Path(file_path).exists():
                    return {
                        "success": False,
                        "error": f"File not accessible: {file_path}",
                        "hint": "Plex server may be on different machine. Ensure path is accessible."
                    }
                
                # Load to VirtualDJ
                vdj_client = await get_vdj_client()
                normalized_path = file_path.replace("\\", "/")
                
                async with vdj_client:
                    # Stop deck if playing
                    status_result = await vdj_client.query(f"deck {deck_id} get_isplaying")
                    if status_result.get("result") in ("1", "true", "True"):
                        await vdj_client.send_command(f"deck {deck_id} stop")
                        import asyncio
                        await asyncio.sleep(0.2)
                    
                    result = await vdj_client.send_command(f"deck {deck_id} load '{normalized_path}'")
                    
                    if result["status"] != "success":
                        raise VDJError(f"Failed to load track: {result.get('error')}")
                    
                    console.print(f"[green]Loaded '{track.get('title')}' by {track.get('artist')} to deck {deck_id}[/green]")
                    
                    return {
                        "success": True,
                        "operation": "load_from_plex",
                        "deck_id": deck_id,
                        "track": {
                            "title": track.get("title"),
                            "artist": track.get("artist"),
                            "album": track.get("album"),
                            "file_path": file_path
                        }
                    }

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_plex: {e}[/red]")
            return {"success": False, "error": str(e)}

