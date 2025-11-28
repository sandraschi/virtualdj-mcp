# Library Management Guide - VirtualDJ-MCP

## Professional Music Library Organization

### Library Structure Best Practices

#### **Folder Organization**
```
Music Library/
├── Genre/
│   ├── House/
│   ├── Techno/
│   ├── Hip-Hop/
│   └── ...
├── BPM Ranges/
│   ├── 110-120/
│   ├── 120-130/
│   └── ...
├── Energy Levels/
│   ├── Warm-Up/
│   ├── Peak-Time/
│   └── Cool-Down/
└── Special/
    ├── Classics/
    ├── Requests/
    └── Transitions/
```

#### **Metadata Essentials**
- **BPM**: Always accurate
- **Key**: Harmonic mixing capability
- **Genre**: Primary classification
- **Energy**: 1-10 scale (custom tag)
- **Rating**: 1-5 stars (track quality)
- **Comments**: Mix notes, cue points, special info

### Search Strategies

#### **By BPM Range**
```python
# Find tracks for house set (125-130 BPM)
search_library(query="house", min_bpm=125, max_bpm=130)

# Find compatible tracks (±5 BPM from current)
current_bpm = 128
search_library(min_bpm=current_bpm-5, max_bpm=current_bpm+5)
```

#### **By Harmonic Key**
```python
# Find tracks in same key
search_library(key="8A")  # A minor

# Find compatible keys (Camelot wheel ±1)
compatible_keys = ["7A", "8A", "9A", "8B"]
```

#### **By Energy/Mood**
```python
# High-energy peak-time tracks
search_library(query="peak energy vocals")

# Warm-up selections
search_library(query="warm-up melodic chill")

# Genre-specific searches
search_library(query="techno dark driving", min_bpm=130, max_bpm=135)
```

### Playlist Management

#### **Essential Playlists**
1. **Warm-Up**: 110-120 BPM, mellow, building
2. **Main Set**: Genre-appropriate, high-energy
3. **Peak Time**: Crowd favorites, anthems
4. **Cool-Down**: Gradually reducing energy
5. **Requests/Classics**: Popular, recognizable

#### **Dynamic Playlists** (Smart Playlists)
- Tracks added in last 30 days
- High-rated tracks (4-5 stars)
- Never/rarely played tracks
- BPM-specific playlists (auto-updating)

#### **Set Planning Playlists**
- Pre-planned track order for specific events
- Backup track selections
- Genre-crossover transitions
- Special occasion mixes

### Track Analysis

#### **Pre-Performance Check**
```python
# Get comprehensive track info before loading
track_info = get_track_info(track_path)

Check:
- BPM (correct? needs adjustment?)
- Key (compatible with current/upcoming?)
- Duration (too long/short for set?)
- Cue points (set properly?)
- Quality (bitrate acceptable?)
```

#### **Track Ratings System**
```
5 stars: Peak-time bangers, always work
4 stars: Solid tracks, use frequently
3 stars: Good filler, situational
2 stars: Rarely use, specific contexts
1 star: Remove or re-evaluate
```

### VirtualDJ-MCP Library Tools

#### **Browse Library**
```python
# Navigate folder structure
browse_library(folder="D:/Music/House")
browse_library(folder="D:/Music/BPM Ranges/120-130")
```

#### **Search Library**
```python
# Text search
search_library(query="artist name")
search_library(query="track title")
search_library(query="genre techno")

# Combined criteria
search_library(query="house", min_bpm=125, max_bpm=128)
```

#### **Get Track Information**
```python
# Before loading to deck
track_details = get_track_info("path/to/track.mp3")

Returns:
- Title, Artist, Album
- BPM, Key, Duration
- Bitrate, File format
- Cue points, rating
```

### Library Maintenance

#### **Regular Tasks** (Weekly/Monthly)
- Remove duplicates
- Update BPM/key analysis
- Add new acquisitions
- Delete unused/poor quality tracks
- Update ratings based on performance
- Backup library database

#### **Quality Control**
```
Check for:
- Correct BPM analysis (verify manually if needed)
- Accurate key detection
- Proper ID3 tags (artist, title, album)
- Bitrate minimum (320kbps MP3 or FLAC)
- No corrupted files
```

#### **Backup Strategy**
```
Regular backups of:
- Music files (external drive)
- VirtualDJ database (playlists, cue points, ratings)
- Custom mappings/settings
- Performance history
```

---

## Library Optimization Tips

### **Do**:
- ✅ Maintain consistent folder structure
- ✅ Tag metadata properly and completely
- ✅ Regular library cleanup
- ✅ Test new tracks before live use
- ✅ Keep library size manageable (easier to navigate)

### **Don't**:
- ❌ Mix different genres in same folder (unless intentional)
- ❌ Ignore poor quality files
- ❌ Forget to backup
- ❌ Over-complicate organization
- ❌ Add untested tracks to performance playlists

---

**VirtualDJ-MCP** makes library browsing, searching, and track analysis seamless. Invest time in organization now for effortless performances later!

