# Test Audio Fixtures

Small MP3 files for testing and demos.

| File | Frequency | Duration | Size |
|------|-----------|----------|------|
| `test_track_120bpm.mp3` | 440 Hz (A4) | 5 sec | ~40 KB |
| `test_track_128bpm.mp3` | 523 Hz (C5) | 5 sec | ~40 KB |

Generated with ffmpeg:
```bash
ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -c:a libmp3lame -b:a 64k test_track_120bpm.mp3
```

These are sine wave tones, not real music - just for testing deck loading, playback, and crossfading.

