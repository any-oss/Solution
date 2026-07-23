# Security Policy

## Supported Versions

We release patches for security vulnerabilities regularly. The following versions are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Intelligent Request Router seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email at [security@example.com](mailto:security@example.com) or create a draft security advisory on GitHub.

### What to Include

To help us triage your report quickly, please include the following information in your report:

* A description of the vulnerability and its impact
* Step-by-step instructions to reproduce the issue
* Any relevant logs, screenshots, or code snippets
* Your suggested fix (if any)

### Response Timeline

You should receive a response from us within 48 hours acknowledging your report. After the initial reply, we will keep you informed of the progress toward a fix and announcement.

### Disclosure Policy

Once a security issue is reported, we will:

1. Investigate the report and confirm the vulnerability
2. Develop a fix and test it thoroughly
3. Release a patched version
4. Publicly disclose the issue after users have had time to update

We appreciate your responsible disclosure and will acknowledge your contribution when the issue is resolved.

## Security Best Practices

When deploying Intelligent Request Router, please follow these security best practices:

* **Keep dependencies up to date**: Regularly update your dependencies to patch known vulnerabilities
* **Use environment variables**: Never hardcode sensitive credentials in your code
* **Enable HTTPS**: Always use HTTPS in production environments
* **Restrict network access**: Use firewalls to limit access to only necessary ports
* **Monitor logs**: Regularly review logs for suspicious activity
* **Run as non-root**: The Docker container runs as a non-root user by default

## Acknowledgments

We would like to thank the following for their contributions to our security:

* All security researchers who responsibly disclose vulnerabilities
* The open-source community for their ongoing support

Thank you for helping keep Intelligent Request Router secure!
