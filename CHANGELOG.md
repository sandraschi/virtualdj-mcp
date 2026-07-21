
## [Unreleased] — 2026-06-14

### Added
- Tauri native wrapper (native/ directory) with bundle.resources + std::process::Command
- CUA-NSIS: just cua-nsis-test recipe, scripts/cua-smoke.py, scripts/cua-nsis-config.json
- Tauri CORS: tauri://localhost origins for WebView API access
- NSIS installer at dist/ and native/target/release/bundle/nsis/

### Changed
- Frontend API calls use absolute http://127.0.0.1:{port} URLs in production build
- CORS middleware includes allow_origin_regex for tauri.localhost
# Changelog

All notable changes to VirtualDJ-MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Cross-MCP deck handoff endpoints** for external orchestration:
  - `POST /api/v1/deck/{deck_id}/sync`
  - `POST /api/v1/deck/{deck_id}/cue` (`mode=start|cue|set_cue`)
- **API index updates** in `/api` for `deck_sync` and `deck_cue`.

### Changed
- **Server lint baseline** cleaned with repo-level Ruff configuration aligned to active runtime surfaces.
- **Security/runtime hygiene**:
  - exception chaining in API/client error paths
  - loopback bind for FastAPI runner (`127.0.0.1`)
  - status probing now logs errors instead of silent pass
  - non-crypto random and hash warnings addressed in active services

## [1.0.1] - 2025-11-28

### Fixed
- **VDJError Import**: Fixed missing `VDJError` export in `tools/shared/exceptions.py`
- **aubio Integration**: Added aubio for DJ-grade BPM/pitch detection (with librosa fallback)
- **Dependencies**: Moved `mutagen` from dev to main dependencies

### Changed
- **Python Version**: Pinned to `>=3.10,<3.12` (aubio lacks wheels for 3.12+)
- **Audio Analysis**: Now uses aubio for real-time accurate BPM detection, librosa as fallback
- **Key Detection**: Improved using librosa chroma features when aubio unavailable

### Technical Details
- aubio provides DJ-grade BPM accuracy (critical for beatmatching)
- Python 3.11 is the recommended version (fast, stable, wide library support)
- Audio analyzer auto-detects aubio availability and falls back gracefully

## [1.0.0] - 2025-01-24

### Added
- **Dual Interface Architecture**: Both MCP (Claude Desktop) and FastAPI (REST API) interfaces implemented
- **FastMCP 2.12+ Framework**: Upgraded to latest FastMCP with proper modular architecture
- **Modular Tool Organization**: Refactored from monolithic server.py to organized tool categories:
  - `deck_control/` - Deck playback, loading, seeking, volume control
  - `mixing/` - Crossfader, auto-sync, effects, EQ controls
  - `library/` - Track search, audio analysis, library management
  - `automation/` - Auto-DJ, playlist management, performance monitoring
  - `recording/` - Mix recording, export, session management
- **FastAPI REST API**: Complete REST API with OpenAPI documentation at `/api/docs`
- **Health Monitoring**: `/health` endpoint for system status
- **Professional DJ Tools**: 20+ tools covering deck control, mixing, automation, and recording
- **Audio Analysis**: BPM detection, key analysis, energy/danceability scoring
- **VirtualDJ Integration**: Full VirtualDJ REST API and CLI integration
- **Configuration Management**: Environment-based configuration with `.env` support
- **Testing Infrastructure**: Local test scripts for both MCP and FastAPI interfaces
- **PowerShell Support**: Windows/PowerShell compatibility throughout
- **Packaging**: Proper Python packaging with pyproject.toml and setup scripts

### Changed
- **Architecture Refactor**: Complete rewrite from 885-line monster server.py to thin, modular design
- **Entry Point**: Changed from `virtualdj_mcp` to `mcp.server` module
- **Dependencies**: Updated FastMCP to 2.12+, added FastAPI, uvicorn, and other dependencies
- **Directory Structure**: Reorganized to `src/mcp/` with tool categories
- **Configuration**: Updated Claude Desktop config for new module structure

### Technical Details
- **FastMCP Version**: 2.12.0+ (required for production)
- **Python Support**: 3.10, 3.11, 3.12
- **Platform**: Windows 10/11 (PowerShell compatible)
- **Dependencies**: 15 core packages properly declared
- **Tool Categories**: 5 organized categories with 20+ tools total
- **API Endpoints**: 7 REST endpoints with full OpenAPI documentation
- **Test Coverage**: Local test scripts for both interfaces

### Production Readiness
- ✅ Dual interface (MCP + FastAPI) implemented
- ✅ Modular architecture (no monster server.py)
- ✅ FastMCP 2.12+ framework
- ✅ Comprehensive testing infrastructure
- ✅ Professional documentation
- ✅ PowerShell/Windows compatibility
- ✅ Proper packaging and distribution

## [0.1.0] - 2025-01-01

### Added
- Initial VirtualDJ-MCP prototype
- Basic deck control tools (5 tools)
- VirtualDJ CLI integration
- Basic configuration management
- Initial README and documentation

### Known Issues
- Monolithic server architecture (885-line server.py)
- Missing FastAPI interface
- Limited testing infrastructure
- Basic documentation only



