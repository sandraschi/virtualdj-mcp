# VirtualDJ-MCP Help Content

🎵 **VirtualDJ-MCP Server v1.2.0 - Professional DJ Automation**

Austrian efficiency for professional DJ automation and music mixing needs.

## ⚙️ PREREQUISITES

VirtualDJ-MCP requires the **Network Control Plugin** for HTTP communication:

1. **VirtualDJ 2023+** with Pro license
2. Install Network Control Plugin: Config → Extensions → Effects → Other
3. Enable in Master panel → Master Effect → Auto-Start

📖 **[Full Setup Guide](NETWORK_CONTROL_SETUP.md)**

### Quick Connection Test
```bash
curl -X POST http://127.0.0.1:80/execute -H "Content-Type: text/plain" -d "nop"
```
Expected: `true`

---

## 📋 TOOL REFERENCE

### 🔄 **DECK CONTROL**

#### `play_pause_deck(deck_id, action)`
Control playback on a specific deck.
- **Parameters:**
  - `deck_id` (int): Deck number (1-8)
  - `action` (str): "play", "pause", or "toggle"
- **Returns:** Updated deck status

#### `load_track_to_deck(deck_id, track_path)`
Load a track to the specified deck.
- **Parameters:**
  - `deck_id` (int): Target deck number (1-8)
  - `track_path` (str): Full path to audio file
- **Returns:** Deck status with loaded track info

#### `seek_deck(deck_id, position)`
Seek to a specific position in the current track.
- **Parameters:**
  - `deck_id` (int): Deck number (1-8)
  - `position` (float/str): Position in seconds or percentage (e.g., 120.5 or "50%")
- **Returns:** Updated deck status

#### `set_deck_volume(deck_id, volume)`
Adjust the volume of a specific deck.
- **Parameters:**
  - `deck_id` (int): Deck number (1-8)
  - `volume` (int): Volume level (0-100)
- **Returns:** Updated deck status

#### `get_deck_status(deck_id)`
Retrieve the current status of a deck.
- **Parameters:**
  - `deck_id` (int): Deck number (1-8)
- **Returns:** DeckStatus object with track info, position, BPM, key, etc.

### 🎚️ **MIXING TOOLS**

#### `set_crossfader_position(position)`
Control the crossfader position.
- **Parameters:**
  - `position` (float): -100 (full left) to +100 (full right), 0 = center
- **Returns:** Current mixer status

#### `auto_sync_decks(deck_a, deck_b)`
Synchronize BPM between two decks.
- **Parameters:**
  - `deck_a` (int): Source deck number
  - `deck_b` (int): Target deck number
- **Returns:** Sync operation result

#### `set_eq_band(deck_id, band, value, kill=False)`
Adjust EQ settings for a specific deck.
- **Parameters:**
  - `deck_id` (int): Deck number (1-8)
  - `band` (str): EQ band ("low", "mid", or "high")
  - `value` (float): Gain value (-24 to +12 dB)
  - `kill` (bool): Whether to kill the band
- **Returns:** Operation status

#### `set_effect(deck_id, effect_slot, effect_type, enabled=True, wet_dry=50.0, param1=0.0, param2=0.0)`
Apply effects to a deck.
- **Parameters:**
  - `deck_id` (int): Deck number (1-8)
  - `effect_slot` (int): Effect slot (0-2)
  - `effect_type` (str): Effect type ("filter", "flanger", "echo", etc.)
  - `enabled` (bool): Whether the effect is active
  - `wet_dry` (float): Wet/dry mix (0-100)
  - `param1`, `param2` (float): Effect-specific parameters
- **Returns:** Operation status

### 🤖 **AUTO-DJ TOOLS**

#### `auto_dj_mode(duration_minutes, genre_filter, **prefs)`
Start or configure the Auto-DJ system.
- **Parameters:**
  - `duration_minutes` (int): Duration in minutes (0 for indefinite)
  - `genre_filter` (str, optional): Filter tracks by genre
  - `prefs`: Additional preferences (fade_time, energy_matching, etc.)
- **Returns:** Auto-DJ status

#### `stop_auto_dj()`
Stop the Auto-DJ system.
- **Returns:** Operation status

#### `get_auto_dj_status()`
Get the current status of the Auto-DJ system.
- **Returns:** Auto-DJ status information

#### `suggest_next_track(style, current_track_id, limit=5)`
Get track suggestions based on current playback.
- **Parameters:**
  - `style` (str): Suggestion style ("similar", "energy_up", "energy_down", "genre_switch")
  - `current_track_id` (str): ID of current track
  - `limit` (int): Maximum number of suggestions
- **Returns:** List of suggested tracks

### ⏺️ **RECORDING TOOLS**

#### `start_recording(name, format="wav")`
Start recording the current mix.
- **Parameters:**
  - `name` (str, optional): Name for the recording
  - `format` (str): Output format ("wav", "mp3", "ogg", "flac")
- **Returns:** Recording information

#### `stop_recording()`
Stop the current recording.
- **Returns:** Recording information

#### `get_recording_status(recording_id)`
Get the status of a recording.
- **Parameters:**
  - `recording_id` (str, optional): ID of specific recording
- **Returns:** Recording status and metadata

#### `list_recordings(limit=10, offset=0)`
List available recordings.
- **Parameters:**
  - `limit` (int): Maximum number of recordings to return
  - `offset` (int): Offset for pagination
- **Returns:** List of recordings with metadata

#### `export_mix_history(format="json", include_tracklist=True)`
Export mix history in specified format.
- **Parameters:**
  - `format` (str): Output format ("json", "csv", "txt")
  - `include_tracklist` (bool): Whether to include tracklist
- **Returns:** Export information

### 🔍 **SEARCH & LIBRARY**

#### `search_tracks(query, **filters)`
Search the music library.
- **Parameters:**
  - `query` (str): Search query
  - `filters`: Additional filters (genre, bpm, key, etc.)
- **Returns:** List of matching tracks

#### `analyze_track_audio(track_path)`
Analyze audio features of a track.
- **Parameters:**
  - `track_path` (str): Path to audio file
- **Returns:** Audio analysis results

## 🚀 **FEATURES & CAPABILITIES**

### **Professional DJ Features**
- **Multi-deck control** (up to 8 decks)
- **Advanced mixing** with EQ and effects
- **Auto-DJ** with intelligent track selection
- **High-quality recording** in multiple formats
- **BPM and key detection**
- **Harmonic mixing**
- **Track analysis** and metadata extraction

### **Integration & Automation**
- **REST API** for remote control
- **CLI interface** for scripting
- **Real-time status updates**
- **Event-based architecture**
- **Extensible plugin system**

#### **AUTOMATION & AI SUITE** (4 tools planned)
• `auto_dj_mode(duration, genre_filter)` - Automated DJ set
• `suggest_next_track(current_track, style)` - AI track recommendations
• `create_harmonic_mix(tracks, duration)` - Key-compatible mixing
• `record_mix(output_path, format)` - Record current session

#### **PERFORMANCE MONITORING** (3 tools planned)
• `get_session_analytics()` - Mix quality, transitions, crowd response
• `monitor_audio_levels()` - Input/output levels, clipping detection
• `get_hardware_status()` - Controller connectivity, latency

## 💪 STRENGTHS

• **Professional DJ software integration** (20+ years of VirtualDJ development)
• **Dual communication methods** (REST API + CLI for maximum reliability)
• **Real-time deck control** and mixing automation
• **Multi-deck support** (up to 8 decks simultaneously)
• **Hardware controller integration** through VirtualDJ
• **Type-safe operations** with Pydantic models
• **Rich error handling** and logging
• **Austrian efficiency design** - practical without complexity

## ⚠️ LIMITATIONS

• **Requires VirtualDJ installation** (not included with MCP server)
• **Some features need VirtualDJ Pro license** (auto-DJ, recording, advanced effects)
• **Hardware detection depends on VirtualDJ configuration**
• **Audio analysis quality varies with track quality**
• **Real-time performance depends on system resources**
• **CLI mode has limited feedback** compared to REST API
• **Windows-only** (VirtualDJ primary platform)

## 🔧 USAGE TIPS

### **Basic Deck Operations**
```
"Load track to deck 1 and start playing"
"Set deck 2 volume to 75%"
"Pause deck 1 and seek to 2 minutes"
"Show me the status of deck 2"
```

### **Mixing Operations**
```
"Set crossfader to center position"
"Auto-sync deck 2 to match deck 1 BPM"
"Move crossfader to favor deck 2"
```

### **Best Practices**
• Use `get_deck_status()` to monitor current playback state
• `auto_sync_decks()` works better with similar BPM tracks
• Load tracks before attempting playback operations
• Check deck status after load operations to verify success
• Use relative seek positions ("50%") for consistent behavior

### **Error Handling**
• All tools provide detailed error messages
• Check file paths exist before loading tracks
• Verify VirtualDJ is running before sending commands
• Monitor console for debugging information

## 🎛️ PROFESSIONAL FEATURES

### **Wedding DJ Automation**
• Mood-based track transitions (planned)
• Automated announcements (planned)
• Guest request management (planned)

### **Club Performance**
• Real-time mixing automation
• Beat-perfect synchronization
• Hardware controller integration
• Professional audio monitoring (planned)

### **Radio Show Automation**
• Scheduled content automation (planned)
• Intro/outro management (planned)
• Commercial break timing (planned)

### **Practice & Learning**
• Skill improvement tracking (planned)
• Mix quality analysis (planned)
• Beatmatching assistance

## 🚀 GETTING STARTED

### **Prerequisites**
1. **VirtualDJ installed** and configured
2. **Music library** with tracks for testing
3. **Audio configuration** set up in VirtualDJ
4. **Python 3.8+** with required dependencies

### **Installation**
```bash
# Clone the repository
git clone https://github.com/yourusername/virtualdj-mcp.git
cd virtualdj-mcp

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your VirtualDJ paths and settings
```

### **Quick Start**
1. Start the MCP server:
   ```bash
   python -m virtualdj_mcp
   ```

2. Use the API to control VirtualDJ:
   ```python
   # Example: Start playing a track
   response = await play_pause_deck(deck_id=1, action="play")
   ```

## 📚 **EXAMPLES**

### Basic Playback
```python
# Load and play a track
await load_track_to_deck(1, "/path/to/track.mp3")
await play_pause_deck(1, "play")

# Set volume and crossfader
await set_deck_volume(1, 80)
await set_crossfader_position(0)  # Center position
```

### Auto-DJ Session
```python
# Start Auto-DJ for 60 minutes
await auto_dj_mode(
    duration_minutes=60,
    genre_filter="House",
    energy_matching=True,
    harmonic_mixing=True
)

# Get status
status = await get_auto_dj_status()
print(f"Auto-DJ status: {status}")
```

### Recording a Mix
```python
# Start recording
recording = await start_recording("MyLiveSet", "mp3")
print(f"Recording started: {recording['filepath']}")

# ... perform your mix ...

# Stop recording
result = await stop_recording()
print(f"Recording saved: {result['filepath']}")
```

## 📖 **ADDITIONAL RESOURCES**

### **Documentation**
- [API Reference](https://github.com/yourusername/virtualdj-mcp/docs/API.md)
- [Configuration Guide](https://github.com/yourusername/virtualdj-mcp/docs/CONFIGURATION.md)
- [Troubleshooting](https://github.com/yourusername/virtualdj-mcp/docs/TROUBLESHOOTING.md)

### **Support**
For issues and feature requests, please [open an issue](https://github.com/yourusername/virtualdj-mcp/issues).

---
*VirtualDJ-MCP - Professional DJ Automation with Austrian Efficiency* 🇦🇹

1. Check server connection: `show_help()`
2. Test basic deck: `get_deck_status(1)`
3. Load a track: `load_track_to_deck(1, "C:/Music/song.mp3")`
4. Start playback: `play_pause_deck(1, "play")`
5. Try mixing: `set_crossfader_position(0)`
### **Configuration**
• **VirtualDJ Path**: Usually `C:/Program Files/VirtualDJ/virtualdj.exe`
• **API Port**: Default 8080 (configurable)
• **Music Library**: Point to your music collection
• **Audio Setup**: Configure in VirtualDJ settings

## 🎯 EXAMPLE WORKFLOWS

### **Basic DJ Session**
1. `get_deck_status(1)` - Check deck 1
2. `load_track_to_deck(1, "path/to/track1.mp3")` - Load first track
3. `play_pause_deck(1, "play")` - Start playing
4. `load_track_to_deck(2, "path/to/track2.mp3")` - Prepare second track
5. `auto_sync_decks(1, 2)` - Sync BPMs
6. `set_crossfader_position(-50)` - Transition to deck 2
7. `play_pause_deck(2, "play")` - Start second track

### **Quick Practice Session**
1. Load tracks to both decks
2. Use auto-sync for beatmatching practice
3. Practice crossfader transitions
4. Monitor deck status for timing

## 🇦🇹 AUSTRIAN EFFICIENCY FEATURES

• **No decision paralysis** - Clear tool purposes, obvious usage
• **Professional without complexity** - Vienna club standards made simple
• **Cultural context aware** - European electronic music focus
• **Practical solutions** - Real DJ needs drive development
• **Quality over quantity** - Essential features done well

Perfect for Sandra's DJ automation needs in Vienna! 🎵🇦🇹

## 📞 SUPPORT & TROUBLESHOOTING

### **Common Issues**
• **VirtualDJ not responding**: Check if VirtualDJ is running and API enabled
• **Track won't load**: Verify file path exists and format supported
• **No audio output**: Check VirtualDJ audio configuration
• **Command timeouts**: Increase timeout settings in configuration

### **Development Status**
• **Phase 1**: Core infrastructure ✅ COMPLETE
• **Phase 2**: Library & mixing 🚧 IN PROGRESS
• **Phase 3**: Automation & AI 📋 PLANNED
• **Phase 4**: Analytics & monitoring 📋 PLANNED

For detailed development information, see `docs/DEVELOPMENT_PLAN.md`
For VirtualDJ commands reference, see `docs/VIRTUALDJ_REFERENCE.md`

---
**Built with Austrian efficiency for professional DJ automation! 🎵🇦🇹**
