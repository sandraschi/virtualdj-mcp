# VirtualDJ-MCP Examples

This directory contains working example scripts that demonstrate VirtualDJ CLI and VDJScript usage for DJ automation.

## Available Examples

### 1. Basic Playback (`basic_playback.py`)
Demonstrates fundamental VirtualDJ control using CLI commands:
- ✅ Loads tracks to decks (`deck 1 load 'track.mp3'`)
- ✅ Controls playback (`deck 1 play`, `deck 1 pause`, `deck 1 stop`)
- ✅ Adjusts volume (`deck 1 volume 70%`)
- ✅ Uses crossfader (`crossfader -100%` to `crossfader 100%`)

**Usage:**
```bash
python examples/basic_playback.py
```
**Note:** Update the track paths in the script to point to your actual music files!

### 2. Auto-DJ (`auto_dj_example.py`)
Demonstrates VirtualDJ's built-in Auto-DJ features using CLI commands:
- ✅ Enables Auto-DJ (`automix_enable`)
- ✅ Configures crossfader transitions (`automix_crossfader 1`)
- ✅ Sets fade times (`automix_fadetime 8s`)
- ✅ Monitors Auto-DJ status (`get_var 'automix_remain'`)

**Usage:**
```bash
# Run for 5 minutes (default)
python examples/auto_dj_example.py

# Custom duration
python examples/auto_dj_example.py --duration 10
```

### 3. Recording (`recording_example.py`)
Shows how to record DJ mixes using VirtualDJ's recording features:
- ✅ Configures recording format (`rec_format mp3`)
- ✅ Sets recording filename (`rec_filename 'mix_name'`)
- ✅ Starts/stops recording (`rec`, `rec_stop`)
- ✅ Monitors recording status (`get_var 'rec_time'`)

**Usage:**
```bash
# Record for 30 seconds
python examples/recording_example.py

# Custom settings
python examples/recording_example.py --name "MyMix" --format mp3 --duration 60
```

### 4. Performance Monitor (`performance_monitor.py`)
Real-time monitoring of VirtualDJ performance metrics:
- ✅ Displays deck status (track info, BPM, position, volume)
- ✅ Shows mixer state (crossfader, master volume)
- ✅ Monitors system metrics (CPU usage, sample rate)
- ✅ Saves metrics to JSON file for analysis

**Usage:**
```bash
# Monitor for 60 seconds (default)
python examples/performance_monitor.py

# Custom settings with output file
python examples/performance_monitor.py --duration 120 --interval 1.0 --output metrics.json
```

## Prerequisites

1. **VirtualDJ Installation**: Must be installed and accessible at the configured path
2. **Python Dependencies**: Install with `pip install -r requirements.txt`
3. **Music Files**: Update track paths in scripts to point to actual MP3/WAV files

## How It Works

All examples use the `VirtualDJClient` class which:
- ✅ Launches VirtualDJ if not running (`subprocess.Popen`)
- ✅ Sends CLI commands (`virtualdj.exe -cmd "command"`)
- ✅ Retrieves variables (`get_var 'deck1_bpm'`)
- ✅ Supports VDJScript expressions for advanced logic

**No REST API required** - everything uses VirtualDJ's actual CLI interface!

## Example Output

```
🎵 VirtualDJ-MCP Basic Playback Example
==================================================
Using VirtualDJ path: C:/Program Files/VirtualDJ/virtualdj.exe
✅ Connected to VirtualDJ client
🎧 VirtualDJ is running
🎵 Loading C:\Users\sandr\Music\track1.mp3 to deck 1
Load result: {'status': 'success', 'result': ''}
▶️  Starting playback on both decks
🔊 Setting volumes to 70%
🎛️  Moving crossfader to center
✅ Example completed successfully!
```

## Common Issues & Solutions

- **"Please update the track paths"**: Edit the track paths in the script
- **"Failed to start VirtualDJ"**: Check VirtualDJ installation path
- **"Command failed"**: VirtualDJ may not be responding to CLI commands
- **Import errors**: Run from project root: `python examples/basic_playback.py`

## Extending the Examples

All examples are built using these core VirtualDJClient methods:
- `send_command(cmd)` - Execute CLI/VDJScript commands
- `get_variable(var)` - Get VirtualDJ variables
- `get_status()` - Get overall VirtualDJ status
- `is_running()` - Check if VirtualDJ process is active

**Ready to extend?** Check the VirtualDJ documentation for more CLI commands and VDJScript functions!
