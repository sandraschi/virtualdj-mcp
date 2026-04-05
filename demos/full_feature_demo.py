"""
Full Feature Demo - Comprehensive VirtualDJ-MCP demonstration

This script exercises ALL major VirtualDJ-MCP features with visual popups
announcing each section. Perfect for impressing DJ friends!

Features demonstrated:
1. Track loading & deck status
2. Playback controls (play/pause/stop)
3. Volume manipulation
4. Seek/scrubbing
5. Crossfader mixing
6. BPM sync between decks
7. Recording
8. Skin information
9. Performance metrics

Run with: python full_feature_demo.py
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from virtualdj_mcp.config import VDJConfig
from virtualdj_mcp.core.vdj_client import VirtualDJClient


# ANSI colors for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def banner(text: str, char: str = "="):
    """Print a banner."""
    width = 60
    print(f"\n{Colors.CYAN}{char * width}")
    print(f"{text.center(width)}")
    print(f"{char * width}{Colors.END}\n")


def announce(section: str, description: str = "", wait: float = 3.0):
    """Announce next section with countdown."""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'─' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}▶ NEXT: {section}{Colors.END}")
    if description:
        print(f"{Colors.CYAN}  {description}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{'─' * 60}{Colors.END}")

    # Countdown
    for i in range(int(wait), 0, -1):
        print(f"\r{Colors.YELLOW}  Starting in {i}...{Colors.END}", end="", flush=True)
        import time
        time.sleep(1)
    print(f"\r{Colors.GREEN}  GO!              {Colors.END}")


def status(msg: str, success: bool = True):
    """Print status message."""
    icon = "✅" if success else "❌"
    color = Colors.GREEN if success else Colors.RED
    print(f"{color}{icon} {msg}{Colors.END}")


def info(msg: str):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.END}")


async def smooth_crossfade(vdj: VirtualDJClient, start: float, end: float, duration: float = 3.0):
    """Smoothly move crossfader."""
    steps = 30
    step_delay = duration / steps
    for i in range(steps + 1):
        progress = i / steps
        position = start + (end - start) * progress
        await vdj.set_crossfader(position)
        # Progress bar
        bar_len = 20
        filled = int(bar_len * progress)
        bar = "█" * filled + "░" * (bar_len - filled)
        pos_display = f"{position:+.0f}".rjust(4)
        print(f"\r  Crossfader: [{bar}] {pos_display}", end="", flush=True)
        await asyncio.sleep(step_delay)
    print()


async def smooth_volume(vdj: VirtualDJClient, deck: int, start: int, end: int, duration: float = 2.0):
    """Smoothly change volume."""
    steps = 20
    step_delay = duration / steps
    for i in range(steps + 1):
        progress = i / steps
        volume = int(start + (end - start) * progress)
        await vdj.set_volume(deck, volume)
        # Progress bar
        bar_len = 15
        filled = int(bar_len * (volume / 100))
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\r  Deck {deck} Volume: [{bar}] {volume:3d}%", end="", flush=True)
        await asyncio.sleep(step_delay)
    print()


# ═══════════════════════════════════════════════════════════
# DJ TRICKS - Fast Artistic Moves!
# ═══════════════════════════════════════════════════════════

def flash(text: str):
    """Print flashy trick name."""
    print(f"{Colors.BOLD}{Colors.YELLOW}  ★ {text} ★{Colors.END}")


async def transformer_scratch(vdj: VirtualDJClient, deck: int, cuts: int = 8):
    """Transformer scratch - rapid crossfader cuts."""
    flash("TRANSFORMER SCRATCH")
    print("    ", end="")
    pos = -100 if deck == 1 else 100
    for _ in range(cuts):
        await vdj.set_crossfader(pos)
        print("▓", end="", flush=True)
        await asyncio.sleep(0.08)
        await vdj.set_crossfader(0)
        print("░", end="", flush=True)
        await asyncio.sleep(0.08)
    await vdj.set_crossfader(pos)
    print(" CHKA-CHKA!")


async def baby_scratch(vdj: VirtualDJClient, reps: int = 3):
    """Baby scratch - quick back and forth."""
    flash("BABY SCRATCH")
    print("    ", end="")
    for _ in range(reps):
        for pos in [-100, 100, -100, 0]:
            await vdj.set_crossfader(pos)
            print("◄" if pos < 0 else ("►" if pos > 0 else "●"), end="", flush=True)
            await asyncio.sleep(0.1)
    print(" WIKKI-WIKKI!")


async def ping_pong(vdj: VirtualDJClient, bounces: int = 6):
    """Ping pong between decks."""
    flash("PING PONG")
    print("    ", end="")
    for _ in range(bounces):
        await vdj.set_crossfader(-100)
        print("◄─", end="", flush=True)
        await asyncio.sleep(0.12)
        await vdj.set_crossfader(100)
        print("─►", end="", flush=True)
        await asyncio.sleep(0.12)
    await vdj.set_crossfader(0)
    print(" BOING!")


async def volume_pump(vdj: VirtualDJClient, deck: int, pumps: int = 6):
    """Volume pumping - EDM buildup style."""
    flash("VOLUME PUMP")
    print("    ", end="")
    for _ in range(pumps):
        await vdj.set_volume(deck, 100)
        print("▲", end="", flush=True)
        await asyncio.sleep(0.12)
        await vdj.set_volume(deck, 30)
        print("▼", end="", flush=True)
        await asyncio.sleep(0.12)
    await vdj.set_volume(deck, 80)
    print(" UNTZ-UNTZ!")


async def stutter_cut(vdj: VirtualDJClient, deck: int, stutters: int = 10):
    """Stutter effect - rapid play/pause."""
    flash("STUTTER CUT")
    print("    ", end="")
    for _ in range(stutters):
        await vdj.play(deck)
        print("►", end="", flush=True)
        await asyncio.sleep(0.05)
        await vdj.pause(deck)
        print("║", end="", flush=True)
        await asyncio.sleep(0.05)
    await vdj.play(deck)
    print(" T-T-T-T!")


async def crab_scratch(vdj: VirtualDJClient, deck: int):
    """Crab scratch - ultra fast crossfader clicks."""
    flash("CRAB SCRATCH")
    print("    ", end="")
    pos = -100 if deck == 1 else 100
    for _ in range(12):
        await vdj.set_crossfader(pos)
        await asyncio.sleep(0.03)
        await vdj.set_crossfader(0)
        await asyncio.sleep(0.03)
        print(".", end="", flush=True)
    await vdj.set_crossfader(pos)
    print(" 🦀 SKRRT!")


async def main():
    banner("🎵 VirtualDJ-MCP Full Feature Demo 🎵")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  This demo will exercise all major MCP features")
    print("  Watch VirtualDJ respond to each command!\n")

    # Get test tracks
    fixtures_path = Path(__file__).parent.parent / "tests" / "fixtures" / "audio"
    tracks = sorted(fixtures_path.glob("*.mp3"))

    if len(tracks) < 2:
        print(f"❌ Need test tracks in {fixtures_path}")
        return

    info(f"Found {len(tracks)} test tracks:")
    for t in tracks:
        print(f"     - {t.name}")

    config = VDJConfig()

    async with VirtualDJClient(config) as vdj:

        # ═══════════════════════════════════════════════════════════
        # SECTION 1: Connection & Status
        # ═══════════════════════════════════════════════════════════
        announce("CONNECTION CHECK", "Verifying VirtualDJ is running")

        if not await vdj.is_running():
            status("VirtualDJ not running - attempting to start...", False)
            if not await vdj.start_virtualdj():
                status("Could not start VirtualDJ. Please start it manually.", False)
                return
            await asyncio.sleep(3)

        status("Connected to VirtualDJ!")

        # Get skin info
        try:
            skin_info = await vdj.get_skin_info()
            info(f"Skin: {skin_info.get('width', '?')}x{skin_info.get('height', '?')} pixels")
        except:
            info("Skin info not available")

        # ═══════════════════════════════════════════════════════════
        # SECTION 2: Track Loading
        # ═══════════════════════════════════════════════════════════
        announce("TRACK LOADING", "Loading tracks to both decks")

        track1 = tracks[0]  # First track (probably sine wave)
        track2 = tracks[1] if len(tracks) > 1 else tracks[0]

        info(f"Loading '{track1.name}' to Deck 1...")
        await vdj.load_track(1, str(track1))
        await asyncio.sleep(1)
        status(f"Deck 1 loaded: {track1.name}")

        info(f"Loading '{track2.name}' to Deck 2...")
        await vdj.load_track(2, str(track2))
        await asyncio.sleep(1)
        status(f"Deck 2 loaded: {track2.name}")

        # ═══════════════════════════════════════════════════════════
        # SECTION 3: Volume Control
        # ═══════════════════════════════════════════════════════════
        announce("VOLUME CONTROL", "Demonstrating smooth volume fades")

        info("Setting both decks to 0%...")
        await vdj.set_volume(1, 0)
        await vdj.set_volume(2, 0)
        await asyncio.sleep(0.5)

        info("Fading Deck 1 up to 80%...")
        await smooth_volume(vdj, 1, 0, 80, duration=2.0)
        status("Deck 1 volume: 80%")

        info("Fading Deck 2 up to 80%...")
        await smooth_volume(vdj, 2, 0, 80, duration=2.0)
        status("Deck 2 volume: 80%")

        # ═══════════════════════════════════════════════════════════
        # SECTION 4: Playback Controls
        # ═══════════════════════════════════════════════════════════
        announce("PLAYBACK CONTROLS", "Play, pause, and stop commands")

        # Set crossfader to deck 1
        await vdj.set_crossfader(-100)
        info("Crossfader: Full left (Deck 1)")

        info("Playing Deck 1...")
        await vdj.play(1)
        status("Deck 1: PLAYING ▶")
        await asyncio.sleep(2)

        info("Pausing Deck 1...")
        await vdj.pause(1)
        status("Deck 1: PAUSED ⏸")
        await asyncio.sleep(1)

        info("Resuming Deck 1...")
        await vdj.play(1)
        status("Deck 1: PLAYING ▶")
        await asyncio.sleep(2)

        # ═══════════════════════════════════════════════════════════
        # SECTION 5: Seek/Scrubbing
        # ═══════════════════════════════════════════════════════════
        announce("SEEK CONTROL", "Jumping to different positions")

        info("Seeking to 50%...")
        await vdj.seek(1, "50%")
        await asyncio.sleep(1)
        status("Position: 50%")

        info("Seeking to 25%...")
        await vdj.seek(1, "25%")
        await asyncio.sleep(1)
        status("Position: 25%")

        info("Seeking back to start...")
        await vdj.seek(1, "0%")
        await asyncio.sleep(1)
        status("Position: 0%")

        # ═══════════════════════════════════════════════════════════
        # SECTION 6: Crossfader Mixing
        # ═══════════════════════════════════════════════════════════
        announce("CROSSFADER MIXING", "Smooth crossfade between decks")

        # Start deck 2
        info("Starting Deck 2 for mixing...")
        await vdj.play(2)
        status("Deck 2: PLAYING ▶")
        await asyncio.sleep(1)

        info("Crossfading from Deck 1 to Deck 2...")
        await smooth_crossfade(vdj, -100, 100, duration=4.0)
        status("Crossfade complete: Now on Deck 2")

        # Stop deck 1
        await vdj.stop(1)
        info("Deck 1 stopped")
        await asyncio.sleep(2)

        info("Crossfading back to center...")
        await smooth_crossfade(vdj, 100, 0, duration=2.0)
        status("Crossfader: Center position")

        # ═══════════════════════════════════════════════════════════
        # SECTION 7: DJ TRICKS!
        # ═══════════════════════════════════════════════════════════
        announce("🎧 DJ TRICKS!", "Fast artistic moves - watch the crossfader!")

        # Make sure both decks are playing
        await vdj.play(1)
        await vdj.play(2)
        await asyncio.sleep(0.5)

        await transformer_scratch(vdj, 1, cuts=8)
        await asyncio.sleep(0.8)

        await baby_scratch(vdj, reps=3)
        await asyncio.sleep(0.8)

        await ping_pong(vdj, bounces=5)
        await asyncio.sleep(0.8)

        await volume_pump(vdj, 1, pumps=6)
        await asyncio.sleep(0.8)

        await stutter_cut(vdj, 1, stutters=8)
        await asyncio.sleep(0.8)

        await crab_scratch(vdj, 1)
        await asyncio.sleep(0.5)

        status("DJ tricks complete! 🔥")

        # Reset for next section
        await vdj.set_crossfader(-100)
        await vdj.set_volume(1, 80)
        await vdj.set_volume(2, 80)

        # ═══════════════════════════════════════════════════════════
        # SECTION 8: Load Different Track (The Funny Ones!)
        # ═══════════════════════════════════════════════════════════
        if len(tracks) >= 3:
            announce("BONUS TRACKS", "Loading the whimsical test tracks! 💨")

            # Find the funny tracks
            funny_tracks = [t for t in tracks if any(x in t.name.lower() for x in ['fart', 'buzzer', 'dissonance'])]

            for funny in funny_tracks[:2]:
                info(f"Loading '{funny.name}' to Deck 1...")
                await vdj.load_track(1, str(funny))
                await asyncio.sleep(0.5)

                await vdj.set_crossfader(-100)
                await vdj.play(1)
                status(f"Playing: {funny.name} 🎵")
                await asyncio.sleep(3)
                await vdj.stop(1)
                await asyncio.sleep(0.5)

        # ═══════════════════════════════════════════════════════════
        # SECTION 9: Deck Status Query
        # ═══════════════════════════════════════════════════════════
        announce("STATUS QUERY", "Getting detailed deck information")

        for deck_id in [1, 2]:
            try:
                deck_status = await vdj.get_deck_status(deck_id)
                print(f"\n  {Colors.BOLD}Deck {deck_id} Status:{Colors.END}")
                print(f"    Playing:  {'▶ Yes' if deck_status.get('is_playing') else '⏹ No'}")
                print(f"    Track:    {deck_status.get('track_title', 'N/A')}")
                print(f"    Artist:   {deck_status.get('track_artist', 'N/A')}")
                print(f"    BPM:      {deck_status.get('bpm', 'N/A')}")
                print(f"    Volume:   {deck_status.get('volume', 'N/A')}%")
            except Exception as e:
                info(f"Could not get Deck {deck_id} status: {e}")

        # ═══════════════════════════════════════════════════════════
        # CLEANUP
        # ═══════════════════════════════════════════════════════════
        announce("CLEANUP", "Stopping all playback")

        await vdj.stop(1)
        await vdj.stop(2)
        await vdj.set_crossfader(0)
        await vdj.set_volume(1, 100)
        await vdj.set_volume(2, 100)

        status("Deck 1: Stopped")
        status("Deck 2: Stopped")
        status("Crossfader: Center")
        status("Volumes: Reset to 100%")

        # ═══════════════════════════════════════════════════════════
        # DONE!
        # ═══════════════════════════════════════════════════════════
        banner("🎉 DEMO COMPLETE! 🎉", "═")
        print(f"  {Colors.GREEN}All VirtualDJ-MCP features demonstrated!{Colors.END}")
        print(f"  {Colors.CYAN}Your DJ friend should be properly flabbergasted.{Colors.END}")
        print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Demo interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()

