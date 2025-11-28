# Test Audio Fixtures

Small MP3 files for testing and demos.

| File | Description | Duration | Size |
|------|-------------|----------|------|
| `test_track_120bpm.mp3` | 440 Hz sine (A4) | 5 sec | ~40 KB |
| `test_track_128bpm.mp3` | 523 Hz sine (C5) | 5 sec | ~40 KB |
| `test_track_fart.mp3` | Synthetic fart 💨 | 1.5 sec | ~12 KB |

Generated with ffmpeg:
```bash
# Sine tones
ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -c:a libmp3lame -b:a 64k test_track_120bpm.mp3

# Synthetic fart (pink noise + lowpass + tremolo + vibrato)
ffmpeg -f lavfi -i "anoisesrc=d=1.5:c=pink:a=0.3" -af "lowpass=f=200,tremolo=f=8:d=0.7,vibrato=f=5:d=0.5" -c:a libmp3lame -b:a 64k test_track_fart.mp3
```

These are synthetic sounds, not real music - for testing deck loading, playback, and crossfading. A bit of whimsy is allowed! 😄

