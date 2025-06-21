# Security Policy

## 🛡️ Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | ✅ Yes             |
| < 1.0   | ❌ No              |

## 🔒 Security Best Practices

### When Using This Software

1. **Environment Variables**: Always use environment variables or `.env` files for sensitive data
2. **Container Security**: Run containers as non-root users (default behavior)
3. **Network Security**: Limit network access to only required endpoints
4. **Credential Management**: Rotate your Prusa Connect tokens regularly
5. **Updates**: Keep the software updated to the latest version

### Configuration Security

- ✅ **Do**: Use environment variables for `FINGERPRINT` and `TOKEN`
- ✅ **Do**: Use HTTPS for all HTTP endpoints
- ✅ **Do**: Validate RTSP URLs before use
- ❌ **Don't**: Hardcode credentials in configuration files
- ❌ **Don't**: Commit `.env` files to version control
- ❌ **Don't**: Use plain HTTP for sensitive data

## 🚨 Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 📧 Contact Information

**For security issues, please email privately:**
- **Email**: [security@example.com] <!-- Replace with actual email -->
- **Subject**: `[SECURITY] Prusa Connect Webcam Uploader - [Brief Description]`

### 📋 What to Include

When reporting a vulnerability, please include:

1. **Description**: Clear description of the vulnerability
2. **Impact**: Potential security impact and affected components
3. **Reproduction**: Steps to reproduce the issue
4. **Environment**: Affected versions and configurations
5. **Suggested Fix**: If you have ideas for mitigation

### 🔄 Response Process

1. **Acknowledgment**: We'll acknowledge receipt within 48 hours
2. **Assessment**: We'll assess the severity and impact within 5 business days
3. **Fix Development**: We'll work on a fix with priority based on severity
4. **Disclosure**: We'll coordinate responsible disclosure with you

### 🏆 Security Hall of Fame

We appreciate security researchers who help improve our project. With your permission, we'll recognize your contribution in:
- Project documentation
- Security advisories
- Release notes

## 🔒 Security Features

### Current Security Measures

- **Container Security**: Non-root user execution
- **Dependency Management**: Regular dependency updates
- **Input Validation**: Validation of configuration parameters
- **Error Handling**: Secure error messages without information disclosure
- **Logging**: Security-conscious logging practices

### Planned Security Enhancements

- [ ] Automated security scanning in CI/CD
- [ ] SBOM (Software Bill of Materials) generation
- [ ] Enhanced input validation
- [ ] Security audit logging

## 📚 Security Resources

### Documentation
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Python Security Guidelines](https://python-security.readthedocs.io/)
- [OWASP Container Security](https://owasp.org/www-project-docker-top-10/)

### Tools
- [Safety](https://pyup.io/safety/) - Python dependency vulnerability scanner
- [Bandit](https://bandit.readthedocs.io/) - Python security linter
- [Docker Bench](https://github.com/docker/docker-bench-security) - Docker security audit

## 🚫 Out of Scope

The following are generally considered out of scope for security reports:

- Issues requiring physical access to the host system
- Social engineering attacks
- Vulnerabilities in third-party dependencies (report to upstream)
- Issues that require admin/root access to exploit
- Theoretical attacks without practical exploit

However, if you're unsure, please err on the side of caution and report it.

---

**Thank you for helping keep our project and users secure! 🛡️**
