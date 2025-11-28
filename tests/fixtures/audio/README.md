# Test Audio Fixtures

Small MP3 files for testing and demos.

## The Collection

| File | Description | Duration | Size |
|------|-------------|----------|------|
| `test_track_120bpm.mp3` | 440 Hz sine (A4) | 5 sec | ~40 KB |
| `test_track_128bpm.mp3` | 523 Hz sine (C5) | 5 sec | ~40 KB |
| `test_track_fart.mp3` | Synthetic fart 💨 | 1.5 sec | ~12 KB |
| `test_track_holdmusic.mp3` | Elevator muzak from hell 🎵 | 2.4 sec | ~20 KB |
| `test_track_buzzer.mp3` | Game show wrong answer 📢 | 1.5 sec | ~12 KB |

## Generation Recipes

```bash
# Sine tones
ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -c:a libmp3lame -b:a 64k test_track_120bpm.mp3

# Synthetic fart (pink noise + lowpass + tremolo + vibrato)
ffmpeg -f lavfi -i "anoisesrc=d=1.5:c=pink:a=0.3" \
  -af "lowpass=f=200,tremolo=f=8:d=0.7,vibrato=f=5:d=0.5" \
  -c:a libmp3lame -b:a 64k test_track_fart.mp3

# Hold music (ascending scale with echo)
ffmpeg -f lavfi -i "aevalsrc=sin(523*2*PI*t)*exp(-3*t):d=0.4" ... \
  -filter_complex "concat=n=5:v=0:a=1,aecho=0.8:0.5:100:0.4" \
  -c:a libmp3lame -b:a 64k test_track_holdmusic.mp3

# Wrong answer buzzer (dissonant chord)
ffmpeg -f lavfi -i "aevalsrc=sin(200*2*PI*t)+sin(250*2*PI*t)+sin(300*2*PI*t):d=1.5" \
  -af "volume=0.3,afade=t=out:st=1:d=0.5" \
  -c:a libmp3lame -b:a 64k test_track_buzzer.mp3
```

All sounds are 100% synthetic - no copyright issues, just pure audio engineering whimsy! 🎉

