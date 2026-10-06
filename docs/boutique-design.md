# MỘC boutique — approved extension

User approved the whole extension and autonomous Build execution on 2026-10-06.

## Experience

Keep the four-chapter, reduced-motion-aware journey. Its scroll range becomes local to `#journey`, independent of content below. A normal-flow boutique follows: studio product image, 24-view product turntable, three-question illustrated advisor, brewing guide and an honest demo footer. Existing taste-note dialog remains available.

The turntable uses rendered WebP images, pointer drag with vertical scrolling preserved, previous/next keys and buttons, label reset, and three descriptive hotspots. Load remaining images only near the viewer; never replace a working image with a failed one. No automatic continuous spin. Static/reduced-motion modes still permit user-requested rotation.

Advisor runs locally, stores answers only in page memory, supports back/edit/restart and explains its recommendation. It represents a fictional barista, not a human chat. No invented reviews, claims, purchasing or external contacts.

## Art and type

Original Blender studio scene: shaped forest-green pouch, folded seams, paper label, ceramic latte, textured beans, warm neutral lighting. Separate desktop/portrait hero images and macro. Be Vietnam Pro and Fraunces self-hosted with OFL licenses. Original inline SVG barista and line icons.

## Implementation units

- `scripts/product_scene.py`: reproducible isolated Blender studio, sources and render outputs.
- `scripts/prepare_boutique.py`: font downloads/license preservation and image packaging.
- `web/boutique.css`: namespaced editorial layout, type, viewer and advisor styles.
- `web/boutique.js`: lazy turntable and accessible advisor state machine.
- `web/advisor.js`: pure recommendation logic and content.
- `web/app.js`: bounded journey scroll, normal-content anchors and modal position restoration.
- `scripts/test_boutique.py`: real-browser flows, error recovery, keyboard/touch, no-JS and responsive coverage.

## Verification

New tests fail before feature implementation, then pass alongside existing motion/UX/browser suites. Old tests measuring document-wide progress must measure the journey's own scroll span. Render dimensions/asset completeness and screenshot review are separate from functional verification. No paid services, commits, publishing or changes to the user's live Blender scene.
