"""
VDJ Show Control Portmanteau Tool

Controls show triggers including DMX lighting (via OS2L/VDJScript) and high-end visual systems like Resolume Arena (via OSC).
"""

from typing import Any, Literal

from fastmcp import FastMCP
from pythonosc.udp_client import SimpleUDPClient
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from ..shared.exceptions import VDJError

console = Console(file=__import__("sys").stderr)


def setup_show_control_portmanteau(mcp: FastMCP):
    """Register vdj_show_control portmanteau tool."""

    @mcp.tool()
    async def vdj_show_control(
        operation: Literal["osc_send", "os2l_button", "os2l_fader", "os2l_cmd"],
        address: str | None = None,
        value: float | str | None = None,
        name: str | None = None,
        enable: bool = True,
        host: str = "127.0.0.1",
        port: int = 7000,
    ) -> dict[str, Any]:
        """
        Automate DMX lights and visuals for high-end DJ performances.

        PORTMANTEAU PATTERN: Bridges lighting software (SoundSwitch, QLC+) and visual engines (Resolume Arena).

        SUPPORTED OPERATIONS:
        - osc_send: Send an OSC UDP message to a visual server like Resolume (requires address, value)
        - os2l_button: Toggle a button state in DMX controllers via VirtualDJ's OS2L bridge (requires name, enable)
        - os2l_fader: Adjust a fader level 0-100% in DMX controllers via OS2L (requires name, value)
        - os2l_cmd: Send custom lighting events via OS2L (requires name, value)

        Args:
            operation: The show control operation to execute
            address: OSC route string, e.g. "/composition/layers/1/clips/1/connect" (for osc_send)
            value: Float, int, or string value for OSC/OS2L commands (e.g. 1.0, 50, "green")
            name: OS2L trigger identifier (e.g. "fog", "stroberate", "laser")
            enable: Boolean state toggle (default: True, for os2l_button)
            host: Network host destination for OSC packages (default: "127.0.0.1")
            port: Network port destination for OSC packages (default: 7000)

        Returns:
            Dict containing the operation results

        Examples:
            vdj_show_control("osc_send", address="/composition/layers/1/clips/1/connect", value=1) # Connect Resolume clip
            vdj_show_control("osc_send", address="/composition/dashboard/link1", value=0.75)       # Set clip tempo
            vdj_show_control("os2l_button", name="fog", enable=True)                               # Fire fog machine
            vdj_show_control("os2l_fader", name="stroberate", value=50)                            # Speed up strobe 50%
        """
        try:
            client = await get_vdj_client()

            if operation == "osc_send":
                if not address:
                    return {"success": False, "error": "address required for osc_send operation"}

                # Try parsing value to float/int if possible
                val: Any = value
                if value is not None:
                    val_str = str(value)
                    try:
                        if "." in val_str:
                            val = float(val_str)
                        else:
                            val = int(val_str)
                    except ValueError:
                        # Fallback to boolean or string
                        if val_str.lower() == "true":
                            val = True
                        elif val_str.lower() == "false":
                            val = False
                        else:
                            val = value

                try:
                    udp_client = SimpleUDPClient(host, port)
                    udp_client.send_message(address, val)
                    console.print(f"[green]OSC: Sent {val} to '{address}' on {host}:{port}[/green]")
                    return {
                        "success": True,
                        "operation": "osc_send",
                        "host": host,
                        "port": port,
                        "address": address,
                        "value": val,
                    }
                except Exception as exc:
                    return {"success": False, "error": f"Failed to transmit OSC packet: {exc}"}

            elif operation == "os2l_button":
                if not name:
                    return {"success": False, "error": "name required for os2l_button operation"}

                on_off = "on" if enable else "off"
                async with client:
                    result = await client.send_command(f"os2l_button '{name}' {on_off}")
                    if result["status"] == "success":
                        console.print(f"[green]OS2L Button '{name}': {on_off}[/green]")
                        return {"success": True, "operation": "os2l_button", "name": name, "enabled": enable}
                    else:
                        raise VDJError(f"Failed to toggle OS2L button: {result.get('error')}")

            elif operation == "os2l_fader":
                if not name or value is None:
                    return {"success": False, "error": "name and value required for os2l_fader operation"}

                try:
                    val_pct = max(0.0, min(100.0, float(value)))
                except ValueError:
                    return {"success": False, "error": "value must be a numeric percentage (0-100)"}

                async with client:
                    result = await client.send_command(f"os2l_fader '{name}' {val_pct}%")
                    if result["status"] == "success":
                        console.print(f"[green]OS2L Fader '{name}': {val_pct}%[/green]")
                        return {"success": True, "operation": "os2l_fader", "name": name, "value": val_pct}
                    else:
                        raise VDJError(f"Failed to set OS2L fader: {result.get('error')}")

            elif operation == "os2l_cmd":
                if not name or value is None:
                    return {"success": False, "error": "name and value required for os2l_cmd operation"}

                async with client:
                    result = await client.send_command(f"os2l_cmd '{name}' {value}")
                    if result["status"] == "success":
                        console.print(f"[green]OS2L Command '{name}': {value}[/green]")
                        return {"success": True, "operation": "os2l_cmd", "name": name, "value": value}
                    else:
                        raise VDJError(f"Failed to execute OS2L command: {result.get('error')}")

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_show_control: {e}[/red]")
            return {"success": False, "error": str(e)}
