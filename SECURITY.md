# Security Policy

## Supported Versions

VirtualDJ-MCP follows semantic versioning and maintains security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in VirtualDJ-MCP, please report it responsibly.

### Contact
- **Email**: security@sandraschi.dev (create this email alias)
- **GitHub Security Advisories**: Use [GitHub's security advisory feature](https://github.com/sandraschi/virtualdj-mcp/security/advisories)

### What to Include
When reporting a vulnerability, please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if known)
- Your contact information for follow-up

### Our Process
1. **Acknowledgment**: We'll acknowledge receipt within 48 hours
2. **Investigation**: We'll investigate and validate the report
3. **Fix Development**: We'll develop and test a fix
4. **Disclosure**: We'll coordinate disclosure with you
5. **Release**: We'll release the fix with appropriate documentation

## Security Considerations

### Network Security
- VirtualDJ-MCP communicates with VirtualDJ via localhost only
- No external network connections required
- FastAPI server binds to localhost by default

### Data Protection
- No user data is transmitted externally
- Audio files and metadata remain local
- Configuration files may contain paths but no sensitive credentials

### Dependencies
- All dependencies are monitored for security vulnerabilities
- Regular dependency updates via Dependabot
- Security audits performed before major releases

## Known Security Considerations

### VirtualDJ Integration
- Requires local VirtualDJ installation
- VirtualDJ network settings must be properly configured
- API access should be restricted to localhost

### File System Access
- Reads audio files from configured library paths
- Writes recordings to configured output directories
- Respects file system permissions

### Environment Variables
- Sensitive configuration via environment variables
- No hardcoded credentials
- `.env` files should not be committed

## Best Practices for Users

### Installation
- Install in virtual environment
- Verify package signatures when available
- Keep dependencies updated

### Configuration
- Use strong, unique environment variable names
- Restrict file system access to necessary directories
- Regularly backup configuration files

### Operation
- Run with minimal required permissions
- Monitor logs for unusual activity
- Keep VirtualDJ and system updated

## Security Updates

Security updates will be:
- Released as patch versions (1.0.x)
- Documented in CHANGELOG.md
- Announced via GitHub releases
- Backported to supported versions when applicable

## Contact

For security-related questions or concerns:
- **Maintainer**: Sandra Schilling
- **Email**: sandra@sandraschi.dev
- **Response Time**: Within 48 hours for security issues

---

**Security is our priority. Thank you for helping keep VirtualDJ-MCP safe! 🔒**


