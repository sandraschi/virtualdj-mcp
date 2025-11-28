# Automation Guide - VirtualDJ-MCP

## Automated DJ Operations

### Auto-DJ Overview

**VirtualDJ Auto-DJ** provides intelligent automatic mixing when you need:
- Continuous music during breaks
- Backup during technical issues
- Pre-programmed automated sets
- Testing transition ideas

#### **When to Use Auto-DJ**
- ✅ DJ breaks (bathroom, drink, etc.)
- ✅ Background music (before/after main set)
- ✅ Emergency backup (technical issues)
- ✅ Learning tool (watch how VirtualDJ mixes)
- ❌ Primary mixing method (lacks human touch)

### Auto-DJ Controls

#### **Enable/Disable**
```python
# Start Auto-DJ
automix_enable()

# Stop Auto-DJ (resume manual control)
automix_disable()

# Check status
status = get_automix_status()
```

#### **Auto-DJ Settings**
```
Transition Length: 8-32 beats (adjustable)
Track Selection: From specified playlist or folder
BPM Matching: Automatic sync
Volume Fading: Auto-managed
Energy Matching: Compatible track selection
```

### Recording Automation

#### **Session Recording**
```python
# Start recording current output
record_start(output_path="D:/Recordings/session_2025-10-25.mp3")

# Stop recording
record_stop()

# Record with specific quality
record_start(output_path="D:/Recordings/set.wav", quality="high")
```

#### **Recording Best Practices**
- Record in WAV or high-bitrate MP3 (320kbps)
- Include date/event in filename
- Monitor disk space (long sets = large files)
- Test recording setup before live performance
- Keep backups of important recordings

### Session Management

#### **Save/Load Sessions**
```python
# Save current session state
save_session(name="Friday Night Set")

# Load previous session
load_session(name="Friday Night Set")

Session includes:
- Loaded tracks on all decks
- Deck positions
- Cue points
- Effects settings
- Crossfader position
```

#### **Session Use Cases**
- Prepare sets in advance
- Create templates for events
- Resume interrupted performances
- Test different track orders
- Share setups between sessions

### Playlist Automation

#### **Smart Playlists** (Auto-updating)
```
Criteria examples:
- BPM range (125-130)
- Key compatibility (8A and compatible)
- Energy level (high-energy tag)
- Rating (4-5 stars)
- Recently added (last 30 days)
- Never played (expand repertoire)
```

#### **Auto-Mix Playlists**
```
Create flow-optimized playlists:
1. Sort by BPM (gradual increase/decrease)
2. Group by compatible keys
3. Alternate energy levels appropriately
4. Include transitions between genres
5. Test with Auto-DJ before live use
```

### Scripting and Macros

#### **VDJScript Automation**
```vdjscript
# Custom automation scripts
repeat_start 'deck 1' 4bt & effect_active 'echo' on
wait 3000ms & effect_active 'echo' off

# Conditional automation
deck 1 play ? deck 2 play : deck 1 play

# Time-based triggers
get_time > 230000 ? automix on : nothing
```

#### **Macro Examples**
```
Emergency Stop All: Stop all decks + fade master
Quick Transition: Auto-crossfade from current deck
Genre Switch: Load next genre playlist + automix
```

### Scheduled Operations

#### **Time-Based Automation**
```python
# Schedule events
schedule_event(time="23:00", action="enable_automix")
schedule_event(time="02:00", action="volume_fade_out", duration=300)

Use cases:
- Auto-start at event time
- Auto-end at closing time
- Scheduled breaks
- Timed announcements
```

### Monitoring and Alerts

#### **Performance Monitoring**
```python
# Real-time status checks
status = get_deck_status(deck=1)
master_volume = get_master_volume()
automix_active = get_automix_status()

# Alert conditions
if master_volume > 95:
    alert("Volume approaching maximum!")

if deck_time_remaining < 30:
    alert("Track ending soon!")
```

#### **Automated Responses**
```
Condition: Track ends unexpectedly
Response: Auto-start next track or enable Auto-DJ

Condition: Volume too high/low
Response: Auto-adjust to target range

Condition: No track loaded on backup deck
Response: Auto-load compatible track
```

### Best Practices

#### **Automation Do's**:
- ✅ Test automated routines before live use
- ✅ Have manual override always available
- ✅ Monitor automated processes
- ✅ Use for repetitive tasks (recording, breaks)
- ✅ Create backups of automated setups

#### **Automation Don'ts**:
- ❌ Rely completely on automation for live sets
- ❌ Ignore what Auto-DJ is doing (monitor it!)
- ❌ Use untested automation live
- ❌ Forget human touch and crowd reading
- ❌ Over-automate creative decisions

---

## Automation Philosophy

**Automation should**:
- Handle technical/repetitive tasks
- Provide safety nets
- Free you to focus on creativity
- Enhance, not replace, DJ skills

**Austrian Efficiency**: Automate the mundane, elevate the musical!

---

**VirtualDJ-MCP** enables sophisticated automation while keeping you in control. Use it wisely for professional, stress-free performances!

