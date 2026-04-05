"""
DJ Tricks Demo - Fast artistic DJ moves!

Demonstrates rapid-fire DJ techniques:
- Crossfader cuts (transformer scratch)
- Beat juggling
- Volume kills
- Spinbacks
- Stutter effects
- Drop builds

Run with: python dj_tricks_demo.py
"""

import asyncio
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from virtualdj_mcp.config import VDJConfig
from virtualdj_mcp.core.vdj_client import VirtualDJClient

# ANSI colors
C = {
    'R': '\033[91m', 'G': '\033[92m', 'Y': '\033[93m',
    'B': '\033[94m', 'M': '\033[95m', 'C': '\033[96m',
    'W': '\033[97m', 'BOLD': '\033[1m', 'END': '\033[0m'
}


def flash(text: str, color: str = 'Y'):
    """Print flashy text."""
    print(f"{C['BOLD']}{C[color]}★ {text} ★{C['END']}")


async def transformer_scratch(vdj: VirtualDJClient, deck: int, cuts: int = 8):
    """
    Transformer scratch - rapid crossfader cuts
    Classic hip-hop technique!
    """
    flash("TRANSFORMER SCRATCH!", 'M')
    print("  ", end="")

    pos = -100 if deck == 1 else 100
    for i in range(cuts):
        # Cut in
        await vdj.set_crossfader(pos)
        print("▓", end="", flush=True)
        await asyncio.sleep(0.08)
        # Cut out
        await vdj.set_crossfader(0)
        print("░", end="", flush=True)
        await asyncio.sleep(0.08)

    await vdj.set_crossfader(pos)
    print(" CHKA-CHKA-CHKA!")


async def crossfader_baby_scratch(vdj: VirtualDJClient, reps: int = 4):
    """
    Baby scratch pattern with crossfader
    Back and forth real quick!
    """
    flash("BABY SCRATCH!", 'C')
    print("  ", end="")

    for _ in range(reps):
        # Quick left-right-left
        for pos in [-100, 100, -100, 0]:
            await vdj.set_crossfader(pos)
            print("◄" if pos < 0 else ("►" if pos > 0 else "●"), end="", flush=True)
            await asyncio.sleep(0.1)
    print(" WIKKI-WIKKI!")


async def volume_pump(vdj: VirtualDJClient, deck: int, pumps: int = 6):
    """
    Volume pumping - EDM style buildup
    """
    flash("VOLUME PUMP!", 'G')
    print("  ", end="")

    for i in range(pumps):
        # Pump up
        await vdj.set_volume(deck, 100)
        print("▲", end="", flush=True)
        await asyncio.sleep(0.15)
        # Drop down
        await vdj.set_volume(deck, 30)
        print("▼", end="", flush=True)
        await asyncio.sleep(0.15)

    await vdj.set_volume(deck, 100)
    print(" UNTZ-UNTZ-UNTZ!")


async def stutter_cut(vdj: VirtualDJClient, deck: int, stutters: int = 12):
    """
    Stutter effect - rapid play/pause
    """
    flash("STUTTER CUT!", 'R')
    print("  ", end="")

    for i in range(stutters):
        await vdj.play(deck)
        print("►", end="", flush=True)
        await asyncio.sleep(0.05)
        await vdj.pause(deck)
        print("║", end="", flush=True)
        await asyncio.sleep(0.05)

    await vdj.play(deck)
    print(" T-T-T-T-T!")


async def echo_fade(vdj: VirtualDJClient, deck: int):
    """
    Simulated echo fade out
    """
    flash("ECHO FADE!", 'B')
    print("  ", end="")

    volumes = [80, 60, 45, 30, 20, 10, 5, 0]
    for vol in volumes:
        await vdj.set_volume(deck, vol)
        bar = "█" * (vol // 10)
        print(f"[{bar.ljust(10)}]", end="", flush=True)
        await asyncio.sleep(0.2)
        print("\r  ", end="")

    print("[          ] ...fade out")
    await vdj.set_volume(deck, 80)


async def ping_pong(vdj: VirtualDJClient, bounces: int = 8):
    """
    Ping pong between decks
    """
    flash("PING PONG!", 'Y')
    print("  ", end="")

    for i in range(bounces):
        # Deck 1
        await vdj.set_crossfader(-100)
        print("◄──", end="", flush=True)
        await asyncio.sleep(0.15)
        # Deck 2
        await vdj.set_crossfader(100)
        print("──►", end="", flush=True)
        await asyncio.sleep(0.15)

    await vdj.set_crossfader(0)
    print(" BOING BOING!")


async def drop_build(vdj: VirtualDJClient, deck: int):
    """
    Classic EDM drop buildup
    """
    flash("DROP INCOMING!", 'R')

    # Volume swell
    print("  Building...", end="", flush=True)
    for vol in range(20, 101, 10):
        await vdj.set_volume(deck, vol)
        print("▓", end="", flush=True)
        await asyncio.sleep(0.1)

    # Quick cuts
    print("\n  Tension...", end="", flush=True)
    for _ in range(8):
        await vdj.set_crossfader(random.choice([-100, 0, 100]))
        print("×", end="", flush=True)
        await asyncio.sleep(0.08)

    # THE DROP
    print(f"\n  {C['BOLD']}{C['R']}💥 D R O P 💥{C['END']}")
    await vdj.set_crossfader(-100)
    await vdj.set_volume(deck, 100)
    await asyncio.sleep(0.5)


async def crab_scratch(vdj: VirtualDJClient, deck: int):
    """
    Crab scratch - super fast crossfader clicks
    """
    flash("CRAB SCRATCH!", 'M')
    print("  ", end="")

    pos = -100 if deck == 1 else 100
    # Ultra-fast cuts
    for _ in range(16):
        await vdj.set_crossfader(pos)
        await asyncio.sleep(0.03)
        await vdj.set_crossfader(0)
        await asyncio.sleep(0.03)
        print(".", end="", flush=True)

    await vdj.set_crossfader(pos)
    print(" 🦀 SKRRT!")


async def main():
    print(f"""
{C['BOLD']}{C['M']}╔══════════════════════════════════════════════════════════╗
║            🎧 DJ TRICKS DEMO 🎧                          ║
║           Fast Artistic Moves!                            ║
╚══════════════════════════════════════════════════════════╝{C['END']}
""")

    fixtures = Path(__file__).parent.parent / "tests" / "fixtures" / "audio"
    tracks = sorted(fixtures.glob("*.mp3"))

    if len(tracks) < 2:
        print("❌ Need test tracks!")
        return

    config = VDJConfig()

    async with VirtualDJClient(config) as vdj:

        if not await vdj.is_running():
            print("❌ Start VirtualDJ first!")
            return

        print(f"{C['G']}✅ Connected!{C['END']}\n")

        # Load tracks
        print(f"{C['C']}Loading tracks...{C['END']}")
        await vdj.load_track(1, str(tracks[0]))
        await vdj.load_track(2, str(tracks[1] if len(tracks) > 1 else tracks[0]))
        await asyncio.sleep(1)

        # Set up
        await vdj.set_volume(1, 80)
        await vdj.set_volume(2, 80)
        await vdj.play(1)
        await vdj.play(2)
        await asyncio.sleep(0.5)

        print(f"\n{C['Y']}🎵 LET'S GO! 🎵{C['END']}\n")
        await asyncio.sleep(1)

        # THE TRICKS!
        await transformer_scratch(vdj, 1, cuts=10)
        await asyncio.sleep(1)

        await crossfader_baby_scratch(vdj, reps=3)
        await asyncio.sleep(1)

        await ping_pong(vdj, bounces=6)
        await asyncio.sleep(1)

        await volume_pump(vdj, 1, pumps=8)
        await asyncio.sleep(1)

        await stutter_cut(vdj, 1, stutters=10)
        await asyncio.sleep(1)

        await crab_scratch(vdj, 1)
        await asyncio.sleep(1)

        await echo_fade(vdj, 1)
        await asyncio.sleep(1)

        await drop_build(vdj, 1)
        await asyncio.sleep(2)

        # Finale
        print(f"""
{C['BOLD']}{C['G']}╔══════════════════════════════════════════════════════════╗
║                   🎉 TRICKS COMPLETE! 🎉                  ║
║                                                           ║
║  Techniques demonstrated:                                  ║
║  • Transformer Scratch    • Baby Scratch                  ║
║  • Ping Pong             • Volume Pump                    ║
║  • Stutter Cut           • Crab Scratch                   ║
║  • Echo Fade             • Drop Build                     ║
║                                                           ║
║              Your DJ friend is SHOOK! 🔥                  ║
╚══════════════════════════════════════════════════════════╝{C['END']}
""")

        # Cleanup
        await vdj.stop(1)
        await vdj.stop(2)
        await vdj.set_crossfader(0)
        await vdj.set_volume(1, 100)
        await vdj.set_volume(2, 100)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{C['Y']}⚠️ Interrupted{C['END']}")
    except Exception as e:
        print(f"\n{C['R']}❌ Error: {e}{C['END']}")

