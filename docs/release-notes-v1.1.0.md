# Tech Price Tracker v1.1.0

v1.1.0 is a reliability-focused release. It keeps the project intentionally
small while making price handling, catalog scanning, database updates, and CLI
behavior safer and easier to verify.

## Highlights

- Prices are parsed with decimal arithmetic and stored as integer minor units.
- Products are identified by source and canonical URL.
- The scanner can follow pagination with a configurable 50-page safety cap.
- Database writes are transactional and timestamps are stored in UTC.
- Malformed products and later-page failures are handled without losing valid
  results.
- New CLI options support bounded scans, output limits, and direct product IDs.
- The offline test suite covers parsing, persistence, scanning, CLI behavior,
  and visualization.
- GitHub Actions runs the full suite for every push and pull request.

## Commands

```bash
python -m src.main scan --max-pages 5
python -m src.main scan --all-pages
python -m src.main products --limit 10
python -m src.main history --product-id 7
```

## Upgrade Note

The database schema changed in this release. Automatic migration is
intentionally not attempted. If a v1.0.0 database is detected, back up
`data/products.db` if needed, delete it manually, and run the scan command to
create a clean version 2 database.

## Verification

- Full automated test suite passes locally on Python 3.14.
- Network behavior is tested with mocks; tests do not contact the live site.
- Live scanning should be verified once against a newly created version 2
  database before publishing the release.
