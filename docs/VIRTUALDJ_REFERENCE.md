# VirtualDJ Software Documentation for MCP Integration

## 🎵 VirtualDJ Overview

VirtualDJ is professional DJ software with 20+ years of development, used by millions of DJs worldwide. It provides comprehensive mixing, effects, and automation capabilities with excellent API support.

## 🔧 Key Technical Features

### Core Capabilities
- **Multi-deck mixing** (2, 4, 6, 8+ decks simultaneously)
- **Real-time effects** (filters, reverb, delay, flangers, etc.)
- **Advanced beat detection** (BPM analysis, beat grids, key detection)
- **Hardware controller support** (100+ controllers supported)
- **Recording and broadcasting** (live streaming, mix recording)
- **Extensive scripting** (VDJScript programming language)

### API Interfaces

#### 1. Command Line Interface (CLI)
VirtualDJ provides excellent CLI support for automation:
```bash
# Basic syntax
virtualdj.exe -cmd "command_string"

# Examples
virtualdj.exe -cmd "deck 1 play"
virtualdj.exe -cmd "deck 1 load 'C:\Music\track.mp3'"
virtualdj.exe -cmd "crossfader 50%"
virtualdj.exe -cmd "get_var 'deck1_bpm'"
```

#### 2. REST API Interface
VirtualDJ can expose a REST API for web-based control:
```bash
# Start with API enabled
virtualdj.exe -api 8080

# HTTP requests
POST http://localhost:8080/command
{
  "cmd": "deck 1 play"
}

GET http://localhost:8080/status
```

#### 3. VDJScript Language
Advanced scripting for complex operations:
```vdjscript
# VDJScript examples
deck 1 play ? deck 1 pause : deck 1 play
repeat_start_stop deck 1
deck 1 bpm > 120 ? effect 'filter' active : effect 'reverb' active
```

## 🎛️ VirtualDJ Command Reference

### Deck Control Commands
```bash
# Playback control
virtualdj.exe -cmd "deck 1 play"
virtualdj.exe -cmd "deck 1 pause"
virtualdj.exe -cmd "deck 1 stop"
virtualdj.exe -cmd "deck 1 play_pause"

# Loading tracks
virtualdj.exe -cmd "deck 1 load 'filepath'"
virtualdj.exe -cmd "deck 1 load_next"
virtualdj.exe -cmd "deck 1 load_previous"

# Position control
virtualdj.exe -cmd "deck 1 goto 30%"      # Percentage
virtualdj.exe -cmd "deck 1 goto 120s"     # Seconds
virtualdj.exe -cmd "deck 1 goto +10s"     # Relative

# Volume and pitch
virtualdj.exe -cmd "deck 1 volume 75%"
virtualdj.exe -cmd "deck 1 pitch +5%"
virtualdj.exe -cmd "deck 1 pitch_reset"

# Synchronization
virtualdj.exe -cmd "deck 1 sync"
virtualdj.exe -cmd "deck 1 sync deck 2"
```

### Mixer Control Commands
```bash
# Crossfader
virtualdj.exe -cmd "crossfader 0%"        # Full left (deck 1)
virtualdj.exe -cmd "crossfader 50%"       # Center
virtualdj.exe -cmd "crossfader 100%"      # Full right (deck 2)

# EQ controls
virtualdj.exe -cmd "deck 1 eq_high 80%"
virtualdj.exe -cmd "deck 1 eq_mid 75%"
virtualdj.exe -cmd "deck 1 eq_low 90%"

# Master volume
virtualdj.exe -cmd "master_volume 85%"

# Headphone controls
virtualdj.exe -cmd "headphone_volume 60%"
virtualdj.exe -cmd "deck 1 headphone_cue"
```

### Effects Commands
```bash
# Effect selection
virtualdj.exe -cmd "deck 1 effect_select 'filter'"
virtualdj.exe -cmd "deck 1 effect_select 'reverb'"
virtualdj.exe -cmd "deck 1 effect_select 'flanger'"

# Effect activation
virtualdj.exe -cmd "deck 1 effect_button 1"      # Toggle effect
virtualdj.exe -cmd "deck 1 effect_active 1"      # Activate
virtualdj.exe -cmd "deck 1 effect_active 0"      # Deactivate

# Effect parameters
virtualdj.exe -cmd "deck 1 effect_parameter 1 50%"
```

### Library and Playlist Commands
```bash
# Library browsing
virtualdj.exe -cmd "browser_folder 'C:\Music'"
virtualdj.exe -cmd "browser_search 'artist name'"
virtualdj.exe -cmd "browser_filter 'bpm > 120'"

# Playlist operations
virtualdj.exe -cmd "playlist_create 'My Set'"
virtualdj.exe -cmd "playlist_add 'track_id'"
virtualdj.exe -cmd "playlist_load 'My Set'"
```

### Recording Commands
```bash
# Recording control
virtualdj.exe -cmd "rec"                  # Start recording
virtualdj.exe -cmd "rec_stop"             # Stop recording
virtualdj.exe -cmd "rec_pause"            # Pause recording

# Recording settings
virtualdj.exe -cmd "rec_format mp3"
virtualdj.exe -cmd "rec_quality 320"
virtualdj.exe -cmd "rec_filename 'mix_session'"
```

### Auto-DJ Commands
```bash
# Auto-DJ control
virtualdj.exe -cmd "automix_enable"
virtualdj.exe -cmd "automix_disable"
virtualdj.exe -cmd "automix_skip"

# Auto-DJ settings
virtualdj.exe -cmd "automix_fadetime 5s"
virtualdj.exe -cmd "automix_crossfader 1"
```

## 📊 Variable System (get_var commands)

### Deck Variables
```bash
# Playback state
virtualdj.exe -cmd "get_var 'deck1_play'"         # 0 or 1
virtualdj.exe -cmd "get_var 'deck1_pause'"        # 0 or 1

# Track information
virtualdj.exe -cmd "get_var 'deck1_title'"        # Track title
virtualdj.exe -cmd "get_var 'deck1_artist'"       # Artist name
virtualdj.exe -cmd "get_var 'deck1_album'"        # Album name
virtualdj.exe -cmd "get_var 'deck1_bpm'"          # BPM value
virtualdj.exe -cmd "get_var 'deck1_key'"          # Musical key

# Position and timing
virtualdj.exe -cmd "get_var 'deck1_position'"     # Current position (seconds)
virtualdj.exe -cmd "get_var 'deck1_duration'"     # Track duration (seconds)
virtualdj.exe -cmd "get_var 'deck1_remain'"       # Time remaining (seconds)

# Volume and pitch
virtualdj.exe -cmd "get_var 'deck1_volume'"       # Volume level (0-100)
virtualdj.exe -cmd "get_var 'deck1_pitch'"        # Pitch adjustment
```

### Mixer Variables
```bash
# Crossfader and master
virtualdj.exe -cmd "get_var 'crossfader'"         # Crossfader position
virtualdj.exe -cmd "get_var 'master_volume'"      # Master volume

# EQ levels
virtualdj.exe -cmd "get_var 'deck1_eq_high'"
virtualdj.exe -cmd "get_var 'deck1_eq_mid'"
virtualdj.exe -cmd "get_var 'deck1_eq_low'"
```

### System Variables
```bash
# Performance monitoring
virtualdj.exe -cmd "get_var 'cpu_usage'"          # CPU usage percentage
virtualdj.exe -cmd "get_var 'audio_buffer'"       # Audio buffer usage
virtualdj.exe -cmd "get_var 'sample_rate'"        # Audio sample rate

# Auto-DJ status
virtualdj.exe -cmd "get_var 'automix'"            # Auto-DJ enabled
virtualdj.exe -cmd "get_var 'automix_remain'"     # Time to next transition

# Recording status
virtualdj.exe -cmd "get_var 'rec'"                # Recording active
virtualdj.exe -cmd "get_var 'rec_time'"           # Recording duration
```

## 🔍 Advanced Features

### Beat Synchronization
```bash
# Manual beat sync
virtualdj.exe -cmd "deck 1 sync"
virtualdj.exe -cmd "deck 1 sync deck 2"

# Beat matching assistance
virtualdj.exe -cmd "deck 1 pitch_bend +0.1"
virtualdj.exe -cmd "deck 1 pitch_bend -0.1"

# Quantized operations (snap to beat)
virtualdj.exe -cmd "deck 1 play_start_next_beat"
virtualdj.exe -cmd "deck 1 cue_next_beat"
```

### Key Detection and Harmonic Mixing
```bash
# Key information
virtualdj.exe -cmd "get_var 'deck1_key'"          # Current track key
virtualdj.exe -cmd "get_var 'deck1_key_detected'" # Auto-detected key

# Harmonic mixing assistance
virtualdj.exe -cmd "get_var 'harmonic_compatible_keys'" # Compatible keys
```

### Advanced Effects and Loops
```bash
# Loop controls
virtualdj.exe -cmd "deck 1 loop 4"               # 4-beat loop
virtualdj.exe -cmd "deck 1 loop_roll 2"          # 2-beat roll
virtualdj.exe -cmd "deck 1 loop_exit"            # Exit loop

# Hot cues
virtualdj.exe -cmd "deck 1 cue 1"                # Set/jump to cue point 1
virtualdj.exe -cmd "deck 1 cue_delete 1"         # Delete cue point 1

# Advanced effects
virtualdj.exe -cmd "deck 1 effect 'filter' parameter 1 75%"
virtualdj.exe -cmd "deck 1 effect 'beatgrid' active"
```

## 🎯 VirtualDJ-MCP Integration Strategy

### Command Mapping Priority
**Phase 1 (Implemented):**
- Basic deck control (play, pause, load, volume)
- Crossfader control
- Status retrieval (get_var commands)

**Phase 2 (Next):**
- Library browsing and search
- EQ controls
- Basic effects
- Playlist management

**Phase 3 (Future):**
- Auto-DJ functionality
- Recording controls
- Advanced effects
- Performance monitoring

### Error Handling Patterns
```bash
# Commands that might fail
virtualdj.exe -cmd "deck 1 load 'nonexistent.mp3'"    # File not found
virtualdj.exe -cmd "deck 1 play"                      # No track loaded
virtualdj.exe -cmd "get_var 'invalid_variable'"       # Variable doesn't exist
```

### Performance Considerations
- **Command latency**: CLI commands typically respond in 10-50ms
- **Variable polling**: Don't poll more than 10 times per second
- **Batch commands**: Use VDJScript for multiple operations
- **Error recovery**: Always check command success before continuing

### Limitations and Workarounds
**Limitations:**
- CLI provides limited feedback (success/failure only)
- Some operations require VirtualDJ Pro license
- API availability depends on VirtualDJ version
- Hardware-specific features may not work via API

**Workarounds:**
- Use get_var to verify command results
- Implement retry logic for critical operations
- Graceful degradation for Pro-only features
- Mock/simulate unavailable hardware features

## 📚 Documentation Resources

### Official VirtualDJ Resources
- **VirtualDJ Manual**: Comprehensive user guide
- **VDJScript Reference**: Complete scripting documentation
- **API Documentation**: REST API and automation guides
- **Forum Community**: Active developer community

### Useful Community Resources
- **VirtualDJ Scripts Database**: User-contributed scripts
- **Controller Mappings**: Hardware integration examples
- **Video Tutorials**: Visual learning resources
- **GitHub Projects**: Open-source VirtualDJ tools

## 🔧 Development Tips

### Testing with VirtualDJ
1. **Install VirtualDJ** (free version sufficient for basic testing)
2. **Test CLI commands** manually before implementing in code
3. **Use small music library** for initial testing (10-20 tracks)
4. **Enable logging** in VirtualDJ for debugging
5. **Document working commands** as you discover them

### Common Integration Patterns
```python
# Error handling pattern
async def safe_vdj_command(self, command: str):
    try:
        result = await self.send_command(command)
        if result["status"] != "success":
            raise VDJError(f"Command failed: {command}")
        return result
    except Exception as e:
        console.print(f"[red]VDJ Error: {e}[/red]")
        raise

# Status verification pattern
async def verify_deck_state(self, deck_id: int, expected_state: str):
    actual = await self.send_command(f"get_var 'deck{deck_id}_play'")
    return actual["result"] == expected_state
```

This documentation provides comprehensive guidance for integrating with VirtualDJ's extensive API capabilities! 🎵
