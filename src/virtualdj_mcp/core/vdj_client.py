"""
VirtualDJ Client - HTTP API wrapper for Network Control Plugin

Uses VirtualDJ's Network Control Plugin HTTP API instead of CLI.
Requires VirtualDJ 2023+ with Pro license and Network Control Plugin installed.
"""

from pathlib import Path
from typing import Any

import httpx
import psutil


class VDJError(Exception):
    """VirtualDJ operation error"""

    pass


class VirtualDJClient:
    """VirtualDJ HTTP API client using Network Control Plugin"""

    def __init__(self, config):
        self.config = config
        self.base_url = f"http://{config.http_host}:{config.http_port}"
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(timeout=self.config.http_timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_headers(self) -> dict[str, str]:
        """Get request headers including auth if configured"""
        headers = {"Content-Type": "text/plain"}
        if self.config.http_password:
            headers["Authorization"] = f"Bearer {self.config.http_password}"
        return headers

    async def is_running(self) -> bool:
        """Check if VirtualDJ is running and Network Control Plugin is responding"""
        try:
            # First check process
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] and "virtualdj" in proc.info["name"].lower():
                    # Process running, check HTTP API
                    try:
                        async with httpx.AsyncClient(timeout=2.0) as client:
                            response = await client.get(
                                f"{self.base_url}/execute?script=nop", headers=self._get_headers()
                            )
                            return response.status_code == 200
                    except Exception:
                        return True  # Process running but plugin not responding
            return False
        except Exception:
            return False

    async def send_command(self, command: str) -> dict[str, Any]:
        """Send VDJScript command via HTTP API"""
        return await self._send_http_command(command, is_query=False)

    async def query(self, script: str) -> dict[str, Any]:
        """Query VirtualDJ for information via HTTP API"""
        return await self._send_http_command(script, is_query=True)

    async def _send_http_command(self, script: str, is_query: bool = False) -> dict[str, Any]:
        """Send command via HTTP Network Control Plugin API"""
        endpoint = "query" if is_query else "execute"

        try:
            client = self._client or httpx.AsyncClient(timeout=self.config.http_timeout)
            close_after = self._client is None

            try:
                # Use POST for complex scripts (handles special chars better)
                response = await client.post(f"{self.base_url}/{endpoint}", content=script, headers=self._get_headers())

                if response.status_code == 200:
                    result = response.text.strip()
                    # For execute, result is 'true' or 'false'
                    # For query, result is the actual value
                    if is_query:
                        return {"status": "success", "result": result}
                    else:
                        success = result.lower() == "true"
                        return {"status": "success" if success else "error", "result": result}
                elif response.status_code == 401:
                    return {"status": "error", "error": "Authentication failed - check password"}
                else:
                    return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}

            finally:
                if close_after:
                    await client.aclose()

        except httpx.ConnectError:
            return {"status": "error", "error": "Cannot connect to VirtualDJ Network Control Plugin. Is it enabled?"}
        except httpx.TimeoutException:
            return {"status": "error", "error": "Command timeout"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def execute(self, script: str) -> bool:
        """Execute VDJScript and return success status"""
        result = await self.send_command(script)
        return result.get("status") == "success" and result.get("result", "").lower() == "true"

    async def get_status(self) -> dict[str, Any]:
        """Get VirtualDJ status"""
        try:
            if not await self.is_running():
                return {"status": "not_running", "details": "VirtualDJ is not running"}

            # Try to get deck info
            result = await self.query("deck 1 get_title")
            if result["status"] == "success":
                return {
                    "status": "running",
                    "details": "VirtualDJ Network Control Plugin responding",
                    "current_track": result.get("result", "Unknown"),
                }
            else:
                return {"status": "running", "details": "VirtualDJ process found but plugin not responding"}
        except Exception as e:
            raise VDJError(f"Failed to get status: {e}") from e

    async def get_variable(self, variable: str) -> Any:
        """Get a VirtualDJ variable value"""
        result = await self.query(f"get_var '{variable}'")
        if result["status"] == "success":
            return result.get("result", "")
        else:
            raise VDJError(f"Failed to get variable {variable}: {result.get('error', 'Unknown error')}")

    async def execute_vdjscript(self, script: str) -> dict[str, Any]:
        """Execute a VDJScript expression directly"""
        return await self.send_command(script)

    async def load_track(self, deck_id: int, track_path: str) -> bool:
        """Load a track to a deck"""
        # Normalize path to forward slashes for VDJScript
        normalized_path = str(Path(track_path)).replace("\\", "/")
        script = f"deck {deck_id} load '{normalized_path}'"
        return await self.execute(script)

    async def play(self, deck_id: int) -> bool:
        """Start playback on a deck"""
        return await self.execute(f"deck {deck_id} play")

    async def pause(self, deck_id: int) -> bool:
        """Pause playback on a deck"""
        return await self.execute(f"deck {deck_id} pause")

    async def stop(self, deck_id: int) -> bool:
        """Stop playback on a deck"""
        return await self.execute(f"deck {deck_id} stop")

    async def get_deck_info(self, deck_id: int) -> dict[str, Any]:
        """Get comprehensive deck information"""
        info = {}
        queries = {
            "title": f"deck {deck_id} get_title",
            "artist": f"deck {deck_id} get_artist",
            "bpm": f"deck {deck_id} get_bpm",
            "key": f"deck {deck_id} get_key",
            "position": f"deck {deck_id} get_position",
            "duration": f"deck {deck_id} get_songlength",
            "is_playing": f"deck {deck_id} get_isplaying",
        }

        for key, script in queries.items():
            result = await self.query(script)
            if result["status"] == "success":
                info[key] = result["result"]
            else:
                info[key] = None

        return info

    async def stop_virtualdj(self):
        """Stop VirtualDJ application"""
        try:
            await self.send_command("quit")
        except Exception as e:
            raise VDJError(f"Failed to stop VirtualDJ: {e}") from e
