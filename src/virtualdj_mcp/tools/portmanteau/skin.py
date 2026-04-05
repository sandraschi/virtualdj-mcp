"""
VDJ Skin Portmanteau Tool

Consolidates skin control operations into a single interface.
Operations: info, load, variation, panel, panel_group, window
"""

from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from ..shared.exceptions import VDJError

console = Console(file=__import__('sys').stderr)


def setup_skin_portmanteau(mcp: FastMCP):
    """Register vdj_skin portmanteau tool."""

    @mcp.tool()
    async def vdj_skin(
        operation: Literal["info", "load", "variation", "panel", "panel_group", "window"],
        skin_name: str | None = None,
        variation: str | None = None,
        panel_name: str | None = None,
        group_name: str | None = None,
        window_name: str | None = None,
        visible: bool | None = None,
        index: int | None = None
    ) -> dict[str, Any]:
        """
        Skin control for VirtualDJ.

        PORTMANTEAU PATTERN: Consolidates 6 skin tools into 1 unified interface.

        SUPPORTED OPERATIONS:
        - info: Get current skin information
        - load: Load a skin (requires skin_name, optional variation)
        - variation: Switch skin variation
        - panel: Show/hide a skin panel
        - panel_group: Switch panel in a panel group
        - window: Toggle skin window visibility

        Args:
            operation: The skin operation to perform
            skin_name: Name of skin to load (e.g., "default", "essentialPro")
            variation: Skin variation name
            panel_name: Panel name to show/hide
            group_name: Panel group name
            window_name: Window name to toggle
            visible: True to show, False to hide
            index: Index for panel group switching

        Returns:
            Dict with operation result

        Examples:
            vdj_skin("info")
            vdj_skin("load", skin_name="essentialPro")
            vdj_skin("load", skin_name="default", variation="dark")
            vdj_skin("variation", variation="dark")
            vdj_skin("panel", panel_name="browser", visible=True)
            vdj_skin("panel_group", group_name="decks", index=1)
            vdj_skin("window", window_name="video", visible=True)
        """
        try:
            client = await get_vdj_client()

            if operation == "info":
                async with client:
                    # Get skin info via queries
                    skin_result = await client.query("get_skin")
                    width_result = await client.query("skin_width")
                    height_result = await client.query("skin_height")
                    decks_result = await client.query("skin_decks")

                    return {
                        "success": True,
                        "operation": "info",
                        "skin_name": skin_result.get("result", "unknown"),
                        "width": int(width_result.get("result", 0)) if width_result.get("result") else None,
                        "height": int(height_result.get("result", 0)) if height_result.get("result") else None,
                        "deck_count": int(decks_result.get("result", 2)) if decks_result.get("result") else 2
                    }

            elif operation == "load":
                if not skin_name:
                    return {"success": False, "error": "skin_name required for load operation"}

                async with client:
                    if variation:
                        cmd = f"skin '{skin_name}' '{variation}'"
                    else:
                        cmd = f"skin '{skin_name}'"

                    result = await client.send_command(cmd)
                    if result["status"] == "success":
                        console.print(f"[green]Skin loaded: {skin_name}{f' ({variation})' if variation else ''}[/green]")
                        return {
                            "success": True,
                            "operation": "load",
                            "skin_name": skin_name,
                            "variation": variation
                        }
                    else:
                        raise VDJError(f"Failed to load skin: {result.get('error')}")

            elif operation == "variation":
                if not variation:
                    return {"success": False, "error": "variation required for variation operation"}

                async with client:
                    result = await client.send_command(f"skin_variation '{variation}'")
                    if result["status"] == "success":
                        console.print(f"[green]Skin variation switched to: {variation}[/green]")
                        return {"success": True, "operation": "variation", "variation": variation}
                    else:
                        raise VDJError(f"Failed to switch variation: {result.get('error')}")

            elif operation == "panel":
                if not panel_name:
                    return {"success": False, "error": "panel_name required for panel operation"}

                show = visible if visible is not None else True

                async with client:
                    action = "show" if show else "hide"
                    result = await client.send_command(f"skin_panel '{panel_name}' {action}")
                    if result["status"] == "success":
                        console.print(f"[green]Panel '{panel_name}' {action}n[/green]")
                        return {"success": True, "operation": "panel", "panel_name": panel_name, "visible": show}
                    else:
                        raise VDJError(f"Failed to {action} panel: {result.get('error')}")

            elif operation == "panel_group":
                if not group_name:
                    return {"success": False, "error": "group_name required for panel_group operation"}

                async with client:
                    if panel_name:
                        cmd = f"skin_panel_group '{group_name}' '{panel_name}'"
                    elif index is not None:
                        cmd = f"skin_panel_group '{group_name}' {index}"
                    else:
                        return {"success": False, "error": "Either panel_name or index required for panel_group"}

                    result = await client.send_command(cmd)
                    if result["status"] == "success":
                        console.print(f"[green]Panel group '{group_name}' switched[/green]")
                        return {
                            "success": True,
                            "operation": "panel_group",
                            "group_name": group_name,
                            "panel_name": panel_name,
                            "index": index
                        }
                    else:
                        raise VDJError(f"Failed to switch panel group: {result.get('error')}")

            elif operation == "window":
                if not window_name:
                    return {"success": False, "error": "window_name required for window operation"}

                async with client:
                    if visible is None:
                        # Toggle
                        cmd = f"skin_window_toggle '{window_name}'"
                    else:
                        action = "show" if visible else "hide"
                        cmd = f"skin_window '{window_name}' {action}"

                    result = await client.send_command(cmd)
                    if result["status"] == "success":
                        console.print(f"[green]Window '{window_name}' toggled[/green]")
                        return {"success": True, "operation": "window", "window_name": window_name, "visible": visible}
                    else:
                        raise VDJError(f"Failed to toggle window: {result.get('error')}")

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_skin: {e}[/red]")
            return {"success": False, "error": str(e)}

