# Asset provenance

All terrain, structures, coffee leaves/cherries, roaster, espresso machine, grinder, cups, bag, paths, trays and props are original procedural geometry created for this project by `scripts/farm_scene.py` and `scripts/journey_scene.py`. No downloaded models or image textures are used. Materials are procedural. Rendered branding is fictional.

Tools: Blender (GPL), FFmpeg (this build's license is reported by `ffmpeg -L`), ImageMagick (ImageMagick License), Python (PSF License), Playwright (Apache-2.0), Chromium (BSD and third-party licenses). No dependency is bundled in the website. These are tool licenses, not an automatic license assignment to the project's renders.

Interaction reference: [oso95/scroll-world](https://github.com/oso95/scroll-world), MIT, discovered through the user's TikTok reference. Its source code/assets are not copied: `web/app.js` is a small original implementation for one continuous video per viewport. Online model candidates researched previously have not been imported.

## Boutique extension — 2026-10-06

`scripts/product_scene.py` creates the original shaped pouch, paper label, seams, latte and beans. Studio renders and the 24-angle turntable are original outputs, with no downloaded models or image textures. The inline SVG barista in `web/index.html` is an original illustration. Branding and product specifications are demonstration concepts.

Self-hosted fonts, downloaded unmodified from Google Fonts:
- [Be Vietnam Pro](https://github.com/google/fonts/tree/main/ofl/bevietnampro): Regular and SemiBold; SIL Open Font License 1.1, retained at `web/fonts/BeVietnamPro-OFL.txt`.
- [Fraunces](https://github.com/google/fonts/tree/main/ofl/fraunces): variable upright font; SIL Open Font License 1.1, retained at `web/fonts/Fraunces-OFL.txt`.

The static Be Vietnam Pro font used on the product label is packed in `source/moc-product-v01.blend`. Original copyright notices are preserved in the accompanying OFL files.

## Atelier v2

`scripts/product_atelier.py` generates the new pouch surface, conforming label and glyph meshes, pressed seams, stone slab and espresso cup from original geometry. Fine surface variation is procedural noise, with no downloaded textures. The standalone `source/moc-product-v02.blend` includes the font. The single-line barista and three brewing SVG icons are original drawings. Version 1 assets remain in `web/media/product/`; the current set is `web/media/product-v2/`.
