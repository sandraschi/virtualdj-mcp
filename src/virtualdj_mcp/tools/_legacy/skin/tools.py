"""
Skin tools for VirtualDJ MCP

Provides tools for managing VirtualDJ skins, panels, and interface customization.
Uses HTTP Network Control Plugin API.
"""


from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from .models import SkinInfo, SkinOperationResult

# Initialize console for logging
console = Console(file=__import__('sys').stderr)


def setup_skin_tools(mcp: FastMCP):
    """
    Set up skin-related MCP tools.

    Args:
        mcp: MCP instance to register tools with
    """

    @mcp.tool()
    async def get_skin_info() -> SkinInfo:
        """
        Get information about the current VirtualDJ skin.

        Returns:
            SkinInfo with current skin details including dimensions and deck count
        """
        try:
            client = await get_vdj_client()

            async with client:
                # Query skin properties
                queries = {
                    "width": "skin_width",
                    "height": "skin_height",
                    "color": "get_skin_color",
                    "deck_count": "get_decks",
                }

                results = {}
                for key, script in queries.items():
                    result = await client.query(script)
                    if result["status"] == "success":
                        results[key] = result["result"]

                def safe_int(val, default=None):
                    try:
                        return int(float(val)) if val else default
                    except (ValueError, TypeError):
                        return default

                return SkinInfo(
                    width=safe_int(results.get("width")),
                    height=safe_int(results.get("height")),
                    color=results.get("color") or None,
                    deck_count=safe_int(results.get("deck_count")),
                )

        except Exception as e:
            console.print(f"[red]Error in get_skin_info: {e}[/red]")
            return SkinInfo()


    @mcp.tool()
    async def load_skin(
        skin_name: str,
        variation: str | None = None
    ) -> SkinOperationResult:
        """
        Load a VirtualDJ skin or skin variation.

        Args:
            skin_name: Name of the skin to load (e.g., "default", "essentialPro")
            variation: Optional variation within the skin (prefix with ":" for same-skin variation)

        Returns:
            SkinOperationResult with success status and updated skin info

        Examples:
            load_skin("default") - Load the default skin
            load_skin("essentialPro") - Load essentialPro skin
            load_skin("current", variation="dark") - Load dark variation of current skin
        """
        try:
            client = await get_vdj_client()

            async with client:
                # Build the load_skin command
                if variation:
                    # Load variation within same or different skin
                    if skin_name.lower() == "current":
                        cmd = f"load_skin ':{variation}'"
                    else:
                        cmd = f"load_skin '{skin_name}:{variation}'"
                else:
                    cmd = f"load_skin '{skin_name}'"

                result = await client.send_command(cmd)

                if result["status"] == "success" and result.get("result", "").lower() == "true":
                    console.print(f"[green]Loaded skin: {skin_name}[/green]")

                    # Get updated skin info
                    skin_info = await get_skin_info()

                    return SkinOperationResult(
                        success=True,
                        message=f"Successfully loaded skin: {skin_name}" + (f" ({variation})" if variation else ""),
                        skin_info=skin_info
                    )
                else:
                    return SkinOperationResult(
                        success=False,
                        message=f"Failed to load skin: {skin_name}. Skin may not exist."
                    )

        except Exception as e:
            console.print(f"[red]Error in load_skin: {e}[/red]")
            return SkinOperationResult(
                success=False,
                message=f"Error loading skin: {e!s}"
            )


    @mcp.tool()
    async def switch_skin_variation(variation: str) -> SkinOperationResult:
        """
        Switch to a different variation of the current skin.

        Args:
            variation: Name of the variation to switch to

        Returns:
            SkinOperationResult with success status
        """
        try:
            client = await get_vdj_client()

            async with client:
                cmd = f"switch_skin_variation '{variation}'"
                result = await client.send_command(cmd)

                if result["status"] == "success" and result.get("result", "").lower() == "true":
                    console.print(f"[green]Switched to skin variation: {variation}[/green]")
                    skin_info = await get_skin_info()
                    return SkinOperationResult(
                        success=True,
                        message=f"Switched to variation: {variation}",
                        skin_info=skin_info
                    )
                else:
                    return SkinOperationResult(
                        success=False,
                        message=f"Failed to switch variation. '{variation}' may not exist in current skin."
                    )

        except Exception as e:
            console.print(f"[red]Error in switch_skin_variation: {e}[/red]")
            return SkinOperationResult(
                success=False,
                message=f"Error switching variation: {e!s}"
            )


    @mcp.tool()
    async def set_skin_panel(
        panel_name: str,
        visible: bool = True
    ) -> SkinOperationResult:
        """
        Show or hide a panel on the VirtualDJ skin.

        Args:
            panel_name: Name of the panel to show/hide (skin-dependent)
            visible: True to show, False to hide

        Returns:
            SkinOperationResult with operation status

        Note:
            Panel names are skin-specific. Common panels include:
            - "browser", "sampler", "effects", "video", "mixer"
            Check your skin's documentation for available panels.
        """
        try:
            client = await get_vdj_client()

            async with client:
                state = "on" if visible else "off"
                cmd = f"skin_panel '{panel_name}' {state}"
                result = await client.send_command(cmd)

                if result["status"] == "success" and result.get("result", "").lower() == "true":
                    action = "shown" if visible else "hidden"
                    console.print(f"[green]Panel '{panel_name}' {action}[/green]")
                    return SkinOperationResult(
                        success=True,
                        message=f"Panel '{panel_name}' {action}"
                    )
                else:
                    return SkinOperationResult(
                        success=False,
                        message=f"Failed to modify panel '{panel_name}'. Panel may not exist in current skin."
                    )

        except Exception as e:
            console.print(f"[red]Error in set_skin_panel: {e}[/red]")
            return SkinOperationResult(
                success=False,
                message=f"Error modifying panel: {e!s}"
            )


    @mcp.tool()
    async def set_skin_panel_group(
        group_name: str,
        panel_name: str | None = None,
        index: int | None = None
    ) -> SkinOperationResult:
        """
        Switch which panel is shown in a skin panel group.

        Args:
            group_name: Name of the panel group
            panel_name: Name of the panel to show (use this OR index)
            index: Index/position to switch to (use this OR panel_name)

        Returns:
            SkinOperationResult with operation status

        Examples:
            set_skin_panel_group("browser", panel_name="folders") - Show folders panel in browser group
            set_skin_panel_group("decks", index=1) - Switch to second deck layout option
        """
        try:
            client = await get_vdj_client()

            async with client:
                if panel_name:
                    cmd = f"skin_panelgroup '{group_name}' '{panel_name}'"
                elif index is not None:
                    cmd = f"skin_panelgroup '{group_name}' {index}"
                else:
                    return SkinOperationResult(
                        success=False,
                        message="Either panel_name or index must be provided"
                    )

                result = await client.send_command(cmd)

                if result["status"] == "success" and result.get("result", "").lower() == "true":
                    target = panel_name if panel_name else f"index {index}"
                    console.print(f"[green]Panel group '{group_name}' switched to {target}[/green]")
                    return SkinOperationResult(
                        success=True,
                        message=f"Panel group '{group_name}' switched to {target}"
                    )
                else:
                    return SkinOperationResult(
                        success=False,
                        message=f"Failed to switch panel group '{group_name}'"
                    )

        except Exception as e:
            console.print(f"[red]Error in set_skin_panel_group: {e}[/red]")
            return SkinOperationResult(
                success=False,
                message=f"Error switching panel group: {e!s}"
            )


    @mcp.tool()
    async def toggle_skin_window(
        window_name: str,
        visible: bool | None = None
    ) -> SkinOperationResult:
        """
        Show or hide a window on skins with multiple windows.

        Args:
            window_name: Name of the window to toggle
            visible: True to show, False to hide, None to toggle

        Returns:
            SkinOperationResult with operation status

        Note:
            Only works on skins that support multiple windows.
        """
        try:
            client = await get_vdj_client()

            async with client:
                if visible is None:
                    cmd = f"window '{window_name}'"  # Toggle
                else:
                    state = "on" if visible else "off"
                    cmd = f"window '{window_name}' {state}"

                result = await client.send_command(cmd)

                if result["status"] == "success" and result.get("result", "").lower() == "true":
                    console.print(f"[green]Window '{window_name}' toggled[/green]")
                    return SkinOperationResult(
                        success=True,
                        message=f"Window '{window_name}' toggled successfully"
                    )
                else:
                    return SkinOperationResult(
                        success=False,
                        message=f"Failed to toggle window '{window_name}'. Window may not exist or skin doesn't support multiple windows."
                    )

        except Exception as e:
            console.print(f"[red]Error in toggle_skin_window: {e}[/red]")
            return SkinOperationResult(
                success=False,
                message=f"Error toggling window: {e!s}"
            )

