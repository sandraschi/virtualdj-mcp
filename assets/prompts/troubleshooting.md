# Troubleshooting Guide - VirtualDJ-MCP

## Common Issues and Solutions

### Connection Issues

#### **Problem: VirtualDJ not responding to commands**

**Symptoms**:
- Commands timeout
- No response from VirtualDJ
- "VirtualDJ not found" errors

**Solutions**:
1. ✅ Verify VirtualDJ is running (`ps | Select-String "virtualdj"`)
2. ✅ Check CLI path is correct (typically `C:\Program Files\VirtualDJ\virtualdj.exe`)
3. ✅ Restart VirtualDJ
4. ✅ Check Windows firewall/antivirus
5. ✅ Run VirtualDJ as administrator

#### **Problem: Intermittent command failures**

**Solutions**:
- Reduce command frequency (wait for previous to complete)
- Check system resources (CPU/RAM usage)
- Close unnecessary applications
- Update VirtualDJ to latest version

### Audio Issues

#### **Problem: No sound output**

**Checklist**:
1. Master volume not muted (`get_master_volume`)
2. Deck volume not at zero (`deck_volume(deck=1)`)
3. Audio interface configured in VirtualDJ settings
4. Correct output device selected
5. Windows volume not muted

#### **Problem: Distorted/clipping audio**

**Solutions**:
- ✅ Reduce master volume to -6dB to -3dB headroom
- ✅ Lower individual deck gains
- ✅ Check EQ settings (not over-boosting)
- ✅ Verify audio interface bit depth/sample rate
- ✅ Check for CPU overload

#### **Problem: Latency/delay**

**Solutions**:
- Reduce audio buffer size in VirtualDJ settings
- Use ASIO driver if available
- Close background applications
- Check USB connection quality (audio interface)

### Playback Issues

#### **Problem: Track won't load**

**Checklist**:
1. File exists at specified path
2. File format supported (MP3, WAV, FLAC, AAC)
3. File not corrupted (play in media player)
4. Deck available (not already playing)
5. Sufficient disk space

#### **Problem: Sync not working properly**

**Solutions**:
- ✅ Verify BPM analysis is correct
- ✅ Manually beatmatch if BPM detection wrong
- ✅ Disable/re-enable sync
- ✅ Check for tempo drift (variable BPM tracks)
- ✅ Use manual pitch control for final adjustment

### Library/Search Issues

#### **Problem: Search returns no results**

**Checklist**:
1. Library database up-to-date (rescan if needed)
2. Search syntax correct
3. Tracks actually in library
4. File paths haven't changed
5. Database not corrupted

#### **Problem: Missing metadata**

**Solutions**:
- ✅ Analyze tracks in VirtualDJ (BPM/key detection)
- ✅ Update ID3 tags manually or with tool
- ✅ Re-import library
- ✅ Check file encoding (UTF-8)

### VirtualDJ-MCP Specific

#### **Problem: FastMCP server won't start**

**Checklist**:
1. Python version (3.11+ required)
2. Dependencies installed (`uv pip install -r requirements.txt`)
3. Port not in use (default MCP ports)
4. Check logs for errors
5. Virtual environment activated

#### **Problem: MCP tools not responding**

**Solutions**:
- ✅ Check MCP server logs
- ✅ Verify VirtualDJ connection
- ✅ Restart MCP server
- ✅ Check Claude Desktop config
- ✅ Validate JSON in config file

### Performance Issues

#### **Problem: Slow command execution**

**Possible causes**:
- VirtualDJ busy with other operations
- System resources limited
- Large library search
- Network latency (if using remote VirtualDJ)

**Solutions**:
- ✅ Increase command timeout
- ✅ Optimize library size
- ✅ Close unnecessary applications
- ✅ Upgrade hardware if consistently slow

#### **Problem: High CPU usage**

**Solutions**:
- Reduce visual effects in VirtualDJ
- Lower sample rate if acceptable
- Disable unnecessary features
- Check for malware/background processes

### Emergency Procedures

#### **Mid-Performance Technical Failure**

**Priority Order**:
1. **Keep music playing** (most important!)
2. Enable Auto-DJ immediately if available
3. Have backup track ready on alternate deck
4. Troubleshoot without interrupting music

**Emergency Kit**:
- Backup laptop with VirtualDJ
- Backup USB with emergency playlist
- Phone with essential tracks
- Hardware mixer (if available)

#### **Data Recovery**

**If VirtualDJ crashes/corrupts**:
1. Check Auto-Backup folder (VirtualDJ creates automatic backups)
2. Restore from manual backup
3. Re-analyze library if needed
4. Restore settings from backup

**Regular Backups** (Prevention):
- Daily: Critical playlists
- Weekly: Full library database
- Monthly: Complete music collection
- Before events: Everything

### Diagnostic Commands

#### **System Health Check**

```python
# Check VirtualDJ status
status = check_virtualdj_status()

# Get all deck statuses
for deck in range(1, 5):
    deck_info = get_deck_status(deck)
    print(f"Deck {deck}: {deck_info}")

# Check master volume
volume = get_master_volume()

# Verify automix status
automix = get_automix_status()
```

#### **Connection Test**

```python
# Simple command test
result = execute_vdjscript("get_version")

# Expected: VirtualDJ version number
# If error: Connection issue
```

### Getting Help

#### **In Order of Priority**:

1. **This troubleshooting guide** - Common issues covered
2. **VirtualDJ-MCP Documentation** - Check README, docs/
3. **VirtualDJ Forums** - Community support
4. **VirtualDJ Support** - Official help for VirtualDJ-specific issues
5. **GitHub Issues** - Bug reports, feature requests for MCP server

#### **When Reporting Issues**

**Include**:
- VirtualDJ version
- VirtualDJ-MCP version
- Operating system
- Error messages (exact text)
- Steps to reproduce
- Expected vs actual behavior

#### **Debug Mode**

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Capture detailed logs
# Check console output for diagnostic info
```

---

## Prevention Best Practices

### **Pre-Performance**:
- ✅ Test all equipment 1 hour before
- ✅ Verify audio output
- ✅ Load essential tracks
- ✅ Check library accessible
- ✅ Enable Auto-DJ as backup

### **During Performance**:
- ✅ Monitor levels constantly
- ✅ Keep backup tracks ready
- ✅ Save session periodically
- ✅ Watch for warnings/errors

### **Post-Performance**:
- ✅ Save recording if made
- ✅ Note any issues encountered
- ✅ Update library/playlists
- ✅ Backup session

---

**Remember**: Most issues have simple solutions. Stay calm, methodical troubleshooting solves 95% of problems. Austrian efficiency: Prepare well, prevent problems! 🇦🇹

