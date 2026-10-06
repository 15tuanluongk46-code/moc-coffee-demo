# Boutique verification — 2026-10-06

## Delivered

- Original isolated Blender studio, 60 objects. Three studio images (1600×1100 desktop, 900×1200 portrait, 1200×900 macro), 24 turntable views at 800×900. Render report: `renders/product/report.json`, 171.97 seconds reported for the batch.
- WebP product media total 284,478 bytes; three self-hosted font files total 630,124 bytes, with two OFL files. These are additional assets, not total page transfer measurements.
- Standalone `source/moc-product-v01.blend` finalized successfully, sole scene `MOC - Boutique Studio`; label font packed. Background work did not edit the live user scene.
- Bounded four-chapter journey plus normal-flow boutique, product rotation, original SVG barista, local three-question recommendations and brewing guide.

## Functional evidence

`scripts/test_boutique.py`: eight Chromium tests pass, including bounded journey navigation, handoff without blank background, normal-section history, five responsive sizes, drag, keyboard rotation/reset, three detail buttons, failed-image recovery, lazy loading, no-JavaScript readable content, advisor back/edit/restart and synthetic touch gestures.

Touch test first reproduced a real failure: implicit pointer capture on the image emitted a bubbling `lostpointercapture` when capture transferred to its parent. The parent mistakenly canceled the new drag. Cleanup now checks the event target; the same test passes with horizontal rotation and vertical page scrolling.

Existing tests now measure progress against the journey's own height, rather than the document's extended height. Their seek, focus, history, modal and reduced-motion assertions remain in place. Run:

```bash
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_boutique.py
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_motion.py
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_motion_v2.py
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_ux.py
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_web.py
node --check web/app.js
node --check web/boutique.js
node --check web/advisor.js
python3 -m compileall -q scripts
```

## Visual evidence and limits

Desktop and mobile screenshots of collection, viewer and advisor are under `renders/browser/boutique-*.png`. A resized desktop collection screenshot was reviewed through the local vision tool: headline left, product image right, no reported overlap or clipping in that sample. This is a sampled layout check, not a comprehensive aesthetic or every-angle turntable approval.

Real iPhone/Safari, physical touchscreen behavior, screen-reader narration and sustained-device FPS have not been tested. Chromium touch input is synthetic. Advisor is a deterministic demo, not a live barista or remote AI service. Overall: functional checks passed; device and visual validation remain partial.
