# Atelier V2 — validation record

## Brief and changes

The user rejected the first boutique presentation as insufficiently luxurious.
The approved direction was a premium craft coffee atelier: product-led typography,
less repetitive layout, restrained controls and more convincing packaging/light.

- Rebuilt the pouch with curved surfaces, pressed seals and a conforming paper label.
- Used finer material surface variation and directional studio lighting.
- Rendered separate desktop/mobile hero images, a detail image and 24 rotation views.
- Replaced the arched hero frame with a bounded, asymmetric editorial layout.
- Made the product name the main heading and moved the rotation image to the left
  on desktop, avoiding another identical text-left/image-right section.
- Simplified the visual treatment of rotation controls and product details.
- Unified the barista and brewing illustrations as original monoline SVG artwork.
- Preserved the advisor, keyboard/touch controls, static mode and journey behavior.

Original product assets and `source/moc-product-v01.blend` remain available.
The new files are under `renders/product-v2`, `web/media/product-v2` and
`source/moc-product-v02.blend`.

## Executed verification

Date: 2026-10-06.

- PASS: `python3 scripts/prepare_boutique.py --version 2` — packaged 3 studio
  images and 24 turntable frames.
- PASS: `/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/check_atelier.py`
  — 20 layout checks across 2494×1100, 1440×1000, 768×1024, 390×844 and 320×568;
  checks include horizontal overflow, bounded hero width, image loading and JS errors.
- PASS: `/home/sss/AI-Home/projects/flowbot/.venv/bin/python -m unittest scripts/test_boutique.py scripts/test_motion.py scripts/test_motion_v2.py scripts/test_ux.py`
  — 30 tests, 58.293 seconds. Includes advisor navigation, rotation, simulated touch,
  image-failure recovery, motion preferences, history, resize and modal behavior.
- PASS: `/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_web.py`
  — three viewport suites; forward/reverse journey navigation, keyboard dialog,
  reduced-motion media policy, responsive media, video fallback and byte ranges.
- PASS: `node --check web/app.js`, `node --check web/boutique.js`,
  `node --check web/motion.js`, `python3 -m compileall -q scripts`.
- PASS: reopened the standalone V2 blend in background Blender. Its only scene is
  `MOC - Atelier V2`, with 27 objects, a valid camera and the external font packed.

Render report: `renders/product-v2/report.json` — GPU rendering, 326.86 seconds.
Layout report: `renders/browser/atelier-layout.json`.
Screenshots: `renders/browser/atelier-{desktop,mobile}-{collection,product-viewer,advisor,brew-guide}.png`.

## Visual evidence and limits

Direct image input is unavailable in this session. A local Vision model reviewed
one resized desktop hero screenshot and one mobile product-viewer screenshot.
It identified the product and shadows/depth in the hero and described the mobile
bag as fully framed. Its answers did not address every requested layout detail,
so these are limited sampled observations, not an aesthetic acceptance verdict.

Automated checks establish functional and geometric layout correctness, not that
the design meets the user's subjective standard of luxury. Every rotation angle,
real-device Safari behavior and temporal visual smoothness have not been manually
reviewed. No claim of a complete visual-quality pass is made.

Demo: http://127.0.0.1:8046/?v=atelier-2#collection
