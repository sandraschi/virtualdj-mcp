# MCPB Packaging Standards

**Version:** 1.0  
**Date:** 2025-10-24  
**Status:** Official Standard  
**Applies to:** All MCP projects using MCPB packaging

---

## 🎯 **Overview**

**MCPB (Model Context Protocol Bundle) is the packaging format used EXCLUSIVELY for Claude Desktop installations.** This document defines the complete standards for MCPB packaging.

### ⚠️ **Critical MCPB Requirements**

1. **NO Dependencies**: MCPB packages must NOT include any Python dependencies or libraries. Claude Desktop provides its own Python runtime and dependencies must be installed separately by the user.

2. **Extensive Prompt Templates**: MCPB packages MUST include comprehensive prompt templates in the `prompts/` directory. These templates are read by Claude Desktop to understand how to interact with your MCP server.

3. **Claude Desktop Only**: MCPB format is ONLY used for Claude Desktop. For other MCP clients (Cursor, Windsurf, etc.), use standard MCP server installation methods (npm/npx or local installation).

4. **Weird Installation**: MCPB packages are installed by dragging the `.mcpb` file into Claude Desktop settings. There is no command-line installer.

---

## 📦 **MCPB Package Structure**

### **Required Files**

```
mcp-server/
├── manifest.json          # MCPB manifest configuration
├── assets/                # Package assets
│   ├── icon.png          # Package icon
│   ├── screenshots/      # Screenshots for documentation
│   └── prompts/          # EXTENSIVE prompt templates (REQUIRED)
│       ├── system.md     # System prompt for Claude Desktop
│       ├── user.md       # User interaction templates
│       └── examples.json # Usage examples
├── src/                  # Source code ONLY (no dependencies)
│   └── package_name/
│       ├── __init__.py
│       ├── mcp_server.py
│       └── tools/
└── README.md            # Package documentation
```

### ⚠️ **What MCPB Packages MUST NOT Include**

- ❌ **NO `requirements.txt`** - Dependencies are NOT bundled
- ❌ **NO `pyproject.toml`** - Not used by Claude Desktop
- ❌ **NO `lib/` or `dependencies/` directories** - No bundled libraries
- ❌ **NO virtual environments** - Claude Desktop provides Python runtime

### ✅ **What MCPB Packages MUST Include**

- ✅ **Extensive `prompts/` directory** - Comprehensive prompt templates for Claude Desktop
- ✅ **Source code only** - Just your Python server code
- ✅ **Clear documentation** - README explaining installation and configuration

---

## 📋 **Manifest Configuration**

### **Required Manifest Structure**

```json
{
  "manifest_version": "0.2",
  "server": {
    "type": "python",
    "entry_point": "src/package_name/mcp_server.py",
    "mcp_config": {
      "command": "python",
      "args": ["-m", "package_name.mcp_server"],
      "env": {
        "PYTHONPATH": "${PWD}",
        "PYTHONUNBUFFERED": "1"
      }
    }
  },
  "user_config": {
    "api_key": {
      "type": "string",
      "title": "API Key",
      "required": true,
      "default": ""
    },
    "timeout": {
      "type": "string",
      "title": "Operation Timeout (seconds)",
      "default": "30"
    }
  },
  "tools": [
    {
      "name": "tool_name_1",
      "description": "Brief description of what this tool does"
    },
    {
      "name": "tool_name_2",
      "description": "Brief description of what this tool does"
    }
  ],
  "compatibility": {
    "platforms": ["win32", "darwin", "linux"],
    "python": ">=3.10"
  }
}
```

---

## 🔧 **Build Process**

### **MCPB CLI Installation**

```bash
# Install MCPB CLI
npm install -g @anthropic-ai/mcpb

# Verify installation
mcpb --version
```

### **Package Building**

```bash
# Build MCPB package
mcpb pack . dist/package-name-v{version}.mcpb

# Build with validation
mcpb pack . dist/package-name-v{version}.mcpb --validate

# Build with signing (if configured)
mcpb pack . dist/package-name-v{version}.mcpb --sign
```

### **Package Validation**

```bash
# Validate manifest
mcpb validate manifest.json

# Validate package
mcpb validate dist/package-name-v{version}.mcpb
```

---

## 📁 **Assets Directory**

### **Required Assets**

```
assets/
├── icon.png              # Package icon (256x256px)
├── screenshots/          # Screenshots for documentation
│   ├── dashboard.png
│   ├── configuration.png
│   └── usage.png
└── prompts/             # EXTENSIVE prompt templates (REQUIRED)
    ├── system.md        # System prompt (REQUIRED)
    ├── user.md          # User interaction templates (REQUIRED)
    ├── examples.json    # Usage examples (REQUIRED)
    ├── quick-start.md   # Quick start guide
    ├── configuration.md # Configuration guide
    └── troubleshooting.md # Troubleshooting guide
```

### **Prompts (CRITICAL - REQUIRED)**
- **Purpose**: Claude Desktop reads these to understand your MCP server
- **Format**: Markdown for text, JSON for structured data
- **Content**: MUST be extensive and comprehensive
- **Why Required**: Claude Desktop uses these prompts to generate appropriate tool calls and responses

---

## 🔍 **Quality Standards**

### **Package Validation**

- **Manifest validation**: All required fields present
- **Tool registration**: All tools properly registered
- **Asset validation**: All required assets present
- **Python validation**: Code quality and testing

### **Testing Requirements**

- **Unit tests**: All tools and functions tested
- **Integration tests**: End-to-end workflows tested
- **Coverage**: 80%+ code coverage
- **Quality gates**: Ruff linting, security scanning

---

## 📦 **Distribution**

### **Package Distribution**

- **GitHub Releases**: Automated package releases (`.mcpb` files)
- **Claude Desktop Only**: MCPB packages are ONLY for Claude Desktop
  - Installation: Drag-and-drop `.mcpb` file into Claude Desktop settings
  - No command-line installer available
- **Other MCP Clients**: Use standard installation methods (npm/npx or local clone)

---

*Document created: October 24, 2025*  
*Status: Official Standard*  
*Last Updated: November 2025*

