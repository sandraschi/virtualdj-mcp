#!/usr/bin/env python3
"""
Plex + VirtualDJ Integration Demo

Mix ABBA and Pink Floyd tracks from Plex libraries using VirtualDJ!

This demonstrates the new vdj_plex portmanteau tool that enables
seamless integration between Plex Media Server and VirtualDJ.

Usage:
    # Set environment variables first
    $env:PLEX_TOKEN = "your_plex_token"
    $env:PLEX_SERVER_URL = "http://localhost:32400"  # optional
    
    python demos/plex_mix_demo.py

Requirements:
    - VirtualDJ running with Network Control Plugin enabled
    - Plex Media Server with music libraries
    - ABBA and Pink Floyd tracks in your Plex library
"""

import asyncio
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


async def main():
    """Run the Plex + VirtualDJ demo."""
    
    console.print(Panel.fit(
        "[bold magenta]🎵 PLEX + VIRTUALDJ INTEGRATION DEMO 🎵[/bold magenta]\n\n"
        "Mix ABBA and Pink Floyd tracks from your Plex library!",
        border_style="magenta"
    ))
    
    # Check Plex configuration
    plex_token = os.getenv("PLEX_TOKEN")
    plex_url = os.getenv("PLEX_SERVER_URL", "http://localhost:32400")
    
    if not plex_token:
        console.print("[red]❌ PLEX_TOKEN not set![/red]")
        console.print("Set your Plex token: $env:PLEX_TOKEN = 'your_token'")
        return
    
    console.print(f"[green]✓ Plex configured: {plex_url}[/green]")
    
    # Import VDJ client and portmanteau tools
    try:
        from virtualdj_mcp.tools.portmanteau.plex import vdj_plex
        from virtualdj_mcp.tools.portmanteau.deck import vdj_deck
        from virtualdj_mcp.tools.portmanteau.mixer import vdj_mixer
        from virtualdj_mcp.tools.portmanteau.stems import vdj_stems
        from virtualdj_mcp.tools.portmanteau.system import vdj_system
    except ImportError as e:
        console.print(f"[red]Import error: {e}[/red]")
        console.print("Make sure you've installed the package: pip install -e .")
        return
    
    # Step 1: Check VirtualDJ connection
    console.print("\n[bold]Step 1: Testing VirtualDJ connection...[/bold]")
    
    # Note: For this demo, we'll simulate the calls
    # In real usage with Claude, these tools are registered with the MCP server
    
    console.print("[yellow]This demo shows the workflow. In Claude Desktop/Cursor,[/yellow]")
    console.print("[yellow]you can use these commands directly:[/yellow]\n")
    
    # Display example workflow
    workflow = Table(title="Plex + VirtualDJ Workflow", show_header=True)
    workflow.add_column("Step", style="cyan")
    workflow.add_column("Command", style="green")
    workflow.add_column("Description", style="white")
    
    workflow.add_row(
        "1",
        'vdj_plex("list_libraries")',
        "List your Plex music libraries"
    )
    workflow.add_row(
        "2",
        'vdj_plex("search", query="ABBA", limit=5)',
        "Search for ABBA tracks"
    )
    workflow.add_row(
        "3",
        'vdj_plex("search", artist="Pink Floyd", limit=5)',
        "Search for Pink Floyd tracks"
    )
    workflow.add_row(
        "4",
        'vdj_plex("load_from_plex", query="Dancing Queen", deck_id=1)',
        "Load ABBA's Dancing Queen to deck 1"
    )
    workflow.add_row(
        "5",
        'vdj_plex("load_from_plex", artist="Pink Floyd", deck_id=2)',
        "Load Pink Floyd to deck 2"
    )
    workflow.add_row(
        "6",
        'vdj_deck("play", deck_id=1)',
        "Start playing deck 1"
    )
    workflow.add_row(
        "7",
        'vdj_mixer("sync", deck_a=1, deck_b=2)',
        "Sync deck 2 BPM to deck 1"
    )
    workflow.add_row(
        "8",
        'vdj_mixer("crossfader", position=0)',
        "Center crossfader for 50/50 mix"
    )
    workflow.add_row(
        "9",
        'vdj_stems("swap", deck_a=1, deck_b=2, stem="vocal")',
        "ABBA vocals over Pink Floyd instrumental!"
    )
    
    console.print(workflow)
    
    # Example Claude prompt
    console.print("\n[bold magenta]Example Claude Prompt:[/bold magenta]")
    console.print(Panel(
        '"Search my Plex library for ABBA and Pink Floyd tracks, load Dancing Queen to deck 1 and '
        'Wish You Were Here to deck 2, sync the BPMs, and then swap the vocals to create a mashup!"',
        title="Ask Claude",
        border_style="green"
    ))
    
    # Available portmanteau tools
    console.print("\n[bold]All 13 Portmanteau Tools Available:[/bold]")
    
    tools_table = Table(show_header=True)
    tools_table.add_column("Tool", style="cyan")
    tools_table.add_column("Operations", style="white")
    
    tools_table.add_row("vdj_deck", "play, pause, toggle, stop, load, seek, volume, status, load_security")
    tools_table.add_row("vdj_mixer", "crossfader, sync, eq_high, eq_mid, eq_low, gain, filter")
    tools_table.add_row("vdj_library", "search, analyze")
    tools_table.add_row("vdj_automation", "start, stop, status, suggest, preferences")
    tools_table.add_row("vdj_recording", "start, stop, status, list, export, delete")
    tools_table.add_row("vdj_performance", "metrics, stats, trends, recommendations, export")
    tools_table.add_row("vdj_stems", "kill, unkill, volume, acapella, instrumental, isolate_drums, swap, reset")
    tools_table.add_row("vdj_beatgrid", "set_bpm, tap, adjust, anchor, pitch_bend, pitch_reset, beat_jump, loop, loop_roll, loop_exit")
    tools_table.add_row("vdj_skin", "info, load, variation, panel, panel_group, window")
    tools_table.add_row("vdj_video", "crossfader, transition, fx, text, output, master, karaoke, scratch, loop, tempo_sync, load")
    tools_table.add_row("[bold green]vdj_plex[/bold green]", "[bold green]search, get_path, load_from_plex, list_libraries[/bold green]")
    tools_table.add_row("vdj_system", "status, help, connection_test")
    
    console.print(tools_table)
    
    console.print("\n[bold green]✓ Demo complete![/bold green]")
    console.print("Use these tools in Claude Desktop or Cursor to mix music from Plex!")


if __name__ == "__main__":
    asyncio.run(main())

