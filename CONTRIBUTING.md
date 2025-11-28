# Contributing to VirtualDJ-MCP

Thank you for your interest in contributing to VirtualDJ-MCP! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites
- Python 3.10 or later
- VirtualDJ installation (for testing)
- Windows 10/11 (primary development platform)
- PowerShell 7+ (for scripts)

### Quick Setup
```powershell
# Clone repository
git clone https://github.com/sandraschi/virtualdj-mcp.git
cd virtualdj-mcp

# Run automated setup
.\setup_venv.ps1

# Activate environment
& vdj-mcp-env/Scripts/Activate.ps1
```

## Development Workflow

### 1. Choose an Issue
- Check [Issues](../../issues) for open tasks
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to indicate you're working on it

### 2. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Changes
- Follow the existing code style and architecture
- Add tests for new functionality
- Update documentation as needed
- Ensure PowerShell compatibility

### 4. Test Your Changes
```bash
# Run MCP interface tests
python tests/local/test_mcp_interface.py

# Run FastAPI interface tests
python tests/local/test_fastapi_interface.py

# Run unit tests
python -m pytest tests/unit/

# Test manually with Claude Desktop
python -m mcp.server  # in Claude config
```

### 5. Commit and Push
```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

### 6. Create Pull Request
- Use a clear, descriptive title
- Fill out the PR template
- Reference any related issues
- Request review from maintainers

## Code Guidelines

### Architecture
- **Thin Server**: Keep `src/mcp/server.py` under 150 lines
- **Modular Tools**: All logic in `src/mcp/tools/` subdirectories
- **Category Organization**: Group related tools by functionality
- **Dual Interface**: Support both MCP and FastAPI interfaces

### Python Style
- Type hints throughout
- Black formatting (100 char line length)
- isort import sorting
- Descriptive variable/function names

### PowerShell Compatibility
- No Linux syntax (`&&`, `||`)
- Use PowerShell cmdlets (`New-Item`, `Copy-Item`)
- File redirect pattern: `Command > temp.txt; Get-Content temp.txt`
- Quote paths with spaces: `"C:\Program Files\"`
- Backslashes for Windows paths

### Error Handling
- Comprehensive try/catch blocks
- User-friendly error messages
- Graceful degradation on failures
- Proper logging with rich console

## Tool Development

### Adding New Tools
1. **Choose Category**: Add to appropriate `src/mcp/tools/` subdirectory
2. **Create Models**: Define Pydantic models in `models.py`
3. **Implement Tool**: Add tool function with `@mcp.tool()` decorator
4. **Setup Function**: Create `setup_*_tools(mcp)` function
5. **Register Tool**: Import and call setup function in `server.py`

### FastAPI Endpoints
1. **Add Route**: Add endpoint to `src/virtualdj_mcp/api/app.py`
2. **Pydantic Models**: Define request/response models
3. **Documentation**: Include proper docstrings
4. **Error Handling**: HTTP status codes and error responses

### Example Tool Structure
```python
# src/mcp/tools/category/models.py
from pydantic import BaseModel, Field

class ExampleRequest(BaseModel):
    parameter: str = Field(description="Parameter description")

class ExampleResponse(BaseModel):
    result: str = Field(description="Result description")

# src/mcp/tools/category/tools.py
from fastmcp import MCP
from .models import ExampleRequest, ExampleResponse

def setup_category_tools(mcp: MCP):
    @mcp.tool()
    async def example_tool(parameter: str) -> ExampleResponse:
        """Tool description"""
        # Implementation
        return ExampleResponse(result="output")
```

## Testing

### Local Tests
- `tests/local/test_mcp_interface.py` - MCP interface validation
- `tests/local/test_fastapi_interface.py` - FastAPI interface validation

### Unit Tests
- `tests/unit/` - Individual tool/component tests
- Use pytest framework
- Mock external dependencies

### Integration Tests
- `tests/integration/` - End-to-end workflow tests
- Test with actual VirtualDJ when possible
- Validate both interfaces

## Documentation

### Code Documentation
- Docstrings for all public functions
- Type hints for parameters and return values
- Inline comments for complex logic

### User Documentation
- Update README.md for new features
- Add examples to `examples/` directory
- Update prompt templates in `dxt/prompts/`

### API Documentation
- OpenAPI schema auto-generated
- REST endpoint documentation
- Tool parameter descriptions

## Commit Messages

Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

## Issue Reporting

When reporting bugs:
1. Use the bug report template
2. Include VirtualDJ version and edition
3. Provide MCP server logs
4. Describe steps to reproduce
5. Include system information

## Community

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions
- **Wiki**: Detailed documentation and guides

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Built with Austrian efficiency for professional DJ automation! 🎵🇦🇹**

