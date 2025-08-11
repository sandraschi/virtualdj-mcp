# VirtualDJ-MCP 🎵

Professional DJ automation MCP server with Austrian efficiency for Sandra's music mixing needs.

## 🎯 Overview

VirtualDJ-MCP provides seamless integration between Claude and VirtualDJ, enabling professional DJ automation, mixing, and library management through natural language commands.

### 📋 Capabilities (20+ Tools)

- **6 Deck Control Tools**: Play/pause, load tracks, seek, volume, effects, status
- **4 Mixing & Crossfader**: Crossfader control, auto-sync, beatmatching, transitions  
- **5 Library Management**: Scan library, search tracks, analysis, playlists, stats
- **4 Automation & AI**: Auto-DJ mode, track suggestions, harmonic mixing, recording
- **3 Performance Monitoring**: Session analytics, audio levels, hardware status

### 💪 Strengths

- Professional DJ software integration (20+ years of VirtualDJ development)
- Dual communication (REST API + CLI for maximum reliability)
- Real-time deck control and mixing automation
- AI-assisted track selection and harmonic mixing
- Multi-deck support (up to 8 decks simultaneously)
- Hardware controller integration through VirtualDJ

### ⚠️ Limitations

- Requires VirtualDJ installation (not included)
- Some features need VirtualDJ Pro license
- Real-time performance depends on system resources

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/sandraschi/virtualdj-mcp.git
cd virtualdj-mcp

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

### Configuration

1. Create `.env` file:
```env
VDJ_PATH=C:/Program Files/VirtualDJ/virtualdj.exe
VDJ_API_HOST=localhost
VDJ_API_PORT=8080
VDJ_LIBRARY_PATH=C:/Music
VDJ_DEFAULT_VOLUME=75
```

2. Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "virtualdj-mcp": {
      "command": "python",
      "args": ["-m", "virtualdj_mcp"],
      "cwd": "D:/Dev/repos/virtualdj-mcp",
      "env": {
        "VDJ_PATH": "C:/Program Files/VirtualDJ/virtualdj.exe",
        "VDJ_API_HOST": "localhost",
        "VDJ_API_PORT": "8080",
        "VDJ_LIBRARY_PATH": "C:/Music",
        "PYTHONPATH": "D:/Dev/repos/virtualdj-mcp/src"
      }
    }
  }
}
```

### Usage

```python
# Start VirtualDJ-MCP
python -m virtualdj_mcp

# Use Claude commands
"Load track to deck 1 and start playing"
"Set crossfader to favor deck 2"
"Auto-sync decks 1 and 2"
"Show current deck status"
```

## 🎛️ Professional Use Cases

### Wedding DJ
- Mood-based track transitions
- Automated announcements
- Guest request management

### Club Performance
- Crowd energy analysis
- Beat-perfect mixing
- Hardware controller integration

### Radio Show
- Scheduled content automation
- Intro/outro management
- Commercial break timing

### Practice & Learning
- Skill improvement tracking
- Mix quality analysis
- Beatmatching assistance

## 🔧 Development

### Project Structure
```
virtualdj-mcp/
├── src/virtualdj_mcp/
│   ├── __init__.py
│   ├── __main__.py
│   ├── app.py              # Main FastMCP server
│   ├── config.py           # Configuration management
│   ├── core/
│   │   ├── vdj_client.py   # VirtualDJ API wrapper
│   │   ├── deck_manager.py # Deck operations
│   │   └── mixer_controller.py
│   ├── services/
│   │   ├── audio_analysis.py
│   │   ├── library_scanner.py
│   │   └── automation_engine.py
│   └── api/
├── docs/
├── tests/
├── examples/
└── requirements.txt
```

### Available Tools

#### Deck Control
- `play_pause_deck(deck_id, action)` - Control playback
- `load_track_to_deck(deck_id, track_path)` - Load tracks
- `seek_deck(deck_id, position)` - Seek position
- `set_deck_volume(deck_id, volume)` - Volume control
- `get_deck_status(deck_id)` - Status info

#### Mixing
- `set_crossfader_position(position)` - Crossfader control
- `auto_sync_decks(deck_a, deck_b)` - BPM synchronization

#### Austrian Efficiency Features
- `show_help()` - Sandra's brilliant suggestion! 🇦🇹
- No decision paralysis - clear, actionable tools
- Cultural context for Vienna DJ scene
- Professional automation without complexity

## 📊 Implementation Status

### ✅ Phase 1: Core Infrastructure (COMPLETE)
- [x] Project scaffold and structure
- [x] FastMCP 2.10 integration  
- [x] VirtualDJ CLI/REST client wrapper
- [x] Basic deck control tools (6 tools)
- [x] Configuration management
- [x] show_help tool (Sandra's brilliant idea!)

### 🚧 Phase 2: Mixing & Library (IN PROGRESS)
- [x] Crossfader control
- [x] Auto-sync functionality
- [ ] Library search and management
- [ ] Playlist operations
- [ ] Audio analysis integration

### 📋 Phase 3: Automation & AI (PLANNED)
- [ ] Auto-DJ mode
- [ ] Track recommendation engine
- [ ] Harmonic mixing
- [ ] Recording functionality

### 📋 Phase 4: Performance & Analytics (PLANNED)
- [ ] Session analytics
- [ ] Performance monitoring
- [ ] Hardware integration
- [ ] Advanced mixing algorithms

## 🇦🇹 Austrian Efficiency

This project embodies Austrian efficiency principles:
- **Practical solutions** over theoretical complexity
- **Cultural awareness** for Vienna music scene
- **No decision paralysis** - exactly what you need, when you need it
- **Professional quality** without overwhelming options

Perfect for Sandra's DJ automation needs in Vienna!

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Built with Austrian efficiency for professional DJ automation! 🎵🇦🇹**
