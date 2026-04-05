"""
METAL KILLS JINGLE - The Ultimate Holiday Massacre Demo

Load your cheerful holiday track on Deck 1.
Load your heaviest metal on Deck 2.
Watch the metal DESTROY the jingle!

This demo showcases dramatic crossfading, stem manipulation,
and the art of the hostile takeover mix.

Usage:
    python metal_kills_jingle_demo.py
    
    Or with custom tracks:
    python metal_kills_jingle_demo.py "path/to/jingle.mp3" "path/to/metal.mp3"
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from virtualdj_mcp.core.vdj_client import VDJConfig, VirtualDJClient

# ANSI colors
C = {
    'R': '\033[91m', 'G': '\033[92m', 'Y': '\033[93m',
    'B': '\033[94m', 'M': '\033[95m', 'C': '\033[96m',
    'BOLD': '\033[1m', 'DIM': '\033[2m', 'END': '\033[0m',
    'BG_R': '\033[41m', 'BG_G': '\033[42m'
}


def banner():
    print(f"""
{C['BOLD']}{C['R']}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     🎄 + 🤘 = 💀                                                     ║
║                                                                      ║
║         M E T A L   K I L L S   J I N G L E                         ║
║                                                                      ║
║     Deck 1: Cheerful Holiday Tune                                    ║
║     Deck 2: BRUTAL METAL                                             ║
║                                                                      ║
║     The holiday spirit will be DESTROYED.                            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{C['END']}""")


def phase(name: str, emoji: str = ""):
    print(f"\n{C['BOLD']}{C['M']}{'='*60}")
    print(f"  {emoji} {name} {emoji}")
    print(f"{'='*60}{C['END']}\n")


async def the_massacre(vdj: VirtualDJClient):
    """The main event - metal destroys jingle."""

    # PHASE 1: Innocent Beginning
    phase("PHASE 1: INNOCENT BEGINNING", "🎄")

    print(f"  {C['G']}Deck 1 plays... so cheerful... so innocent...{C['END']}")
    await vdj.set_volume(1, 100)
    await vdj.set_volume(2, 0)
    await vdj.set_crossfader(-100)  # Full left (deck 1)
    await vdj.play(1)

    # Let jingle play for a bit
    for i in range(10):
        print(f"  {C['G']}🎄 {'*' * (i+1)} La la la... {'*' * (10-i)} 🎄{C['END']}", end='\r')
        await asyncio.sleep(0.5)
    print()

    # PHASE 2: Ominous Rumble
    phase("PHASE 2: THE RUMBLE BEGINS", "⚡")

    print(f"  {C['Y']}Something stirs in the darkness...{C['END']}")
    await vdj.play(2)  # Start metal (silent)

    # Slowly bring in metal bass rumble
    for vol in range(0, 30, 5):
        await vdj.set_volume(2, vol)
        print(f"  {C['Y']}Metal volume: {'█' * (vol//5)}{'░' * (6 - vol//5)} {vol}%{C['END']}", end='\r')
        await asyncio.sleep(0.3)
    print()

    # PHASE 3: The Invasion
    phase("PHASE 3: METAL INVASION", "🤘")

    print(f"  {C['R']}The metal is coming... crossfader moving...{C['END']}")

    # Dramatic crossfade with volume interplay
    for pos in range(-100, 0, 10):
        await vdj.set_crossfader(pos)
        # Jingle gets weaker, metal gets stronger
        jingle_vol = 100 + pos  # 100 -> 0
        metal_vol = 30 + abs(pos) * 0.7  # 30 -> 100
        await vdj.set_volume(1, int(jingle_vol))
        await vdj.set_volume(2, int(metal_vol))

        jingle_bar = '█' * (jingle_vol // 10)
        metal_bar = '█' * (int(metal_vol) // 10)
        print(f"  🎄[{jingle_bar:10}] vs [{metal_bar:10}]🤘", end='\r')
        await asyncio.sleep(0.15)
    print()

    # PHASE 4: The Kill
    phase("PHASE 4: THE KILL", "💀")

    print(f"  {C['BOLD']}{C['R']}EXECUTING THE JINGLE...{C['END']}")

    # Kill jingle's vocals first (the singing!)
    print(f"  {C['R']}Killing jingle vocals...{C['END']}")
    await vdj.send_command("deck 1 stem_kill 'vocal'")
    await asyncio.sleep(0.5)

    # Kill jingle's melody
    print(f"  {C['R']}Killing jingle melody...{C['END']}")
    await vdj.send_command("deck 1 stem_kill 'instrument'")
    await asyncio.sleep(0.5)

    # Rapid crossfader cuts - metal stabbing through
    print(f"  {C['R']}STAB STAB STAB...{C['END']}")
    for _ in range(15):
        await vdj.set_crossfader(100)  # METAL!
        await asyncio.sleep(0.05)
        await vdj.set_crossfader(-50)  # dying jingle
        await asyncio.sleep(0.05)
        print(f"{C['R']}🗡️{C['END']}", end='', flush=True)
    print()

    # PHASE 5: Total Annihilation
    phase("PHASE 5: TOTAL ANNIHILATION", "🔥")

    print(f"  {C['BOLD']}{C['BG_R']}                                    {C['END']}")
    print(f"  {C['BOLD']}{C['BG_R']}   💀 JINGLE HAS BEEN DESTROYED 💀  {C['END']}")
    print(f"  {C['BOLD']}{C['BG_R']}                                    {C['END']}")

    # Full metal takeover
    await vdj.set_crossfader(100)
    await vdj.set_volume(1, 0)
    await vdj.set_volume(2, 100)

    # Stop the dead jingle
    await vdj.stop(1)

    # Victory lap - metal plays alone
    print(f"\n  {C['R']}🤘 METAL REIGNS SUPREME 🤘{C['END']}")

    for i in range(10):
        chars = "🔥💀🤘⚡"
        line = ' '.join([chars[j % 4] for j in range(i + 1)])
        print(f"  {line}", end='\r')
        await asyncio.sleep(0.3)
    print()

    await asyncio.sleep(2)

    # Cleanup
    print(f"\n  {C['DIM']}Stopping playback...{C['END']}")
    await vdj.stop(2)
    await vdj.set_crossfader(0)
    await vdj.set_volume(1, 100)
    await vdj.set_volume(2, 100)

    # Restore stems
    await vdj.send_command("deck 1 stem_unkill 'vocal'")
    await vdj.send_command("deck 1 stem_unkill 'instrument'")


async def main():
    banner()

    # Check for custom track paths
    if len(sys.argv) >= 3:
        jingle_path = sys.argv[1]
        metal_path = sys.argv[2]
        print(f"  {C['C']}Custom tracks:{C['END']}")
        print(f"    Deck 1 (Jingle): {jingle_path}")
        print(f"    Deck 2 (Metal):  {metal_path}")
    else:
        # Use test fixtures
        fixtures = Path(__file__).parent.parent / "tests" / "fixtures" / "audio"
        tracks = sorted(fixtures.glob("*.mp3"))
        if len(tracks) < 2:
            print(f"  {C['R']}Need 2 MP3 files!{C['END']}")
            print(f"  Usage: python {sys.argv[0]} jingle.mp3 metal.mp3")
            return
        jingle_path = str(tracks[0])
        metal_path = str(tracks[1])
        print(f"  {C['Y']}Using test fixtures (load your own for full effect!):{C['END']}")
        print(f"    Deck 1: {Path(jingle_path).name}")
        print(f"    Deck 2: {Path(metal_path).name}")

    print(f"\n  {C['Y']}Pro tip: Load actual jingle/metal tracks for maximum carnage!{C['END']}")
    input(f"\n  {C['C']}Press ENTER to begin the massacre...{C['END']}")

    config = VDJConfig()

    async with VirtualDJClient(config) as vdj:
        if not await vdj.is_running():
            print(f"  {C['R']}Start VirtualDJ first!{C['END']}")
            return

        print(f"\n  {C['G']}Connected to VirtualDJ{C['END']}")

        # Load tracks
        print("\n  Loading tracks...")
        await vdj.load_track(1, jingle_path)
        print(f"  {C['G']}Deck 1: Jingle loaded{C['END']}")
        await asyncio.sleep(0.5)

        await vdj.load_track(2, metal_path)
        print(f"  {C['R']}Deck 2: METAL loaded{C['END']}")
        await asyncio.sleep(0.5)

        # THE MASSACRE
        await the_massacre(vdj)

        print(f"""
{C['BOLD']}{C['G']}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                    🤘 MASSACRE COMPLETE 🤘                           ║
║                                                                      ║
║   The holiday spirit has been vanquished.                            ║
║   Metal prevails. As it should.                                      ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{C['END']}""")


if __name__ == "__main__":
    asyncio.run(main())

