#!/usr/bin/env python3
"""
VirtualDJ HTTP API Test Script

Tests the HTTP Network Control Plugin connection and VDJScript commands.
Requires VirtualDJ to be running with Network Control Plugin enabled.
"""

import asyncio
import sys
from pathlib import Path

import httpx

# Configuration
VDJ_HTTP_HOST = "127.0.0.1"
VDJ_HTTP_PORT = 80
BASE_URL = f"http://{VDJ_HTTP_HOST}:{VDJ_HTTP_PORT}"


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def ok(self, msg: str):
        self.passed += 1
        print(f"  ✅ {msg}")

    def fail(self, msg: str):
        self.failed += 1
        print(f"  ❌ {msg}")

    def skip(self, msg: str):
        self.skipped += 1
        print(f"  [skip]️  {msg}")

    def summary(self):
        total = self.passed + self.failed + self.skipped
        print(f"\n{'='*50}")
        print(f"Results: {self.passed}/{total} passed, {self.failed} failed, {self.skipped} skipped")
        return self.failed == 0


async def execute(client: httpx.AsyncClient, script: str) -> tuple[bool, str]:
    """Execute VDJScript command"""
    try:
        response = await client.post(
            f"{BASE_URL}/execute",
            content=script,
            headers={"Content-Type": "text/plain"},
            timeout=10.0
        )
        result = response.text.strip()
        success = response.status_code == 200 and result.lower() == "true"
        return success, result
    except Exception as e:
        return False, str(e)


async def query(client: httpx.AsyncClient, script: str) -> tuple[bool, str]:
    """Query VirtualDJ for information"""
    try:
        response = await client.post(
            f"{BASE_URL}/query",
            content=script,
            headers={"Content-Type": "text/plain"},
            timeout=10.0
        )
        return response.status_code == 200, response.text.strip()
    except Exception as e:
        return False, str(e)


async def test_connection(result: TestResult):
    """Test basic HTTP connection to Network Control Plugin"""
    print("\n1. Testing HTTP Connection")
    print("-" * 40)

    async with httpx.AsyncClient() as client:
        # Test basic connectivity using a query (more reliable than execute)
        try:
            success, res = await query(client, "get_decks")
            if success:
                result.ok(f"Connected to VirtualDJ at {BASE_URL} (decks: {res})")
                return True
            else:
                result.fail(f"Connection failed: {res}")
                return False
        except httpx.ConnectError:
            result.fail(f"Cannot connect to {BASE_URL} - Is VirtualDJ running with Network Control Plugin?")
            return False
        except Exception as e:
            result.fail(f"Connection error: {e}")
            return False


async def test_deck_queries(result: TestResult):
    """Test deck status queries"""
    print("\n2. Testing Deck Queries")
    print("-" * 40)

    async with httpx.AsyncClient() as client:
        # Test deck 1 queries
        queries = [
            ("deck 1 get_isplaying", "is_playing"),
            ("deck 1 get_title", "title"),
            ("deck 1 get_artist", "artist"),
            ("deck 1 get_bpm", "bpm"),
            ("deck 1 get_songlength", "duration"),
        ]

        for script, name in queries:
            success, res = await query(client, script)
            if success:
                result.ok(f"Deck 1 {name}: {res[:50] if res else '(empty)'}")
            else:
                result.fail(f"Deck 1 {name} query failed: {res}")


async def test_deck_commands(result: TestResult):
    """Test deck control commands"""
    print("\n3. Testing Deck Commands")
    print("-" * 40)

    async with httpx.AsyncClient() as client:
        # Test play/pause
        success, res = await execute(client, "deck 1 pause")
        if success:
            result.ok("Deck 1 pause command accepted")
        else:
            result.fail(f"Deck 1 pause failed: {res}")

        # Test volume
        success, res = await execute(client, "deck 1 volume 75%")
        if success:
            result.ok("Deck 1 volume command accepted")
        else:
            result.fail(f"Deck 1 volume failed: {res}")


async def test_mixer_commands(result: TestResult):
    """Test mixer commands"""
    print("\n4. Testing Mixer Commands")
    print("-" * 40)

    async with httpx.AsyncClient() as client:
        # Test crossfader
        success, res = await execute(client, "crossfader 50%")
        if success:
            result.ok("Crossfader command accepted")
        else:
            result.fail(f"Crossfader failed: {res}")


async def test_settings(result: TestResult):
    """Test settings commands"""
    print("\n5. Testing Settings")
    print("-" * 40)

    async with httpx.AsyncClient() as client:
        # Query loadSecurity setting
        success, res = await query(client, "setting loadSecurity")
        if success:
            result.ok(f"loadSecurity setting: {res}")
        else:
            result.fail(f"loadSecurity query failed: {res}")


async def test_skin_queries(result: TestResult):
    """Test skin-related queries"""
    print("\n6. Testing Skin Queries")
    print("-" * 40)

    async with httpx.AsyncClient() as client:
        queries = [
            ("skin_width", "width"),
            ("skin_height", "height"),
            ("get_decks", "deck_count"),
        ]

        for script, name in queries:
            success, res = await query(client, script)
            if success:
                result.ok(f"Skin {name}: {res}")
            else:
                result.fail(f"Skin {name} query failed: {res}")


async def test_track_loading(result: TestResult):
    """Test track loading (requires sample file)"""
    print("\n7. Testing Track Loading")
    print("-" * 40)

    # Check for a test track
    test_paths = [
        "E:/Multimedia Files/Music - Classical/Albinoni, Tomaso/Albinoni, Tomaso - Adagio in G minor [arr Giazotto] (Karajan, BePh 73).mp3",
        "C:/Users/Public/Music/Sample Music/Kalimba.mp3",
    ]

    test_track = None
    for path in test_paths:
        if Path(path).exists():
            test_track = path
            break

    if not test_track:
        result.skip("No test track found - skipping load test")
        return

    async with httpx.AsyncClient() as client:
        # First stop the deck to avoid loadSecurity popup
        await execute(client, "deck 2 stop")
        await asyncio.sleep(0.3)

        # Load track to deck 2 (avoid interrupting deck 1)
        normalized_path = test_track.replace("\\", "/")
        script = f"deck 2 load '{normalized_path}'"

        success, res = await execute(client, script)
        if success:
            result.ok("Track loaded to deck 2")

            # Wait for track to load
            await asyncio.sleep(1)

            # Verify track loaded
            success, title = await query(client, "deck 2 get_title")
            if success and title:
                result.ok(f"Verified: {title[:40]}...")
        else:
            result.fail(f"Track load failed: {res}")


async def main():
    """Main test runner"""
    print("=" * 50)
    print("VirtualDJ HTTP API Test Suite")
    print("=" * 50)
    print(f"\nTarget: {BASE_URL}")
    print("Requires: VirtualDJ with Network Control Plugin enabled")

    result = TestResult()

    # Run tests
    connected = await test_connection(result)

    if connected:
        await test_deck_queries(result)
        await test_deck_commands(result)
        await test_mixer_commands(result)
        await test_settings(result)
        await test_skin_queries(result)
        await test_track_loading(result)
    else:
        print("\n⚠️  Skipping remaining tests - no connection")

    # Summary
    success = result.summary()

    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check VirtualDJ and Network Control Plugin.")

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

