# Changelog

All notable changes to VirtualDJ-MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Tauri native wrapper (native/ directory) with bundle.resources + std::process::Command
- CUA-NSIS: just cua-nsis-test recipe, scripts/cua-smoke.py, scripts/cua-nsis-config.json
- Tauri CORS: tauri://localhost origins for WebView API access
- NSIS installer at dist/ and native/target/release/bundle/nsis/
- Cross-MCP deck handoff endpoints for external orchestration:
  - `POST /api/v1/deck/{deck_id}/sync`
  - `POST /api/v1/deck/{deck_id}/cue` (`mode=start|cue|set_cue`)
- `/api/v1/diagnostics` endpoint for fleet health checks
- Dashboard health polling with data-testid attributes
- Zoom control (Ctrl+scroll) for Tauri WebView

### Changed
- Frontend API calls use absolute http://127.0.0.1:{port} URLs in production build
- CORS middleware includes allow_origin_regex for tauri.localhost
- README cleaned up — removed duplicated sections, consistent Python 3.12+
- `.env.example` updated with correct variable names matching config.py
- `native/build.ps1` bundles `.env.example` (not `.env`) for security
- `native/tauri.conf.json` references `.env.example` in resources
- Dashboard now shows live backend connection status with retry
- Added `@tauri-apps/api` for Tauri event/listen pattern

### Fixed
- README Python version inconsistency (3.10-3.11 vs >=3.12)
- Missing CURSOR_SETUP.md reference in README
- `.env.example` used wrong env var names (VDJ_API_HOST instead of VDJ_HTTP_HOST)
- Changelog format (removed stray headers outside document structure)
- Server lint baseline cleaned with repo-level Ruff configuration

## [1.0.1] - 2025-11-28

### Fixed
- VDJError import in tools/shared/exceptions.py
- aubio integration for DJ-grade BPM/pitch detection (with librosa fallback)
- mutagen moved from dev to main dependencies

### Changed
- Python version pinned to >=3.10,<3.12 (aubio lacks wheels for 3.12+)
- Audio analysis now uses aubio for accurate BPM detection, librosa as fallback

## [1.0.0] - 2025-01-24

### Added
- Dual interface: MCP (Claude Desktop) and FastAPI (REST API)
- FastMCP 2.12+ modular architecture
- Modular tool organization: deck_control, mixing, library, automation, recording
- FastAPI REST API with OpenAPI documentation at /api/docs
- Health monitoring at /health
- 20+ tools covering deck control, mixing, automation, recording
- Audio analysis: BPM detection, key analysis, energy/danceability scoring
- VirtualDJ REST API and CLI integration
- Environment-based configuration with .env support
- Testing infrastructure for MCP and FastAPI interfaces

## [0.1.0] - 2025-01-01

### Added
- Initial VirtualDJ-MCP prototype
- Basic deck control tools (5 tools)
- VirtualDJ CLI integration
- Basic configuration management
- Initial README and documentation
