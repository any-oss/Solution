# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Database persistence layer with SQLite connection pooling
- Session tracking and analytics capabilities
- Routing decision logging for audit trails
- Prometheus metrics integration
- UI dashboard for monitoring
- CLI tool for health checks and prompt generation
- SDK for programmatic access

### Changed
- Refactored proxy server with improved error handling
- Enhanced backend selection logic
- Improved logging consistency across all services

### Fixed
- JSON parsing error handling in proxy
- Database connection cleanup on shutdown
- Health check endpoint responses

## [1.0.0] - 2024-01-15

### Added
- Initial release of Intelligent Request Router
- Smart routing based on prompt length
- CPU and GPU backend support
- Docker Compose deployment
- Kubernetes deployment manifests
- GitHub Actions CI/CD pipeline
- Comprehensive test suite
- Production-ready documentation
