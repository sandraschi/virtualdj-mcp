"""Run connectivity checks for the VirtualDJ-MCP dashboard (HTTP plugin + OSC port)."""

from __future__ import annotations

import asyncio
import socket

import httpx

from ..config import VDJConfig
from ..core.vdj_client import VirtualDJClient


def _udp_send_probe(host: str, port: int) -> tuple[bool, str]:
    """Try sending a minimal UDP datagram. Does not prove VirtualDJ received it."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(2.0)
            sock.sendto(b"\x00", (host, port))
        return (
            True,
            "UDP send succeeded. VirtualDJ must listen on this port for OSC; delivery is not confirmed over UDP.",
        )
    except OSError as e:
        return False, str(e)


async def run_connection_tests(config: VDJConfig) -> dict:
    """Return structured results for the webapp (HTTP Network Control + OSC UDP)."""
    base = f"http://{config.http_host}:{config.http_port}"
    vdj = VirtualDJClient(config)
    headers = vdj._get_headers()

    http_ok = False
    http_message = ""

    try:
        async with httpx.AsyncClient(timeout=config.http_timeout) as client:
            response = await client.get(
                f"{base}/execute?script=nop",
                headers=headers,
            )
            http_ok = response.status_code == 200
            if http_ok:
                http_message = "Network Control Plugin responded (execute nop)."
            else:
                http_message = f"HTTP {response.status_code}: {response.text[:200]}"
    except httpx.ConnectError:
        http_message = (
            "Cannot connect - is VirtualDJ running and the Network Control Plugin enabled?"
        )
    except httpx.TimeoutException:
        http_message = "Connection timed out."
    except Exception as e:
        http_message = str(e)

    loop = asyncio.get_running_loop()
    osc_host = "127.0.0.1"
    osc_ok, osc_message = await loop.run_in_executor(
        None,
        lambda: _udp_send_probe(osc_host, config.osc_port),
    )

    overall = http_ok and osc_ok
    return {
        "success": overall,
        "http_plugin": {
            "ok": http_ok,
            "message": http_message,
            "base_url": base,
        },
        "osc": {
            "ok": osc_ok,
            "message": osc_message,
            "port": config.osc_port,
            "target": f"{osc_host}:{config.osc_port}",
        },
    }
