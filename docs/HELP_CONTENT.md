# VirtualDJ-MCP Help Content

🎵 **VirtualDJ-MCP Server v1.0.0 - Professional DJ Automation**

Austrian efficiency for Sandra's music mixing and DJ automation needs.

## 📋 CAPABILITIES (20+ Tools Planned)

### ✅ **CURRENT TOOLS (9 implemented)**

#### **SHOW HELP**
• `show_help()` - Get detailed help about capabilities, strengths, and limitations

#### **DECK CONTROL SUITE** (6 tools)
• `play_pause_deck(deck_id, action)` - Control playback on specific deck
  - deck_id: Deck number (1-8)
  - action: "play", "pause", or "toggle"

• `load_track_to_deck(deck_id, track_path)` - Load track to deck
  - deck_id: Target deck number
  - track_path: Full path to audio file

• `seek_deck(deck_id, position)` - Seek to position
  - deck_id: Deck number
  - position: Seconds (float) or percentage ("50%")

• `set_deck_volume(deck_id, volume)` - Set deck volume
  - deck_id: Deck number
  - volume: Volume level (0-100)

• `get_deck_status(deck_id)` - Get current deck status
  - Returns: DeckStatus with track info, position, BPM, key, etc.

#### **MIXING & CROSSFADER SUITE** (2 tools)
• `set_crossfader_position(position)` - Control crossfader
  - position: -100 (full left) to +100 (full right), 0 = center

• `auto_sync_decks(deck_a, deck_b)` - Sync BPM between decks
  - deck_a: Source deck number
  - deck_b: Target deck number

### 🚧 **COMING SOON (Phase 2-4)**

#### **LIBRARY MANAGEMENT SUITE** (5 tools planned)
• `search_tracks(query, filters)` - Search music library
• `scan_music_library(path)` - Scan and import music files
• `get_track_analysis(track_path)` - BPM, key, energy analysis
• `create_playlist(name, tracks)` - Create/manage playlists
• `get_library_stats()` - Library statistics and health

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
1. **VirtualDJ installed** (free version works for basic features)
2. **Music library** with some tracks for testing
3. **Audio configuration** set up in VirtualDJ
4. **MCP server** added to Claude Desktop configuration

### **First Steps**
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
