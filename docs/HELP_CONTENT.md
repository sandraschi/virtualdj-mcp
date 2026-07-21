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
* **Operations**: `play`, `pause`, `toggle`, `stop`, `load`, `seek`, `volume`, `status`, `load_security`
* **Parameters**:
  - `deck_id` (int, default: 1)
  - `track_path` (str, required for `load`)
  - `position` (float/str, for `seek`, e.g., 120.5 or `"50%"`)
  - `volume` (int, 0-100, for `volume`)
  - `security_mode` (str, for `load_security`, e.g., `"off"`, `"on"`, `"always"`)
* **Example**:
  ```python
  vdj_deck("load", deck_id=1, track_path="C:/Music/song.mp3")
  vdj_deck("play", deck_id=1)
  ```

---

### 🎚️ 2. MIXER CONTROL (`vdj_mixer`)
Control channel gains, EQs, headphones cueing, master levels, and audio effect slots.
* **Operations**: `crossfader`, `sync`, `eq_high`, `eq_mid`, `eq_low`, `gain`, `filter`, `master_volume`, `headphone_volume`, `headphone_mix`, `effect`, `eq_reset`
* **Parameters**:
  - `position` (float, -100 to +100, for `crossfader`, 0 = center)
  - `deck_a` & `deck_b` (int, for `sync`)
  - `deck_id` (int, for channel levels/EQs/effects)
  - `value` (float, 0-100%, for EQ/filter/volume, 0-150% for gain)
  - `effect_slot` (int, 0-2, default: 0)
  - `effect_type` (str, e.g., `"echo"`, `"flanger"`)
  - `enable` (bool, default: True)
  - `wet_dry` (float, 0-100)
  - `param1` / `param2` (float, 0.0-1.0)
* **Example**:
  ```python
  vdj_mixer("crossfader", position=0)  # Center crossfader
  vdj_mixer("sync", deck_a=1, deck_b=2)
  vdj_mixer("effect", deck_id=1, effect_type="echo", enable=True)
  ```

---

### 🔍 3. LIBRARY SEARCH (`vdj_library`)
Discover local tracks and perform audio parameter analysis.
* **Operations**: `search`, `analyze`
* **Parameters**:
  - `query` (str, search query)
  - `track_path` (str, required for `analyze`)
  - `limit` (int, max results, default: 50)
  - `artist` / `genre` / `key` / `bpm_min` / `bpm_max` (optional filters)
  - `sort_by` (str, default: `"relevance"`)
  - `sort_desc` (bool, default: True)
* **Example**:
  ```python
  vdj_library("search", query="ABBA", bpm_min=110, bpm_max=130)
  vdj_library("analyze", track_path="C:/Music/track.mp3")
  ```

---

### 🎥 4. VIDEO MIXING (`vdj_video`)
Manage video deck playback, fullscreen outputs, transitions, and video FX.
* **Operations**: `crossfader`, `transition`, `fx`, `text`, `output`, `karaoke`, `scratch`, `loop`, `tempo_sync`, `load`
* **Example**:
  ```python
  vdj_video("transition", transition_type="slide", duration=2.0)
  ```

---

### 🎙️ 5. STEM SEPARATION (`vdj_stems`)
Isolate vocals, instrumentals, melodies, and drum tracks in real time.
* **Operations**: `kill`, `unkill`, `volume`, `acapella`, `instrumental`, `isolate_drums`, `swap`, `reset`
* **Example**:
  ```python
  vdj_stems("acapella", deck_id=1)  # Mutes everything except vocals on deck 1
  ```

---

### 🖥️ 6. SYSTEM DASHBOARD (`vdj_system`)
Retrieve diagnostics, connection status, and view developer help files.
* **Operations**: `status`, `help`, `connection_test`
* **Example**:
  ```python
  vdj_system("status")
  ```

---

### 🌐 OTHER TOOLS
* `vdj_plex`: Search and load tracks directly from Plex Media Server.
* `vdj_automation`: Start Auto-DJ transition macros and get recommendations.
* `vdj_recording`: Start, stop, and list recordings of active sets.
* `vdj_beatgrid`: Manage loops, rolls, and beat positions.
* `vdj_skin`: Load visual skins and toggle custom UI panels.
* `vdj_performance`: Collect DJ session analytics and stats.

---

## 🚦 TROUBLESHOOTING

* **VirtualDJ not responding**:
  1. Ensure VirtualDJ is actively running on your machine.
  2. Verify that **Network Control** is enabled in Master panel → Master Effect.
  3. Try curl connection test:
     ```bash
     curl -X POST http://127.0.0.1:80/execute -H "Content-Type: text/plain" -d "nop"
     ```
* **Track failing to load**:
  1. Confirm that the exact track file path exists on the disk.
  2. Ensure the VirtualDJ library paths match the folder specified in your `VDJ_LIBRARY_PATH` env configuration.
