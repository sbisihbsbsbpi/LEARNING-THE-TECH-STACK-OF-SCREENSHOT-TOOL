# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-02

### Added
- 🎉 Initial release
- Desktop application built with Tauri + React + FastAPI
- Headless browser automation with Playwright
- Segmented capture for long pages
- Authentication state management (save/reuse login sessions)
- Quality checking (auto-detect blank/low-quality screenshots)
- Document generation (export to .docx)
- Stealth mode with playwright-stealth
- Real browser mode for debugging
- URL library with folder organization
- Session history tracking
- Base URL naming for smart filenames
- Duplicate detection for segments
- Real-time progress tracking via WebSocket
- Stop button to cancel captures
- Live logs panel
- Dark mode UI
- Chrome-style tabs for Settings and Logs
- Auth data preview
- Words to remove from naming
- Beautify URLs feature
- Line numbers for URLs
- Collapsible segment preview
- Dynamic preview sizing
- Quality score display
- URL truncation
- Logs status indicator

### Technical Features
- FastAPI async backend
- Playwright browser automation
- playwright-stealth anti-detection
- python-docx document generation
- Pillow image processing
- imagehash duplicate detection
- React + TypeScript frontend
- Vite build tool with HMR
- Tailwind CSS styling
- WebSocket real-time communication
- Concurrent screenshot processing
- Smart lazy-load detection
- Retry strategies
- Error detection and handling

### Documentation
- Comprehensive README
- Quickstart guide
- Contributing guidelines
- License (MIT)
- Multiple feature documentation files

## [Unreleased]

### Planned Features
- PDF export
- Cloud sync
- Scheduled captures
- Browser extension
- CLI tool
- Batch processing improvements
- Custom viewport presets
- Screenshot annotations
- Video recording
- API documentation
- Unit tests
- Integration tests
- Performance optimizations
- Multi-language support

---

For more details, see the [GitHub releases](https://github.com/sbisihbsbsbpi/screenshot-headless-tool/releases).

