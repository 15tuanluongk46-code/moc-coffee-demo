# Full demo — verification record

Latest website UX update: see [ux-validation.md](ux-validation.md) for the 2026-10-06 fixes and regression results. The media checks below describe the original render delivery.

Date: 2026-10-05. Project: MỘC Coffee, fictional brand demonstration.

## Delivered

- Four original procedural Blender stations: farm, roaster, espresso bar, cup/packaging.
- Standalone `source/moc-journey-v01.blend`, 567 objects and a baked camera journey.
- Two 288-frame, 24 fps, 12-second H.264/yuv420p videos: desktop 1280×800 and mobile 720×1440. Desktop approximately 2.5 MiB; mobile approximately 1.8 MiB.
- Eight WebP posters and dependency-free HTML/CSS/JavaScript website.
- Loopback server at http://127.0.0.1:8046/ with byte-range responses.

## Passed checks

- `node --check web/app.js` — syntax valid.
- `python3 -m compileall -q scripts` — Python syntax valid.
- `python3 scripts/package_media.py` — both complete sequences encoded; FFprobe confirms 288 frames and 12 seconds each. Details: `media-report.json`.
- `python3 scripts/check_media.py` — every PNG decoded; all 576 frames have the expected dimensions and nonuniform content. Pixel-difference data in `frame-check.json`; twelve-frame contact sheets in `../renders/contact-desktop.jpg` and `../renders/contact-mobile.jpg`.
- `/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_web.py --static-only` — static navigation and reduced-motion behavior passed.
- `/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_web.py` — full Chromium integration passed. Viewports: 1440×900, 390×844, 360×640. Checks include chapter navigation forward/reverse, actual video seek time, interrupted rapid seeks, one active copy with other copies inert, copy bounds and no horizontal overflow, dialog Escape/focus restoration, static/video toggle, responsive media switching, no video request under reduced motion, failed-video poster fallback, and HTTP 206 byte range. No JavaScript page errors in the three viewport runs. Report: `../renders/browser/test-full.json`.
- Final server request returned HTTP 200.
- Isolated Blender source finalized and saved with the journey scene; source file exists. Earlier live user scenes were preserved; the user's original file was not overwritten.

## Visual and temporal verdicts

- **Structural / functional: passed** for the checks above.
- **Sampled visual: limited, not a quality PASS.** This session cannot directly read image inputs. Local vision responses identified coffee props but did not reliably answer composition and typography questions. Browser screenshots and contact sheets are retained for inspection.
- **Temporal aesthetics: not independently verified.** Frame completeness, pixel deltas and browser seeks do not establish absence of flicker or aesthetically smooth 1× playback. No claim of a full visual/temporal quality pass is made.
- **Physical mobile / Safari: not tested.** Mobile tests used Chromium viewport emulation, not iOS hardware or Safari.
- **Clean rebuild command: provided but not rerun end-to-end.** The shipped source and renders were produced through the staged build; script syntax was checked.

Overall: functional demo delivered; visual/temporal and real-device verification remain partial.

## Scope and reference fidelity

This implementation uses a continuous orthographic camera journey between miniature stations. It does not reproduce an outside-to-inside flythrough through buildings. Website text, navigation and CTA are real HTML. There is no e-commerce backend. All models/materials are original procedural work; no paid generation service was used. Rendering switched to CPU when GPU memory was unavailable, then resumed with GPU after memory became available. No unrelated applications were stopped.
