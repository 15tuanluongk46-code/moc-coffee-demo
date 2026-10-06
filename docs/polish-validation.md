# Product and advisor polish — 2026-10-06

Demo: http://127.0.0.1:8046/?v=polish-1#collection

## Changes

- Advisor step and result headings retain keyboard focus and are moved below the fixed header only when outside the readable viewport. Checked at 320×568, 360×640 and 390×844.
- Result links explicitly name and target the chosen recipe: Phin, Pour-over or Espresso. The questionnaire's “Máy espresso” value maps to the Espresso card. Destination headings receive focus.
- Recipe arrival gets a 1400ms background highlight in motion mode. Static/reduced-motion mode skips it; enabling reduced motion also cancels an active highlight.
- Viewer instructions, status, controls, detail copy and advisor privacy text use at least 12px; image captions use at least 11px. The secondary advisor link has a minimum 44px tap height.
- Product detail space is measured against all three descriptions at the current width/font. Width changes and font readiness recalculate the reservation; changing the selected detail no longer changes its height.

## Verification

Executed from the project directory using the existing Playwright environment:

```sh
/home/sss/AI-Home/projects/flowbot/.venv/bin/python -m unittest scripts/test_polish.py scripts/test_scroll_stops.py scripts/test_boutique.py scripts/test_motion.py scripts/test_motion_v2.py scripts/test_ux.py
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/check_atelier.py
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_web.py
node --check web/app.js
node --check web/boutique.js
python3 -m compileall -q scripts
```

- PASS: 43 regression tests, 76.980 seconds. Includes five polish tests and the existing scroll, touch/rotation, advisor, motion and UX cases.
- PASS: 20 layout states across five viewport sizes, including 2494px and 320px widths. Report: `renders/browser/atelier-layout.json`.
- PASS: full browser suite across desktop/mobile/small-mobile, forward/reverse seeks, keyboard dialog, overflow and JS errors, reduced-motion media avoidance, responsive source switching, failed-video fallback and HTTP byte ranges. Report: `renders/browser/test-full.json`.
- PASS: JavaScript syntax and Python compilation.

The new behavioral assertions were observed failing before the corresponding fixes. The original Espresso test selector was corrected to match the real questionnaire option “Máy espresso”; the actual recipe link is separately asserted as “Xem cách pha Espresso”.

## Scope of evidence

These results verify Chromium behavior and measured layout. No new Blender render was needed. They do not certify every visual state, native Safari, physical mobile devices, assistive-technology behavior or real trackpad feel.
