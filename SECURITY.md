# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via:

1. **Email**: Send an email to security@summy.example.com with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
   - Your contact information for follow-up

2. **GitHub Private Vulnerability Reporting**: Use the [Private Vulnerability Reporting](https://github.com/anydockerhub/summy/security/advisories/new) feature

### What to Expect

- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Resolution Timeline**: Depends on severity, typically 7-30 days

### Security Best Practices

When deploying this project, follow these security recommendations:

#### Environment Variables

- Never commit `.env` files to version control
- Use strong, unique values for all secrets
- Rotate credentials regularly
- Use environment-specific configurations

#### Network Security

- Deploy behind a reverse proxy (nginx, traefik)
- Use TLS/SSL for all external communications
- Restrict access to metrics endpoints
- Implement rate limiting for public APIs

#### Container Security

- Run containers as non-root user (already configured in Dockerfile)
- Scan images for vulnerabilities: `docker scan summy`
- Keep base images updated
- Use minimal base images when possible

#### Database Security

- Enable WAL mode for better concurrency (default)
- Set appropriate file permissions on database files
- Regular backups
- Encrypt sensitive data at rest

#### Access Control

- Implement authentication for admin endpoints
- Use API keys for service-to-service communication
- Apply principle of least privilege
- Audit access logs regularly

### Known Limitations

- SQLite is used for simplicity; consider PostgreSQL for production workloads with high concurrency
- Default routing threshold may need adjustment based on your specific use case
- Metrics endpoint should be restricted in production environments

### Security Updates

Security patches will be released as patch versions (e.g., 1.0.1). Subscribe to releases or watch the repository for notifications.

### Responsible Disclosure

We follow responsible disclosure practices:
- Acknowledge reporters (unless they prefer anonymity)
- Provide timely fixes
- Publish security advisories for significant issues
- Credit researchers in CHANGELOG.md

Thank you for helping keep Intelligent Request Router secure!
