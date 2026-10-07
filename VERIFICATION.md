# Handoff verification — 2026-10-07

Baseline `5ea3ce437db62894ccee7279d65460b3539b7cd8`; isolated Linux clone,
Python 3.12.3, `.venv-test` with Playwright 1.63.0 and Pillow 12.3.0.
Created ignored `renders/` before running screenshot tests.

Owned server: `python3 scripts/serve.py --port 8146`. The existing server on 8046
belonged to another workspace and was left untouched.

- PASS: `.venv-test/bin/python scripts/test_web.py --static-only --base-url http://127.0.0.1:8146/`
  — responsive navigation/dialogs, no overflow/errors, reduced-motion request checks.
- PASS: `.venv-test/bin/python scripts/test_web.py --base-url http://127.0.0.1:8146/`
  — also responsive media switching, failed-video fallback, HTTP byte ranges and Blob scrubbing.
- PASS: 26 unittest cases from `scripts/test_ux.py`, `scripts/test_boutique.py`,
  `scripts/test_scroll_stops.py`. Each module's `BASE` was overridden in the test
  process to the owned server on 8146; source files were not edited.
- PASS: `python3 scripts/package_site.py` — 96 files, ZIP 10,373,515 bytes.

NOT RUN: Blender rendering, historical Extraction/motion regression sets, external
production/CDN tests and deployment. Website verification uses tracked media;
it does not prove optional source-asset rebuilds on a fresh machine.

**Verdict: current local website checks and packaging passed; optional rebuild and
production deployment unverified.**
