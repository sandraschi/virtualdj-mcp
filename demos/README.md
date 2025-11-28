# VirtualDJ-MCP Demos

A collection of demo scripts showcasing the power of AI-controlled DJing.

## Demo Scripts

| Script | Description | Decks | Highlights |
|--------|-------------|-------|------------|
| `superhuman_dj_demo.py` | 8-deck impossibility | 8 | 16 hands, superluminal speed, polyrhythmic loops |
| `metal_kills_jingle_demo.py` | Holiday massacre | 2 | Stem killing, dramatic crossfade, THE KILL |
| `full_feature_demo.py` | Complete feature tour | 2 | All tools demonstrated with popups |
| `dj_tricks_demo.py` | Fast artistic moves | 2 | Transformer, baby scratch, crab scratch |
| `auto_mix_demo.py` | Automatic mixing | 2 | Library scan, random selection, crossfade |
| `auto_dj_example.py` | AutoDJ mode | 2 | Hands-off automatic mixing |
| `basic_playback.py` | Simple playback | 1 | Load, play, volume basics |
| `recording_example.py` | Mix recording | 2 | Start/stop recording, export |
| `performance_monitor.py` | Analytics | - | BPM stability, energy tracking |

## Quick Start

```powershell
cd D:\Dev\repos\virtualdj-mcp
.venv\Scripts\Activate.ps1

# Run the 8-deck superhuman demo
python demos/superhuman_dj_demo.py

# Run metal kills jingle (with your own tracks!)
python demos/metal_kills_jingle_demo.py "jingle.mp3" "motorhead.mp3"

# Full feature tour
python demos/full_feature_demo.py
```

## Requirements

- VirtualDJ running with HTTP Network Control enabled
- Python 3.11 (for aubio audio analysis)
- Test tracks in `tests/fixtures/audio/` or provide your own

## Demo Ideas (TODO)

### Audio Demos
- [ ] `battle_of_genres.py` - 4 genres fight for dominance
- [ ] `tempo_ramp.py` - BPM escalation from 80 to 180
- [ ] `stem_surgery.py` - Extract and remix stems live
- [ ] `loop_symphony.py` - Build a track from loops across 8 decks
- [ ] `beatmatch_challenge.py` - AI vs manual beatmatching speed test

### Video Demos (VirtualDJ supports video!)
- [ ] `video_crossfade.py` - Smooth video transitions
- [ ] `video_effects.py` - Apply video FX in sync with audio
- [ ] `karaoke_night.py` - Load karaoke videos, control lyrics display
- [ ] `vj_set.py` - Full VJ performance with video mixing
- [ ] `music_video_mashup.py` - Sync multiple music videos

### Creative Demos
- [ ] `ai_request_dj.py` - Take song requests via voice/text
- [ ] `mood_detector.py` - Adjust music based on "crowd energy"
- [ ] `mashup_generator.py` - Auto-create mashups from stems
- [ ] `genre_journey.py` - Smooth transitions across genres
- [ ] `time_machine.py` - Decade-by-decade music journey

### Integration Demos
- [ ] `plex_dj_night.py` - Full DJ set from Plex library
- [ ] `spotify_to_vdj.py` - Import Spotify playlists
- [ ] `obs_streaming.py` - DJ + OBS streaming integration
- [ ] `twitch_requests.py` - Twitch chat song requests

## Test Fixtures

Small MP3 files for testing (in `tests/fixtures/audio/`):

| File | Description |
|------|-------------|
| `test_track_120bpm.mp3` | 5 sec, 440 Hz sine wave |
| `test_track_128bpm.mp3` | 5 sec, 523 Hz sine wave |
| `test_track_fart.mp3` | 1.5 sec, synthetic fart noise |
| `test_track_holdmusic.mp3` | 2.4 sec, annoying ascending scale |
| `test_track_buzzer.mp3` | 1.5 sec, dissonant chord |
| `test_track_dissonance.mp3` | 3 sec, dental nightmare |

## Contributing

Got a cool demo idea? Create it and add to this list!

```python
"""
YOUR_DEMO_NAME - Brief description

What it does...
"""

import asyncio
from virtualdj_mcp.core.vdj_client import VirtualDJClient, VDJConfig

async def main():
    config = VDJConfig()
    async with VirtualDJClient(config) as vdj:
        # Your magic here!
        pass

if __name__ == "__main__":
    asyncio.run(main())
```
