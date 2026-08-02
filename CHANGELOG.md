# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-08-02

### Added

- Decimal-based price parsing and integer minor-unit storage
- Immutable product data model and fixture-based catalog parser
- Pagination discovery and bounded multi-page scanning
- Configurable `scan --max-pages` and `scan --all-pages` options
- `products --limit` and `history --product-id` options
- Versioned SQLite schema with foreign keys, indexes, and UTC timestamps
- Transactional product creation, price updates, and price-history storage
- GitHub Actions test workflow
- MIT License

### Changed

- Product identity now uses the source and canonical product URL
- Price-history charts now consume the version 2 database format
- Scan summaries report pages, created products, updates, unchanged products,
  and failed pages
- CLI commands now return meaningful process exit codes

### Fixed

- Malformed catalog entries no longer stop valid products from being parsed
- A later page failure no longer discards successfully stored earlier pages
- Repeated scans no longer duplicate unchanged products or history rows
- Floating-point price comparison errors are avoided

### Removed

- Support for the version 1 database schema; users receive explicit reset
  instructions instead of an automatic destructive migration

## [1.0.0] - 2026-07-24

### Added

- Initial command-line interface
- Single-page product scraping
- SQLite product and price-history storage
- Price-change detection and historical charts
- Application logging and automated tests

[Unreleased]: https://github.com/agirkayamemin/tech-price-tracker/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/agirkayamemin/tech-price-tracker/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/agirkayamemin/tech-price-tracker/releases/tag/v1.0.0
