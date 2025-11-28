# Changelog

All notable changes to VirtualDJ-MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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


