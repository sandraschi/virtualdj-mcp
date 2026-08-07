# VirtualDJ-MCP Development Environment Setup
# PowerShell script to create and configure Python virtual environment

param(
    [string]$PythonVersion = "3.10",
    [string]$VenvName = "vdj-mcp-env",
    [switch]$Force
)

Write-Host "ðŸŽµ VirtualDJ-MCP Environment Setup" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Yellow

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    Write-Host "âœ... Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "âŒ Python not found. Please install Python $PythonVersion or later." -ForegroundColor Red
    exit 1
}

# Check if virtual environment already exists
if ((Test-Path $VenvName) -and -not $Force) {
    Write-Host "âš ï¸  Virtual environment '$VenvName' already exists." -ForegroundColor Yellow
    Write-Host "   Use -Force to recreate it." -ForegroundColor Yellow
    exit 0
}

# Remove existing environment if forcing
if ((Test-Path $VenvName) -and $Force) {
    Write-Host "[delete]ï¸  Removing existing environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $VenvName
}

# Create virtual environment
Write-Host "ðŸ-ï¸  Creating virtual environment '$VenvName'..." -ForegroundColor Blue
try {
    python -m venv $VenvName
    Write-Host "âœ... Virtual environment created successfully" -ForegroundColor Green
} catch {
    Write-Host "âŒ Failed to create virtual environment: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "[sync] Activating virtual environment..." -ForegroundColor Blue
try {
    & "$VenvName/Scripts/Activate.ps1"
    Write-Host "âœ... Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "âŒ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "   You may need to run: & '$VenvName/Scripts/Activate.ps1'" -ForegroundColor Yellow
}

# Upgrade pip
Write-Host "â¬†ï¸  Upgrading pip..." -ForegroundColor Blue
try {
    python -m pip install --upgrade pip
    Write-Host "âœ... Pip upgraded successfully" -ForegroundColor Green
} catch {
    Write-Host "âš ï¸  Pip upgrade failed, continuing..." -ForegroundColor Yellow
}

# Install dependencies
Write-Host "ðŸ"¦ Installing dependencies..." -ForegroundColor Blue
try {
    pip install -r requirements.txt
    Write-Host "âœ... Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "âŒ Failed to install dependencies: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Install development dependencies
Write-Host "ðŸ"§ Installing development dependencies..." -ForegroundColor Blue
try {
    pip install -e ".[dev]"
    Write-Host "âœ... Development dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "âš ï¸  Development dependencies installation failed, continuing..." -ForegroundColor Yellow
}

Write-Host "" -ForegroundColor White
Write-Host "ðŸŽ‰ Setup Complete!" -ForegroundColor Green
Write-Host "" -ForegroundColor White
Write-Host "To activate the environment in future sessions:" -ForegroundColor Cyan
Write-Host "  & '$VenvName/Scripts/Activate.ps1'" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "To run the MCP server:" -ForegroundColor Cyan
Write-Host "  python -m mcp.server" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "To run the FastAPI server:" -ForegroundColor Cyan
Write-Host "  `$env:RUN_FASTAPI='true'; python -m mcp.server" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "To run tests:" -ForegroundColor Cyan
Write-Host "  python -m pytest tests/" -ForegroundColor White
Write-Host "" -ForegroundColor White


