# VirtualDJ-MCP Help Content

🎵 **VirtualDJ-MCP Server v2.0.0 - Professional DJ Automation & Mixing**

Provides 12 consolidated portmanteau tools for professional deck control, mixing, stem separation, library management, and Plex integration.

---

## ⚙️ PREREQUISITES

VirtualDJ-MCP requires the **Network Control Plugin** for HTTP communication:

1. **VirtualDJ 2023+** with a Pro license.
2. Install the **Network Control** plugin: Go to **Config** → **Extensions** → **Effects** → **Other** and search for "Network Control".
3. Enable it in the Master panel (under **Master Effect** → **Auto-Start**).
4. (Optional) Set up OSC UDP commands mapping (default port: `40100`).

📖 **[Full Plugin Setup Guide](NETWORK_CONTROL_SETUP.md)**

---

## 📋 CONSOLIDATED PORTMANTEAU TOOLS

### 🔄 1. DECK CONTROL (`vdj_deck`)
Manage playback and track loading on VirtualDJ decks.
* **Operations**: `play`, `pause`, `toggle`, `stop`, `load`, `seek`, `volume`, `status`, `load_security`, `edit_lyrics`
* **Parameters**:
  - `deck_id` (int, default: 1)
  - `track_path` (str, required for `load`)
  - `position` (float/str, for `seek`, e.g., 120.5 or `"50%"`)
  - `volume` (int, 0-100, for `volume`)
  - `security_mode` (str, for `load_security`, e.g., `"off"`, `"on"`, `"always"`)
* **Example**:
  ```python
  vdj_deck("load", deck_id=1, track_path="C:/Music/song.mp3")
  vdj_deck("edit_lyrics", deck_id=1)  # Opens the AI lyrics editor panel
  ```

---

### 🎚️ 2. MIXER CONTROL (`vdj_mixer`)
Control channel gains, EQs, headphones cueing, master levels, and audio effect slots.
* **Operations**: `crossfader`, `sync`, `eq_high`, `eq_mid`, `eq_low`, `gain`, `filter`, `master_volume`, `headphone_volume`, `headphone_mix`, `effect`, `eq_reset`
* **Example**:
  ```python
  vdj_mixer("crossfader", position=0)  # Center crossfader
  vdj_mixer("sync", deck_a=1, deck_b=2)
  ```

---

### 🔍 3. LIBRARY SEARCH (`vdj_library`)
Discover local tracks and perform audio parameter analysis.
* **Operations**: `search`, `analyze`
* **Example**:
  ```python
  vdj_library("search", query="ABBA", bpm_min=110, bpm_max=130)
  ```

---

### 🎥 4. VIDEO MIXING (`vdj_video`)
Manage video deck playback, fullscreen outputs, transitions, and video FX.
* **Operations**: `crossfader`, `transition`, `fx`, `text`, `output`, `karaoke`, `scratch`, `loop`, `tempo_sync`, `load`

---

### 🎙️ 5. STEM SEPARATION (`vdj_stems`)
Isolate vocals, instrumentals, melodies, and drum tracks in real time.
* **Operations**: `kill`, `unkill`, `volume`, `acapella`, `instrumental`, `isolate_drums`, `swap`, `reset`, `sample_stem`
* **Parameters**:
  - `slot` (int, for `sample_stem`, sampler slot number to record into, default: 1)
* **Example**:
  ```python
  vdj_stems("acapella", deck_id=1)  # Mutes everything except vocals on deck 1
  vdj_stems("sample_stem", deck_id=1, slot=2)  # Record isolated stems directly to sampler slot 2
  ```

---

### 🔄 6. BEATGRID & TEMPO (`vdj_beatgrid`)
BPM beat grids, loops, tempo adjustments, and variable fluid tempo stabilization.
* **Operations**: `set_bpm`, `tap`, `adjust`, `anchor`, `pitch_bend`, `pitch_reset`, `beat_jump`, `loop`, `loop_roll`, `loop_exit`, `fluid`, `reanalyze_fluid`
* **Parameters**:
  - `enable` (bool, default: True, used for `fluid` variable grids)
* **Example**:
  ```python
  vdj_beatgrid("fluid", deck_id=1, enable=True) # Enable variable tempo beatgrid
  vdj_beatgrid("reanalyze_fluid", deck_id=1)     # Force fluid re-analysis
  ```

---

### 🖥️ 7. SYSTEM DASHBOARD (`vdj_system`)
Retrieve diagnostics, connection status, and view developer help files.
* **Operations**: `status`, `help`, `connection_test`

---

### 🌐 OTHER TOOLS
* `vdj_plex`: Search and load tracks directly from Plex Media Server.
* `vdj_automation`: Start Auto-DJ transition macros and get recommendations.
* `vdj_recording`: Start, stop, and list recordings of active sets.
* `vdj_skin`: Load visual skins and toggle custom UI panels.
* `vdj_performance`: Collect DJ session analytics and stats.
