# FastMCP 2.13+ Migration Guide

**Date:** 2025-11-24  
**Status:** Official Standard  
**Applies to:** All MCP projects using FastMCP 2.12+

---

## 🎯 Overview

This guide covers migration from FastMCP 2.11 and earlier to FastMCP 2.13+, including:
- **FastMCP 2.12**: Tool documentation changes (docstring-based)
- **FastMCP 2.13**: Persistent storage, server lifespans, security fixes

---

## 📋 FastMCP 2.12 Changes: Tool Documentation

**FastMCP 2.12 changed how tool documentation works:**

### ❌ OLD Way (Pre-2.12)
```python
@mcp.tool(
    description="""This tool does something cool.
    
    It has many features and options.
    Use it when you need to do things."""
)
async def my_tool(param: str) -> str:
    """Just a basic docstring."""
    return "result"
```

### ✅ NEW Way (FastMCP 2.12+)
```python
@mcp.tool
async def my_tool(param: str) -> str:
    '''This tool does something cool with comprehensive documentation.
    
    FEATURES:
    - Feature 1 explained
    - Feature 2 explained
    - Feature 3 explained
    
    Args:
        param: Parameter description with type and purpose
        
    Returns:
        Result description with format details
        
    Examples:
        Basic usage: my_tool("value")
        Advanced: my_tool("complex-value")
        
    Notes:
        - Important note 1
        - Important note 2
    '''
    return "result"
```

---

## 🚨 Critical Rule

**NEVER use `description=` parameter in `@mcp.tool()`**

### Why?

**The description parameter OVERRIDES the docstring!**
- FastMCP reads docstring for tool info
- If description= exists, it uses THAT instead
- Your beautiful docstring gets ignored!
- Documentation becomes split between two places

---

## ✅ The Correct Pattern

### For Simple Tools

```python
@mcp.tool
async def simple_tool(name: str) -> str:
    '''Do a simple operation.
    
    Args:
        name: The name to process
        
    Returns:
        Processed result
        
    Example:
        simple_tool("test")
    '''
    return f"Processed: {name}"
```

### For Complex Tools (Portmanteau)

```python
from typing import Literal

@mcp.tool
async def portmanteau_tool(
    operation: Literal["create", "read", "update", "delete"],
    identifier: str | None = None,
    data: dict | None = None,
) -> str:
    '''Comprehensive tool that does multiple related operations.
    
    SUPPORTED OPERATIONS:
    - create: Create new resource
    - read: Retrieve resource
    - update: Modify resource
    - delete: Remove resource
    
    Args:
        operation: The operation to perform (create/read/update/delete)
        identifier: Resource identifier
        data: Resource data for create/update operations
        
    Returns:
        Operation-specific result with status and details
    '''
    # Implementation
```

---

## 🆕 FastMCP 2.13 Changes: Persistent Storage & Server Lifespans

### **Key Features in 2.13+**

**FastMCP 2.13+ introduces:**
- **Persistent storage backends** - Cross-session persistence (survives Claude Desktop and OS restarts)
- **Server lifespans** - Proper startup/shutdown lifecycle management
- **Security fixes** - CVE-2025-62801 (command injection), CVE-2025-62800 (XSS)
- **Storage backends** - `py-key-value-aio` with DiskStore support

### **Version Requirements**

```toml
[project]
dependencies = [
    "fastmcp>=2.13.0,<2.14.0",  # Pin to 2.13.x for security patches
    "py-key-value-aio[disk]>=1.0.0",  # For persistent storage (optional)
]
```

### **Server Lifespan Support**

**FastMCP 2.13+ requires server lifespan for persistent storage:**

```python
from contextlib import asynccontextmanager
from fastmcp import FastMCP

@asynccontextmanager
async def server_lifespan(mcp_instance: FastMCP):
    """Server lifespan for startup and cleanup."""
    # Startup initialization
    logger.info("Server starting up")
    
    yield  # Server runs here
    
    # Cleanup
    logger.info("Server shutting down")

# Initialize FastMCP with lifespan
mcp = FastMCP("app-name", lifespan=server_lifespan)
```

### **Migration Checklist for 2.13+**

- [ ] Upgrade `fastmcp>=2.13.0,<2.14.0` in `pyproject.toml`
- [ ] Add server lifespan if using persistent storage
- [ ] Implement storage wrapper if stateful
- [ ] Review security: validate inputs, no command injection risks
- [ ] Test persistence across Claude Desktop restarts
- [ ] Verify storage location is correct for your platform

---

## 🚨 Critical: Logging and stdout/stderr Rules

### ⚠️ **NEVER Write to stdout!**

**Claude Desktop uses stdout for MCP protocol communication. Writing to stdout breaks the protocol!**

```python
# ❌ BAD - NEVER do this!
print("Server started")  # Breaks Claude Desktop!

# ✅ GOOD - stderr handler for server logs
import sys
import logging
stderr_handler = logging.StreamHandler(sys.stderr)
root_logger.addHandler(stderr_handler)  # Safe for Claude Desktop!
```

### ❌ **No Emojis in Log Messages**

```python
# ❌ BAD - Emojis in log messages
logger.info("✅ Server started successfully")  # Don't use emojis!

# ✅ GOOD - Plain text log messages
logger.info("Server started successfully", status="ok")
```

---

## 📋 Checklist for Each Tool

### Minimum (All Tools)

- [ ] No `description=` parameter in `@mcp.tool()`
- [ ] Docstring exists (not just pass)
- [ ] Purpose clearly stated
- [ ] Args documented with types
- [ ] Returns documented
- [ ] At least 1 example

### Recommended (Quality)

- [ ] Single quote docstrings `'''`
- [ ] Multiple examples
- [ ] Edge cases noted
- [ ] Error conditions documented
- [ ] Related tools mentioned

---

## 🚀 Benefits of Migration

**Better Tool Discovery:**
- FastMCP reads rich docstrings
- AI gets full context
- Better parameter understanding

**Single Source of Truth:**
- Documentation in ONE place (docstring)
- No parameter/docstring conflicts
- Easier to maintain

**Cleaner Code:**
- No multi-line decorator parameters
- Readable tool definitions
- Consistent pattern

**Future-Proof:**
- FastMCP 2.12+ standard
- Matches MCP ecosystem best practices
- Won't need another migration

---

**Last Updated:** 2025-11-24  
**Review:** When FastMCP updates (check changelog)

