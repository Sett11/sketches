# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Progress bar support using `indicatif` for long-running operations
- JSON report format support via `--format json` flag
- Configurable maximum recursion depth via `max_recursion_depth` in config
- Configuration validation with detailed error messages
- Custom error types using `thiserror` for better error handling
- CONTRIBUTING.md with contribution guidelines
- CHANGELOG.md for tracking changes

### Changed
- All code comments translated to English
- Improved error messages with context
- JsonReporter now integrated into CLI (no longer dead code)

### Fixed
- Removed outdated TODO comments
- Fixed temporary value lifetime issues in progress bar messages

## [0.1.0] - 2025-11-26

### Added
- Initial release
- Python/FastAPI support
- TypeScript support
- Call graph building
- Data chain extraction
- Contract checking
- Markdown report generation
- DOT graph visualization
- Configuration file support
- Cache support for graph serialization
- Location converter for accurate line/column tracking
- TypeScript function and class extraction
- TypeScript interface and type alias parsing
- Zod schema extraction and synchronization with TypeScript types
- Integration tests for TypeScript
- Unit tests for core functionality

### Features
- Builds call graphs from Python and TypeScript code
- Extracts data chains from call graphs
- Validates contracts between chain links
- Generates reports in Markdown format
- Visualizes graphs in DOT format
- Supports Pydantic, Zod, TypeScript, OpenAPI, and JSON Schema

