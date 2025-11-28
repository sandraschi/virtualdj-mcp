"""
Performance Monitor Example for VirtualDJ-MCP

This script demonstrates how to monitor VirtualDJ performance metrics
including deck status, playback information, and system variables.
"""
import asyncio
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import from virtualdj_mcp
import sys
sys.path.append(str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.live import Live

from virtualdj_mcp.core.vdj_client import VirtualDJClient
from virtualdj_mcp.config import VDJConfig

async def main():
    print("📊 VirtualDJ-MCP Performance Monitor")
    print("=" * 50)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Monitor VirtualDJ performance')
    parser.add_argument('--output', type=str, default=None,
                      help='Output file for metrics (JSON format)')
    parser.add_argument('--interval', type=float, default=2.0,
                      help='Update interval in seconds (default: 2.0)')
    parser.add_argument('--duration', type=int, default=60,
                      help='Monitoring duration in seconds (default: 60)')

    args = parser.parse_args()

    # Load configuration
    config = VDJConfig()
    print(f"Using VirtualDJ path: {config.virtualdj_path}")

    # Initialize VirtualDJ client
    async with VirtualDJClient(config) as vdj:
        print("✅ Connected to VirtualDJ client")

        # Check if VirtualDJ is running
        if not await vdj.is_running():
            print("⚠️  VirtualDJ is not running. Starting it...")
            if not await vdj.start_virtualdj():
                print("❌ Failed to start VirtualDJ. Please start it manually.")
                return

        print("🎧 VirtualDJ is running - starting performance monitoring")
        print(f"⏱️  Monitoring for {args.duration} seconds (updates every {args.interval}s)")
        print("Press Ctrl+C to stop early\n")

        # Metrics storage
        metrics_history = []
        start_time = datetime.now()
        elapsed = 0

        try:
            while elapsed < args.duration:
                # Collect performance metrics
                metrics = await collect_metrics(vdj)
                metrics['timestamp'] = datetime.now().isoformat()
                metrics['elapsed_seconds'] = elapsed
                metrics_history.append(metrics)

                # Display current metrics
                display_metrics(metrics)

                # Wait for next update
                await asyncio.sleep(args.interval)
                elapsed = (datetime.now() - start_time).total_seconds()

        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")

        # Save metrics if output file specified
        if args.output:
            output_file = Path(args.output)
            with open(output_file, 'w') as f:
                json.dump(metrics_history, f, indent=2)
            print(f"📊 Metrics saved to: {output_file}")

        print("✅ Performance monitoring completed!")
        print(f"📈 Collected {len(metrics_history)} data points")

async def collect_metrics(vdj: VirtualDJClient) -> dict:
    """Collect performance metrics from VirtualDJ."""
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'decks': {},
        'mixer': {},
        'system': {}
    }

    try:
        # Deck metrics
        for deck in [1, 2]:
            deck_metrics = {}
            try:
                # Basic deck info
                deck_metrics['title'] = await vdj.get_variable(f'deck{deck}_title') or 'No track'
                deck_metrics['artist'] = await vdj.get_variable(f'deck{deck}_artist') or 'Unknown'
                deck_metrics['bpm'] = await vdj.get_variable(f'deck{deck}_bpm') or '0'
                deck_metrics['position'] = await vdj.get_variable(f'deck{deck}_position') or '0'
                deck_metrics['volume'] = await vdj.get_variable(f'deck{deck}_volume') or '0'

                # Playback state
                play_state = await vdj.get_variable(f'deck{deck}_play')
                deck_metrics['playing'] = play_state == '1'

            except Exception as e:
                deck_metrics['error'] = str(e)

            metrics['decks'][f'deck_{deck}'] = deck_metrics

        # Mixer metrics
        try:
            metrics['mixer']['crossfader'] = await vdj.get_variable('crossfader') or '0'
            metrics['mixer']['master_volume'] = await vdj.get_variable('master_volume') or '0'
        except Exception as e:
            metrics['mixer']['error'] = str(e)

        # System metrics
        try:
            metrics['system']['cpu_usage'] = await vdj.get_variable('cpu_usage') or '0'
            metrics['system']['sample_rate'] = await vdj.get_variable('sample_rate') or '44100'
        except Exception as e:
            metrics['system']['error'] = str(e)

    except Exception as e:
        metrics['error'] = f"Failed to collect metrics: {e}"

    return metrics

def display_metrics(metrics: dict):
    """Display current metrics in a nice format."""
    console = Console()

    # Clear screen and move cursor to top
    console.clear()

    # Header
    console.print(f"[bold blue]🎵 VirtualDJ Performance Monitor[/bold blue] - {metrics.get('timestamp', 'Unknown')[:19]}")
    console.print("=" * 60)

    # Decks table
    deck_table = Table(title="🎛️  Deck Status")
    deck_table.add_column("Deck", style="cyan", no_wrap=True)
    deck_table.add_column("Track", style="white", max_width=30)
    deck_table.add_column("Artist", style="white", max_width=20)
    deck_table.add_column("BPM", style="yellow", justify="right")
    deck_table.add_column("Position", style="green", justify="right")
    deck_table.add_column("Volume", style="magenta", justify="right")
    deck_table.add_column("Status", style="red")

    for deck_name, deck_data in metrics.get('decks', {}).items():
        if 'error' in deck_data:
            deck_table.add_row(
                deck_name.replace('deck_', '').upper(),
                "[red]Error[/red]",
                deck_data['error'][:20],
                "-", "-", "-", "❌"
            )
        else:
            status = "▶️" if deck_data.get('playing', False) else "⏸️"
            deck_table.add_row(
                deck_name.replace('deck_', '').upper(),
                deck_data.get('title', 'No track')[:30],
                deck_data.get('artist', 'Unknown')[:20],
                deck_data.get('bpm', '0'),
                f"{float(deck_data.get('position', 0)):.1f}s",
                f"{deck_data.get('volume', '0')}%",
                status
            )

    console.print(deck_table)

    # Mixer and System info
    mixer_data = metrics.get('mixer', {})
    system_data = metrics.get('system', {})

    console.print(f"\n🎚️  [bold]Mixer:[/bold] Crossfader: {mixer_data.get('crossfader', '0')}% | Master: {mixer_data.get('master_volume', '0')}%")
    console.print(f"🖥️  [bold]System:[/bold] CPU: {system_data.get('cpu_usage', '0')}% | Sample Rate: {system_data.get('sample_rate', '44100')}Hz")

    if 'error' in metrics:
        console.print(f"\n[red]❌ Error: {metrics['error']}[/red]")

    console.print(f"\n[blue]Monitoring... ({metrics.get('elapsed_seconds', 0):.1f}s elapsed)[/blue]")

if __name__ == "__main__":
    asyncio.run(main())
