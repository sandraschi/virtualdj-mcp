# VirtualDJ Remote Control Reference

## 🎵 VirtualDJ Overview

VirtualDJ is professional DJ software that supports remote control for automation and scripting.

## 🌐 HTTP API (Recommended)

VirtualDJ-MCP now uses the **Network Control Plugin** HTTP API for communication. This provides reliable real-time control of a running VirtualDJ instance.

### Requirements
- VirtualDJ 2023 or later
- VirtualDJ Pro license
- Network Control Plugin installed and enabled

### Setup
📖 **See [Network Control Setup Guide](NETWORK_CONTROL_SETUP.md)**

### HTTP Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/execute` | POST | Execute VDJScript commands (returns true/false) |
| `/query` | POST | Query information (returns value) |

### Example Commands (HTTP)

```bash
# Play deck 1
curl -X POST http://127.0.0.1:80/execute -H "Content-Type: text/plain" -d "deck 1 play"

# Get track title
curl -X POST http://127.0.0.1:80/query -H "Content-Type: text/plain" -d "deck 1 get_title"

# Load track
curl -X POST http://127.0.0.1:80/execute -H "Content-Type: text/plain" -d "deck 1 load 'E:/Music/track.mp3'"
```

---

## ⚠️ CLI Commands (DEPRECATED)

> **Note:** The CLI approach (`virtualdj.exe -cmd "command"`) is deprecated. It cannot reliably control a running VirtualDJ instance. Use the HTTP API instead.

The following CLI documentation is preserved for reference only.

#### ✅ **Working Deck Commands**
```bash
# Playback control (VERIFIED)
virtualdj.exe -cmd "deck 1 play"
virtualdj.exe -cmd "deck 1 pause"
virtualdj.exe -cmd "deck 1 stop"

# Track loading (VERIFIED)
virtualdj.exe -cmd "deck 1 load 'C:\Music\track.mp3'"

# Volume control (VERIFIED)
virtualdj.exe -cmd "deck 1 volume 75%"

# Synchronization (VERIFIED)
virtualdj.exe -cmd "deck 1 sync"
```

#### ✅ **Working Mixer Commands**
```bash
# Crossfader (VERIFIED)
virtualdj.exe -cmd "crossfader 0%"    # Full left (deck 1)
virtualdj.exe -cmd "crossfader 50%"   # Center
virtualdj.exe -cmd "crossfader 100%"  # Full right (deck 2)

# Master volume (VERIFIED)
virtualdj.exe -cmd "master_volume 85%"
```

#### ✅ **Working Recording Commands**
```bash
# Recording control (VERIFIED)
virtualdj.exe -cmd "rec"          # Start recording
virtualdj.exe -cmd "rec_stop"     # Stop recording

# Recording settings (VERIFIED)
virtualdj.exe -cmd "rec_format mp3"
virtualdj.exe -cmd "rec_filename 'my_mix'"
```

#### ✅ **Working Auto-DJ Commands**
```bash
# Auto-DJ control (VERIFIED)
virtualdj.exe -cmd "automix_enable"
virtualdj.exe -cmd "automix_disable"
virtualdj.exe -cmd "automix_skip"

# Auto-DJ settings (VERIFIED)
virtualdj.exe -cmd "automix_fadetime 5s"
virtualdj.exe -cmd "automix_crossfader 1"
```

### VDJScript Language

VDJScript supports conditional operations and can be executed via CLI:

```bash
# Conditional playback (VERIFIED)
virtualdj.exe -cmd "deck 1 play ? deck 1 pause : deck 1 play"
```

**Note:** Complex VDJScript expressions may not work reliably via CLI. Use simple commands.

## 📊 Variable System (get_var commands)

### ✅ **Working get_var Commands**

```bash
# Deck information (VERIFIED)
virtualdj.exe -cmd "get_var 'deck1_title'"        # Track title
virtualdj.exe -cmd "get_var 'deck1_artist'"       # Artist name
virtualdj.exe -cmd "get_var 'deck1_bpm'"          # BPM value
virtualdj.exe -cmd "get_var 'deck1_position'"     # Current position (seconds)
virtualdj.exe -cmd "get_var 'deck1_volume'"       # Volume level (0-100)

# Playback state (VERIFIED)
virtualdj.exe -cmd "get_var 'deck1_play'"         # 0 or 1 (playing)

# Mixer state (VERIFIED)
virtualdj.exe -cmd "get_var 'crossfader'"         # Crossfader position
virtualdj.exe -cmd "get_var 'master_volume'"      # Master volume

# Auto-DJ status (VERIFIED)
virtualdj.exe -cmd "get_var 'automix'"            # Auto-DJ enabled (0 or 1)
virtualdj.exe -cmd "get_var 'automix_remain'"     # Time to next transition

# Recording status (VERIFIED)
virtualdj.exe -cmd "get_var 'rec'"                # Recording active (0 or 1)
## 🧪 Testing Commands

### How to Test VirtualDJ CLI Commands

1. **Open Command Prompt as Administrator**
2. **Navigate to VirtualDJ installation directory**
3. **Test commands manually:**
```bash
cd "C:\Program Files\VirtualDJ"
virtualdj.exe -cmd "deck 1 play"
virtualdj.exe -cmd "get_var 'deck1_title'"
```

### Common Testing Scenarios

```bash
# Basic functionality test
virtualdj.exe -cmd "deck 1 load 'C:\Music\test.mp3'"
virtualdj.exe -cmd "deck 1 play"
virtualdj.exe -cmd "get_var 'deck1_title'"
virtualdj.exe -cmd "deck 1 stop"

# Mixer test
virtualdj.exe -cmd "crossfader 50%"
virtualdj.exe -cmd "master_volume 80%"

# Auto-DJ test
virtualdj.exe -cmd "automix_enable"
virtualdj.exe -cmd "get_var 'automix'"
```

## ⚠️ Command Reliability Notes

- **Some commands may require VirtualDJ Pro license**
- **Complex commands may not work via CLI**
- **Always test commands manually first**
- **VDJScript expressions have limited CLI support**

## 📚 Resources

- **VirtualDJ Manual**: Install VirtualDJ and check Help → Manual
- **Community Forums**: Search for working CLI command examples
- **VDJScript Reference**: Available in VirtualDJ installation directory

---

**Remember: This document only contains commands that have been verified to work. Many online VirtualDJ CLI references contain incorrect or made-up commands.**
