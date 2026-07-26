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

## [1.1.0] - 2026-07-26

### Added
- **README: 11 new MCP server entries** covering cloud platforms, enterprise tools, payments, and communications:
  - Cloudflare MCP Server (Workers/D1/KV/R2/DNS, 10 tools)
  - Vercel MCP Server (deployments/domains/env vars, 8 tools)
  - Supabase MCP Server (PostgreSQL/Auth/Storage/Edge Functions, 9 tools)
  - AWS MCP Server (S3/Lambda/EC2/CloudWatch, 12 tools)
  - Jira MCP Server (Issue/Sprint/Board, 8 tools)
  - Confluence MCP Server (pages/spaces, 6 tools)
  - Stripe MCP Server (payments/subscriptions/refunds, 9 tools)
  - Twilio MCP Server (SMS/Voice/WhatsApp, 6 tools)
  - Google Maps MCP Server (places/routes/geocoding, 7 tools)
  - Datadog MCP Server (metrics/logs/alerts, 8 tools)
  - OpenAPI MCP Server (Swagger spec parsing/mock, 5 tools)
- **README: "2026 MCP 生态趋势" section** covering:
  - MCP 2025-11 specification: Streamable HTTP Transport replacing SSE
  - MCP Authorization extension with OAuth 2.1 (Authorization Code + PKCE, Client Credentials, Token Introspection)
  - Remote MCP Server deployment trend (local stdio vs remote HTTP vs cloud SaaS)
  - MCP ecosystem registries: mcp.so, glama.ai, smithery.ai, Anthropic official list
- **README: "Roadmap" section** with v2.0 (2026 Q3), v2.1 (2026 Q4), and v3.0 (2027 Q1) planning
- **README: Table of contents** updated with new sections (2026 MCP 生态趋势, Roadmap)

### Changed
- Server count badge updated from 26 to 37
- Header description updated to reflect expanded scope (cloud platforms, payments, communications)
- Total tool count updated to 200+
- New server categories added to README: 云平台与基础设施, 企业协作与项目管理, 支付与通信, 地图与可观测性, API 与规范

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
