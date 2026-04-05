"""
🦾 SUPERHUMAN DJ DEMO 🦾

This DJ has 16 hands, superluminal reflexes, and zero latency!

Features:
- 8 DECKS running simultaneously (VirtualDJ maximum!)
- Impossibly fast crossfader cuts
- Stem manipulation on all decks at once
- Beat juggling across 8 decks
- Loop rolls on multiple decks
- Volume automation on all channels
- Things no human could EVER do!

Run with: python superhuman_dj_demo.py

WARNING: May cause VirtualDJ to question its existence.
NOTE: Requires VirtualDJ with 8-deck skin enabled!
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
    'R': '\033[91m', 'G': '\033[92m', 'Y': '\033[93m', 'B': '\033[94m',
    'M': '\033[95m', 'C': '\033[96m', 'W': '\033[97m',
    'BOLD': '\033[1m', 'DIM': '\033[2m', 'END': '\033[0m',
    'BG_R': '\033[41m', 'BG_G': '\033[42m', 'BG_B': '\033[44m', 'BG_M': '\033[45m'
}


NUM_DECKS = 8  # VirtualDJ maximum!


def mega_banner():
    print(f"""
{C['BOLD']}{C['M']}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     🦾🦾🦾🦾🦾🦾🦾🦾  SUPERHUMAN DJ  🦾🦾🦾🦾🦾🦾🦾🦾             ║
║                                                                      ║
║        ████████╗██╗  ██╗███████╗    ██████╗      ██╗                 ║
║        ╚══██╔══╝██║  ██║██╔════╝    ██╔══██╗     ██║                 ║
║           ██║   ███████║█████╗      ██║  ██║     ██║                 ║
║           ██║   ██╔══██║██╔══╝      ██║  ██║██   ██║                 ║
║           ██║   ██║  ██║███████╗    ██████╔╝╚█████╔╝                 ║
║           ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═════╝  ╚════╝                  ║
║                                                                      ║
║     8 DECKS • 16 HANDS • SUPERLUMINAL SPEED • ZERO LATENCY          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{C['END']}""")


def section(title: str, icon: str = "⚡"):
    """Print section header."""
    print(f"\n{C['BOLD']}{C['Y']}{'━' * 70}{C['END']}")
    print(f"{C['BOLD']}{C['C']}{icon} {title} {icon}{C['END']}")
    print(f"{C['BOLD']}{C['Y']}{'━' * 70}{C['END']}\n")


def deck_status(decks: list[int], action: str):
    """Print deck status bar."""
    bar = ""
    for d in range(1, NUM_DECKS + 1):
        if d in decks:
            bar += f"{C['BG_G']}D{d}{C['END']}"
        else:
            bar += f"{C['DIM']}D{d}{C['END']}"
    print(f"  [{bar}] {C['G']}{action}{C['END']}")


async def parallel_play(vdj: VirtualDJClient, decks: list[int]):
    """Play multiple decks simultaneously."""
    await asyncio.gather(*[vdj.play(d) for d in decks])


async def parallel_stop(vdj: VirtualDJClient, decks: list[int]):
    """Stop multiple decks simultaneously."""
    await asyncio.gather(*[vdj.stop(d) for d in decks])


async def parallel_volume(vdj: VirtualDJClient, volumes: dict):
    """Set volumes on multiple decks at once."""
    await asyncio.gather(*[vdj.set_volume(d, v) for d, v in volumes.items()])


async def quad_crossfader_massacre(vdj: VirtualDJClient):
    """Impossibly fast crossfader cuts across all positions."""
    section("QUAD CROSSFADER MASSACRE", "🔀")

    positions = [-100, -50, 0, 50, 100]
    print("  ", end="")

    for _ in range(30):  # 30 cuts in rapid succession
        pos = random.choice(positions)
        await vdj.set_crossfader(pos)

        if pos == -100:
            print(f"{C['R']}◄{C['END']}", end="", flush=True)
        elif pos == 100:
            print(f"{C['B']}►{C['END']}", end="", flush=True)
        else:
            print(f"{C['Y']}●{C['END']}", end="", flush=True)

        await asyncio.sleep(0.04)  # 25 cuts per second!

    print(f" {C['G']}SHREDDED!{C['END']}")


async def stem_chaos(vdj: VirtualDJClient):
    """Manipulate stems on all 8 decks simultaneously."""
    section("8-DECK STEM MANIPULATION CHAOS", "🎚")

    stems = ["vocal", "bass", "drums"]

    # Kill vocals on odd decks, bass on even decks
    print(f"  {C['M']}Killing vocals on D1,3,5,7 + bass on D2,4,6,8...{C['END']}")
    await asyncio.gather(
        *[vdj.send_command(f"deck {d} stem_kill 'vocal'") for d in [1,3,5,7]],
        *[vdj.send_command(f"deck {d} stem_kill 'bass'") for d in [2,4,6,8]]
    )
    deck_status(list(range(1, NUM_DECKS + 1)), "Stems manipulated!")
    await asyncio.sleep(0.5)

    # Rapid stem toggling across ALL 8 decks
    print(f"\n  {C['Y']}Rapid stem toggle storm (8 decks!)...{C['END']}")
    print("  ", end="")

    for _ in range(40):  # More chaos with 8 decks!
        deck = random.randint(1, NUM_DECKS)
        stem = random.choice(stems)
        action = random.choice(["kill", "unkill"])
        await vdj.send_command(f"deck {deck} stem_{action} '{stem}'")
        print(f"{C['C']}⚡{C['END']}", end="", flush=True)
        await asyncio.sleep(0.03)

    print(f" {C['G']}STEM STORM!{C['END']}")

    # Restore all 8 decks
    for d in range(1, NUM_DECKS + 1):
        for s in stems:
            await vdj.send_command(f"deck {d} stem_unkill '{s}'")


async def beat_juggle_8_decks(vdj: VirtualDJClient):
    """Beat juggling across all 8 decks - IMPOSSIBLE for humans!"""
    section("8-DECK BEAT JUGGLE", "🥁")

    print(f"  {C['Y']}Sequencing beats across ALL 8 decks...{C['END']}\n")

    # Pattern sweeps through all 8 decks
    pattern = [1,2,3,4,5,6,7,8,7,6,5,4,3,2,1,2,3,4,5,6,7,8,8,7,6,5,4,3,2,1]

    for deck in pattern:
        # Crossfader position spread across 8 decks
        positions = {i: int(-100 + (i-1) * (200/7)) for i in range(1, 9)}
        await vdj.set_crossfader(positions[deck])

        # Visual for 8 decks
        bars = ["░" for _ in range(8)]
        bars[deck - 1] = f"{C['G']}█{C['END']}"
        visual = "|".join(bars)
        print(f"\r  [{visual}] D{deck}", end="", flush=True)

        await asyncio.sleep(0.06)

    print(f"\n\n  {C['G']}8-DECK JUGGLED!{C['END']}")


async def volume_wave(vdj: VirtualDJClient):
    """Create a wave pattern across all 8 deck volumes."""
    section("8-DECK VOLUME WAVE", "🌊")

    print(f"  {C['C']}Creating volume wave across 8 decks...{C['END']}\n")

    import math

    for frame in range(50):
        volumes = {}
        for deck in range(1, NUM_DECKS + 1):
            # Sine wave offset by deck number - creates rolling wave
            phase = (frame / 8) + (deck * 0.4)
            vol = int(50 + 50 * math.sin(phase * math.pi))
            volumes[deck] = vol

        await parallel_volume(vdj, volumes)

        # Compact visual for 8 decks
        bars = []
        for d in range(1, NUM_DECKS + 1):
            filled = volumes[d] // 20  # 5 chars per bar
            bar = "█" * filled + "░" * (5 - filled)
            bars.append(bar)

        print(f"\r  {C['C']}[{'|'.join(bars)}]{C['END']}", end="", flush=True)
        await asyncio.sleep(0.04)

    print(f"\n\n  {C['G']}8-DECK WAVE COMPLETE!{C['END']}")

    # Reset volumes
    await parallel_volume(vdj, {d: 80 for d in range(1, NUM_DECKS + 1)})


async def loop_roll_madness(vdj: VirtualDJClient):
    """Loop rolls on all 8 decks with different lengths - polyrhythmic chaos!"""
    section("8-DECK LOOP ROLL MADNESS", "🔁")

    print(f"  {C['M']}Triggering polyrhythmic loop rolls on ALL 8 decks...{C['END']}")

    # Different loop lengths per deck - creates polyrhythmic madness
    loops = {1: 0.5, 2: 0.25, 3: 1, 4: 0.125, 5: 2, 6: 0.0625, 7: 0.75, 8: 0.375}

    # Start all loop rolls SIMULTANEOUSLY
    await asyncio.gather(*[
        vdj.send_command(f"deck {d} loop_roll {l}")
        for d, l in loops.items()
    ])

    print("  D1:1/2 D2:1/4 D3:1 D4:1/8 D5:2 D6:1/16 D7:3/4 D8:3/8")

    for i in range(25):
        loops_display = "🔁" * ((i % 8) + 1)
        print(f"\r  {loops_display}{'  ' * (7 - (i % 8))}", end="", flush=True)
        await asyncio.sleep(0.08)

    # Exit all loops
    await asyncio.gather(*[
        vdj.send_command(f"deck {d} loop_exit")
        for d in range(1, NUM_DECKS + 1)
    ])

    print(f"\n  {C['G']}ALL 8 LOOPS RELEASED!{C['END']}")


async def impossible_scratch(vdj: VirtualDJClient):
    """Scratch patterns no human could execute - 8 decks simultaneously!"""
    section("IMPOSSIBLE 8-DECK SCRATCH PATTERN", "💿")

    print(f"  {C['R']}Executing physically impossible 8-deck scratch sequence...{C['END']}\n")
    print("  ", end="")

    # Simultaneous operations on ALL 8 decks!
    for _ in range(20):
        # All 8 decks doing different things AT THE SAME TIME
        await asyncio.gather(
            vdj.set_crossfader(random.randint(-100, 100)),
            *[vdj.set_volume(d, random.randint(0, 100)) for d in range(1, NUM_DECKS + 1)]
        )

        # Visual chaos
        chars = "◄►▲▼●○◆◇★☆⚡✦"
        print(f"{C['M']}{random.choice(chars)}{C['END']}", end="", flush=True)
        await asyncio.sleep(0.025)

    print(f" {C['G']}8-DECK IMPOSSIBLE ACHIEVED!{C['END']}")


async def grand_finale(vdj: VirtualDJClient):
    """The ultimate finale - ALL 8 DECKS at once!"""
    section("🔥 GRAND FINALE - 8 DECKS MAXIMUM CHAOS 🔥", "💥")

    print(f"  {C['BOLD']}{C['R']}ALL 8 SYSTEMS ENGAGED!{C['END']}\n")

    # Build up across all 8 decks
    print(f"  {C['Y']}Building on 8 decks...{C['END']}", end="", flush=True)
    for i in range(10):
        await parallel_volume(vdj, {d: i * 10 for d in range(1, NUM_DECKS + 1)})
        print("▓", end="", flush=True)
        await asyncio.sleep(0.08)

    print(f"\n  {C['R']}TENSION ON ALL DECKS...{C['END']}", end="", flush=True)
    for _ in range(15):
        await vdj.set_crossfader(random.randint(-100, 100))
        print("×", end="", flush=True)
        await asyncio.sleep(0.04)

    # THE DROP
    print(f"""

  {C['BOLD']}{C['BG_R']}                                                         {C['END']}
  {C['BOLD']}{C['BG_R']}     💥💥💥💥  8 - D E C K   D R O P  💥💥💥💥         {C['END']}
  {C['BOLD']}{C['BG_R']}                                                         {C['END']}
""")

    # Maximum chaos - all 8 decks at full volume
    await parallel_volume(vdj, {d: 100 for d in range(1, NUM_DECKS + 1)})
    await vdj.set_crossfader(0)

    # Chaos across all 8 decks
    for _ in range(30):
        await asyncio.gather(
            vdj.set_crossfader(random.randint(-100, 100)),
            vdj.send_command(f"deck {random.randint(1, NUM_DECKS)} stem_kill '{random.choice(['vocal','bass','drums'])}'"),
        )
        await asyncio.sleep(0.03)

    # Restore all 8 decks
    for d in range(1, NUM_DECKS + 1):
        await vdj.send_command(f"deck {d} stem_unkill 'vocal'")
        await vdj.send_command(f"deck {d} stem_unkill 'bass'")
        await vdj.send_command(f"deck {d} stem_unkill 'drums'")


async def main():
    mega_banner()

    print(f"""
  {C['C']}This demo requires VirtualDJ with 8-DECK SKIN enabled!
  The DJ performs moves that would require 16 hands
  and reaction times faster than human neurons.
  
  NO HUMAN CAN DO THIS. Only AI can mix 8 decks at once.{C['END']}
    """)

    input(f"  {C['Y']}Press ENTER to witness the impossible...{C['END']}")

    fixtures = Path(__file__).parent.parent / "tests" / "fixtures" / "audio"
    tracks = sorted(fixtures.glob("*.mp3"))

    if len(tracks) < 2:
        print(f"  {C['R']}Need test tracks in {fixtures}{C['END']}")
        return

    config = VDJConfig()

    async with VirtualDJClient(config) as vdj:

        if not await vdj.is_running():
            print(f"  {C['R']}Start VirtualDJ first (8-deck mode)!{C['END']}")
            return

        print(f"\n  {C['G']}✅ Connected to VirtualDJ{C['END']}")

        # Load tracks to ALL 8 decks!
        section("LOADING ALL 8 DECKS", "📀")
        for deck in range(1, NUM_DECKS + 1):
            track = tracks[(deck - 1) % len(tracks)]
            print(f"  Loading D{deck}: {track.name}")
            await vdj.load_track(deck, str(track))
            await asyncio.sleep(0.2)

        # Set initial state
        await parallel_volume(vdj, {d: 80 for d in range(1, NUM_DECKS + 1)})
        await vdj.set_crossfader(0)

        # Start ALL 8 decks
        section("ENGAGE ALL 8 DECKS", "▶")
        await parallel_play(vdj, list(range(1, NUM_DECKS + 1)))
        deck_status(list(range(1, NUM_DECKS + 1)), "ALL 8 PLAYING!")
        await asyncio.sleep(1)

        # THE SUPERHUMAN MOVES
        await quad_crossfader_massacre(vdj)
        await asyncio.sleep(0.5)

        await beat_juggle_8_decks(vdj)
        await asyncio.sleep(0.5)

        await stem_chaos(vdj)
        await asyncio.sleep(0.5)

        await volume_wave(vdj)
        await asyncio.sleep(0.5)

        await loop_roll_madness(vdj)
        await asyncio.sleep(0.5)

        await impossible_scratch(vdj)
        await asyncio.sleep(0.5)

        await grand_finale(vdj)
        await asyncio.sleep(1)

        # Cleanup
        section("MISSION COMPLETE", "🏆")
        await parallel_stop(vdj, list(range(1, NUM_DECKS + 1)))
        await vdj.set_crossfader(0)
        await parallel_volume(vdj, {d: 100 for d in range(1, NUM_DECKS + 1)})

        print(f"""
{C['BOLD']}{C['G']}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              🏆 8-DECK SUPERHUMAN DJ COMPLETE 🏆                     ║
║                                                                      ║
║   Moves executed that require:                                       ║
║   • 16 hands (2 per deck!)                                           ║
║   • Sub-millisecond reaction time                                    ║
║   • Simultaneous control of 8 decks                                  ║
║   • Parallel stem manipulation on all decks                          ║
║   • Polyrhythmic loop rolls                                          ║
║   • Violation of several laws of physics                             ║
║                                                                      ║
║   NO HUMAN CAN DO THIS. Only AI can.                                 ║
║                                                                      ║
║   Your DJ friend should be questioning reality right now.            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{C['END']}""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{C['Y']}⚠️ Demo interrupted{C['END']}")
    except Exception as e:
        print(f"\n{C['R']}❌ Error: {e}{C['END']}")
        import traceback
        traceback.print_exc()

