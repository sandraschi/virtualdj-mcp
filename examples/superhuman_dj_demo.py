"""
🦾 SUPERHUMAN DJ DEMO 🦾

This DJ has 8 hands, superluminal reflexes, and zero latency!

Features:
- 4 DECKS running simultaneously
- Impossibly fast crossfader cuts
- Stem manipulation on all decks at once
- Beat juggling across 4 decks
- Loop rolls on multiple decks
- Volume automation on all channels
- Things no human could ever do!

Run with: python superhuman_dj_demo.py

WARNING: May cause VirtualDJ to question its existence.
"""

import asyncio
import sys
import random
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

from virtualdj_mcp.core.vdj_client import VirtualDJClient
from virtualdj_mcp.config import VDJConfig


# ANSI colors
C = {
    'R': '\033[91m', 'G': '\033[92m', 'Y': '\033[93m', 'B': '\033[94m',
    'M': '\033[95m', 'C': '\033[96m', 'W': '\033[97m', 
    'BOLD': '\033[1m', 'DIM': '\033[2m', 'END': '\033[0m',
    'BG_R': '\033[41m', 'BG_G': '\033[42m', 'BG_B': '\033[44m', 'BG_M': '\033[45m'
}


def mega_banner():
    print(f"""
{C['BOLD']}{C['M']}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     🦾🦾🦾🦾  SUPERHUMAN DJ  🦾🦾🦾🦾                               ║
║                                                                      ║
║        ████████╗██╗  ██╗███████╗    ██████╗      ██╗                 ║
║        ╚══██╔══╝██║  ██║██╔════╝    ██╔══██╗     ██║                 ║
║           ██║   ███████║█████╗      ██║  ██║     ██║                 ║
║           ██║   ██╔══██║██╔══╝      ██║  ██║██   ██║                 ║
║           ██║   ██║  ██║███████╗    ██████╔╝╚█████╔╝                 ║
║           ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═════╝  ╚════╝                  ║
║                                                                      ║
║     4 DECKS • 8 HANDS • SUPERLUMINAL SPEED • ZERO LATENCY           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{C['END']}""")


def section(title: str, icon: str = "⚡"):
    """Print section header."""
    print(f"\n{C['BOLD']}{C['Y']}{'━' * 70}{C['END']}")
    print(f"{C['BOLD']}{C['C']}{icon} {title} {icon}{C['END']}")
    print(f"{C['BOLD']}{C['Y']}{'━' * 70}{C['END']}\n")


def deck_status(decks: List[int], action: str):
    """Print deck status bar."""
    bar = ""
    for d in range(1, 5):
        if d in decks:
            bar += f" {C['BG_G']} D{d} {C['END']}"
        else:
            bar += f" {C['DIM']}[D{d}]{C['END']}"
    print(f"  {bar}  {C['G']}{action}{C['END']}")


async def parallel_play(vdj: VirtualDJClient, decks: List[int]):
    """Play multiple decks simultaneously."""
    await asyncio.gather(*[vdj.play(d) for d in decks])


async def parallel_stop(vdj: VirtualDJClient, decks: List[int]):
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
    """Manipulate stems on all 4 decks simultaneously."""
    section("STEM MANIPULATION CHAOS", "🎚")
    
    stems = ["vocal", "bass", "drums"]
    
    # Kill vocals on deck 1 & 3, bass on deck 2 & 4
    print(f"  {C['M']}Killing vocals on D1+D3, bass on D2+D4...{C['END']}")
    await asyncio.gather(
        vdj.send_command("deck 1 stem_kill 'vocal'"),
        vdj.send_command("deck 3 stem_kill 'vocal'"),
        vdj.send_command("deck 2 stem_kill 'bass'"),
        vdj.send_command("deck 4 stem_kill 'bass'")
    )
    deck_status([1, 2, 3, 4], "Stems manipulated!")
    await asyncio.sleep(0.5)
    
    # Rapid stem toggling
    print(f"\n  {C['Y']}Rapid stem toggle storm...{C['END']}")
    print("  ", end="")
    
    for _ in range(20):
        deck = random.randint(1, 4)
        stem = random.choice(stems)
        action = random.choice(["kill", "unkill"])
        await vdj.send_command(f"deck {deck} stem_{action} '{stem}'")
        print(f"{C['C']}⚡{C['END']}", end="", flush=True)
        await asyncio.sleep(0.05)
    
    print(f" {C['G']}STEM STORM!{C['END']}")
    
    # Restore all
    for d in range(1, 5):
        for s in stems:
            await vdj.send_command(f"deck {d} stem_unkill '{s}'")


async def beat_juggle_4_decks(vdj: VirtualDJClient):
    """Beat juggling across all 4 decks."""
    section("4-DECK BEAT JUGGLE", "🥁")
    
    print(f"  {C['Y']}Sequencing beats across all decks...{C['END']}\n")
    
    # Pattern: D1-D2-D3-D4-D3-D2-D1...
    pattern = [1, 2, 3, 4, 3, 2, 1, 2, 3, 4, 4, 3, 2, 1, 1, 2, 3, 4]
    
    for deck in pattern:
        # Crossfader position for each deck
        positions = {1: -100, 2: -33, 3: 33, 4: 100}
        await vdj.set_crossfader(positions[deck])
        
        # Visual
        bars = ["░░░", "░░░", "░░░", "░░░"]
        bars[deck - 1] = f"{C['G']}███{C['END']}"
        print(f"\r  [{bars[0]}|{bars[1]}|{bars[2]}|{bars[3]}] D{deck}", end="", flush=True)
        
        await asyncio.sleep(0.08)
    
    print(f"\n\n  {C['G']}JUGGLED!{C['END']}")


async def volume_wave(vdj: VirtualDJClient):
    """Create a wave pattern across all 4 deck volumes."""
    section("VOLUME WAVE", "🌊")
    
    print(f"  {C['C']}Creating volume wave across 4 decks...{C['END']}\n")
    
    import math
    
    for frame in range(40):
        volumes = {}
        for deck in range(1, 5):
            # Sine wave offset by deck number
            phase = (frame / 10) + (deck * 0.5)
            vol = int(50 + 50 * math.sin(phase * math.pi))
            volumes[deck] = vol
        
        await parallel_volume(vdj, volumes)
        
        # Visual
        bars = []
        for d in range(1, 5):
            filled = volumes[d] // 10
            bar = "█" * filled + "░" * (10 - filled)
            bars.append(f"D{d}[{bar}]")
        
        print(f"\r  {' '.join(bars)}", end="", flush=True)
        await asyncio.sleep(0.05)
    
    print(f"\n\n  {C['G']}WAVE COMPLETE!{C['END']}")
    
    # Reset volumes
    await parallel_volume(vdj, {1: 80, 2: 80, 3: 80, 4: 80})


async def loop_roll_madness(vdj: VirtualDJClient):
    """Loop rolls on all decks with different lengths."""
    section("LOOP ROLL MADNESS", "🔁")
    
    print(f"  {C['M']}Triggering loop rolls on all decks...{C['END']}")
    
    # Different loop lengths per deck
    loops = {1: 0.5, 2: 0.25, 3: 1, 4: 0.125}
    
    # Start all loop rolls
    await asyncio.gather(*[
        vdj.send_command(f"deck {d} loop_roll {l}") 
        for d, l in loops.items()
    ])
    
    print(f"  D1: 1/2 beat | D2: 1/4 beat | D3: 1 beat | D4: 1/8 beat")
    
    for i in range(20):
        print(f"\r  {'🔁' * ((i % 4) + 1)}{'  ' * (3 - (i % 4))}", end="", flush=True)
        await asyncio.sleep(0.1)
    
    # Exit all loops
    await asyncio.gather(*[
        vdj.send_command(f"deck {d} loop_exit") 
        for d in range(1, 5)
    ])
    
    print(f"\n  {C['G']}LOOPS RELEASED!{C['END']}")


async def impossible_scratch(vdj: VirtualDJClient):
    """Scratch patterns no human could execute."""
    section("IMPOSSIBLE SCRATCH PATTERN", "💿")
    
    print(f"  {C['R']}Executing physically impossible scratch sequence...{C['END']}\n")
    print("  ", end="")
    
    # Simultaneous operations on all decks
    for _ in range(15):
        # All 4 decks doing different things AT THE SAME TIME
        await asyncio.gather(
            vdj.set_crossfader(random.randint(-100, 100)),
            vdj.set_volume(1, random.randint(0, 100)),
            vdj.set_volume(2, random.randint(0, 100)),
            vdj.set_volume(3, random.randint(0, 100)),
            vdj.set_volume(4, random.randint(0, 100)),
        )
        
        # Visual chaos
        chars = "◄►▲▼●○◆◇★☆"
        print(f"{C['M']}{random.choice(chars)}{C['END']}", end="", flush=True)
        await asyncio.sleep(0.03)
    
    print(f" {C['G']}IMPOSSIBLE ACHIEVED!{C['END']}")


async def grand_finale(vdj: VirtualDJClient):
    """The ultimate finale - everything at once!"""
    section("🔥 GRAND FINALE - EVERYTHING AT ONCE 🔥", "💥")
    
    print(f"  {C['BOLD']}{C['R']}ALL SYSTEMS ENGAGED!{C['END']}\n")
    
    # Build up
    print(f"  {C['Y']}Building...{C['END']}", end="", flush=True)
    for i in range(10):
        await parallel_volume(vdj, {d: i * 10 for d in range(1, 5)})
        print("▓", end="", flush=True)
        await asyncio.sleep(0.1)
    
    print(f"\n  {C['R']}TENSION...{C['END']}", end="", flush=True)
    for _ in range(10):
        await vdj.set_crossfader(random.randint(-100, 100))
        print("×", end="", flush=True)
        await asyncio.sleep(0.05)
    
    # THE DROP
    print(f"""

  {C['BOLD']}{C['BG_R']}                                                    {C['END']}
  {C['BOLD']}{C['BG_R']}     💥💥💥  T H E   D R O P  💥💥💥              {C['END']}
  {C['BOLD']}{C['BG_R']}                                                    {C['END']}
""")
    
    # Maximum chaos for 2 seconds
    await parallel_volume(vdj, {1: 100, 2: 100, 3: 100, 4: 100})
    await vdj.set_crossfader(0)
    
    for _ in range(20):
        await asyncio.gather(
            vdj.set_crossfader(random.randint(-100, 100)),
            vdj.send_command(f"deck {random.randint(1,4)} stem_kill '{random.choice(['vocal','bass','drums'])}'"),
        )
        await asyncio.sleep(0.05)
    
    # Restore
    for d in range(1, 5):
        await vdj.send_command(f"deck {d} stem_unkill 'vocal'")
        await vdj.send_command(f"deck {d} stem_unkill 'bass'")
        await vdj.send_command(f"deck {d} stem_unkill 'drums'")


async def main():
    mega_banner()
    
    print(f"""
  {C['C']}This demo requires VirtualDJ with 4 decks enabled.
  The DJ performs moves that would require 8 hands
  and reaction times faster than human neurons.{C['END']}
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
            print(f"  {C['R']}Start VirtualDJ first (4-deck mode)!{C['END']}")
            return
        
        print(f"\n  {C['G']}✅ Connected to VirtualDJ{C['END']}")
        
        # Load tracks to all 4 decks
        section("LOADING 4 DECKS", "📀")
        for i, deck in enumerate(range(1, 5)):
            track = tracks[i % len(tracks)]
            print(f"  Loading D{deck}: {track.name}")
            await vdj.load_track(deck, str(track))
            await asyncio.sleep(0.3)
        
        # Set initial state
        await parallel_volume(vdj, {1: 80, 2: 80, 3: 80, 4: 80})
        await vdj.set_crossfader(0)
        
        # Start all decks
        section("ENGAGE ALL DECKS", "▶")
        await parallel_play(vdj, [1, 2, 3, 4])
        deck_status([1, 2, 3, 4], "ALL PLAYING!")
        await asyncio.sleep(1)
        
        # THE SUPERHUMAN MOVES
        await quad_crossfader_massacre(vdj)
        await asyncio.sleep(0.5)
        
        await beat_juggle_4_decks(vdj)
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
        await parallel_stop(vdj, [1, 2, 3, 4])
        await vdj.set_crossfader(0)
        await parallel_volume(vdj, {1: 100, 2: 100, 3: 100, 4: 100})
        
        print(f"""
{C['BOLD']}{C['G']}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                    🏆 SUPERHUMAN DJ COMPLETE 🏆                      ║
║                                                                      ║
║   Moves executed that require:                                       ║
║   • 8 hands                                                          ║
║   • Sub-millisecond reaction time                                    ║
║   • Simultaneous control of 4 decks                                  ║
║   • Parallel stem manipulation                                       ║
║   • Violation of several laws of physics                             ║
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

