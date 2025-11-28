# MCPB Format Status & Limitations

**Last Updated**: November 2025  
**MCPB Version**: 1.1.1  
**Status**: Claude Desktop Only - Limited Adoption  
**Applicable To**: All MCP Servers

---

## Why MCPB Failed to Gain Widespread Adoption

### 1. **Claude Desktop Exclusivity**

MCPB (Model Context Protocol Bundle) was designed specifically for Claude Desktop's extension system. While Anthropic intended it to become a universal standard, it never gained traction outside Claude Desktop:

- **No other major MCP clients adopted it**: Cursor IDE, Windsurf, Zed, and other MCP-compatible tools use standard JSON-RPC configuration
- **Vendor lock-in**: The format is tightly coupled to Claude Desktop's UI and extension system
- **Limited ecosystem**: Without broad client support, MCPB remains a niche format

### 2. **Weird Installation UX**

The "drag-and-drop into Claude Desktop settings UI" approach is unconventional:

- **Not intuitive**: Users expect traditional installers or package managers
- **No version management**: Difficult to update or uninstall cleanly
- **Manual process**: Requires users to navigate to settings, find the extensions panel, and drag files
- **No dependency resolution**: Users must manually ensure prerequisites are met

### 3. **Lack of Standard Tooling**

Unlike established formats (npm, pip, cargo), MCPB lacks:

- **Package registry**: No central repository for discovery
- **Version management**: No semantic versioning enforcement
- **Dependency resolution**: No automatic dependency handling
- **Update mechanisms**: No built-in update system
- **Uninstall process**: Removal requires manual cleanup

### 4. **Competing Standards**

The MCP ecosystem already has better alternatives:

- **Standard MCP config**: Works across all clients (Cursor, Windsurf, Zed, Claude Desktop)
- **NPX**: Universal Node.js package execution
- **Local installation**: Direct git clone + pip install (most flexible)

---

## What MCPB Does Well: Prompt Templates

The **one genuinely useful feature** of MCPB is its prompt template system:

### How It Works

MCPB packages can include prompt templates that Claude Desktop automatically loads:

```json
{
  "prompts": [
    {
      "name": "system",
      "description": "System prompt defining capabilities",
      "text": "prompts/system.md"
    },
    {
      "name": "user",
      "description": "User guide and examples",
      "text": "prompts/user.md"
    }
  ]
}
```

### Why Prompts Are Useful

1. **System context**: Provides Claude with detailed information about your MCP server's capabilities
2. **User guidance**: Helps users understand how to interact with your tools
3. **Example interactions**: Shows Claude expected usage patterns
4. **Consistent behavior**: Ensures Claude understands your server's purpose and limitations

---

## Recommendation

### Keep MCPB For:
- ✅ Claude Desktop users who want one-click installation
- ✅ Users who specifically request MCPB format
- ✅ Maintaining prompt template structure (useful reference)

### Prefer Other Methods For:
- ⭐ **NPX Installation** - Universal, works with all MCP clients
- ⭐ **Local Installation** - Most flexible, best for development
- ⭐ **Standard MCP Config** - Works everywhere, no vendor lock-in

### Best Practice:
1. **Primary**: Document NPX and local installation methods prominently
2. **Secondary**: Keep MCPB as optional convenience for Claude Desktop users
3. **Prompts**: Use prompt templates as documentation reference for all users
4. **Tool Docs**: Embed key prompt content in tool docstrings (universal compatibility)

---

## Current Status

- **MCPB Version**: 1.1.1 (latest)
- **Client Support**: Claude Desktop only
- **Maintenance**: Low priority (kept for Claude Desktop users)
- **Recommendation**: Use NPX or local installation for broader compatibility

---

## Bottom Line

- **MCPB format**: Failed standard attempt - Claude Desktop only, limited adoption
- **Prompt templates**: Genuinely useful for providing structured usage scenarios and example interactions
- **Recommendation**: Keep prompt templates as they provide value beyond what docstrings can offer. MCPB remains optional, but the prompt templates themselves are worth maintaining.

---

**This document applies to all MCP servers in the ecosystem.**  
**Consider this when deciding whether to support MCPB packaging.**

