# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Security middleware with CORS restrictions, JWT authentication, API key support
- Security headers middleware (HSTS, CSP, XSS protection, etc.)
- Input sanitization and validation middleware
- Rate limiting middleware
- Comprehensive test suite (unit tests, integration tests, E2E tests)
- GitHub Actions CI/CD pipeline
- pyproject.toml for modern Python project configuration
- mypy.ini for type checking configuration
- .editorconfig for consistent coding styles
- .pre-commit-config.yaml for code quality checks
- CONTRIBUTING.md with contribution guidelines
- Detailed evaluation report

### Changed
- CORS configuration now restricts allowed origins (no longer allows all)
- API endpoints now require authentication (JWT or API Key)
- Dynamic module loading now uses importlib instead of __import__
- Input parameters are now sanitized before processing
- Settings.py redis_url property fixed

### Fixed
- Settings.py syntax error in redis_url property
- Mutable default argument in execute_mcp_tool endpoint
- Import issues in middleware modules

### Security
- Added JWT token authentication
- Added API key authentication
- Added rate limiting
- Added security headers (HSTS, CSP, XSS protection, etc.)
- Added input sanitization to prevent injection attacks
- Added path traversal protection

## [1.0.0] - 2024-01-01

### Added
- Initial release
- 15 MCP servers (Amap, DingTalk, Weather, Calendar, Filesystem, Git, Database, HTTP Client, GitHub, Slack, Brave Search, Notion, Google Sheets, Browser, Memory)
- FastAPI backend with async support
- Celery for background task processing
- Redis for caching and message broker
- Web management interface
- Docker support
- Basic documentation

## [0.1.0] - 2023-12-01

### Added
- Project initialization
- Basic MCP server framework
- Commute assistant feature (Amap + DingTalk integration)

---

## Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

## Versioning

This project uses Semantic Versioning. For a version number MAJOR.MINOR.PATCH:

- **MAJOR**: incompatible API changes
- **MINOR**: backwards-compatible functionality additions
- **PATCH**: backwards-compatible bug fixes

## Release Process

1. Update CHANGELOG.md with new version
2. Update version in pyproject.toml
3. Create a git tag
4. Push tag to trigger release
