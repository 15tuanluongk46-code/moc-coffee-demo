# MỘC farm proof Implementation Plan

> **For agentic workers:** Execute inline using executing-plans; no delegation required. Steps use checkbox syntax.

**Goal:** Deliver desktop and mobile farm renders for the approved visual checkpoint.

**Architecture:** A deterministic Blender builder creates a dedicated scene with independent world, materials and cameras. Export only this scene into a standalone .blend; save proof PNGs separately.

**Tech Stack:** Blender 5.2, Python standard library, local GPU rendering.

**Spec:** `docs/design.md`

## Global Constraints
- Preserve existing Blender scenes and the current source file.
- Original procedural assets, no paid services.
- Vietnamese copy remains separate from the 3D image.
- Stop at the image approval checkpoint before full animation.

### Task 1 — Reproducible farm scene
Files: `scripts/farm_scene.py`, `assets/ATTRIBUTION.md`.
Interface: `setup()`, `landscape()`, `plants()`, `details()`, `configure(view, preview=False)`, `export()`.
- [x] Create dedicated scene and isolated materials/cameras.
- [x] Build terraces, farm shed, paths, drying racks and coffee plants with red cherries.
- [x] Validate object scope and cameras with Blender scene readback.

### Task 2 — Composition and rendering
Outputs: `renders/farm-desktop.png`, `renders/farm-mobile.png`, `source/moc-farm-v01.blend`.
- [x] Render low resolution composition proof and inspect it visually.
- [x] Adjust if clipping, unreadable forms, dark/flat materials or poor text space.
- [x] Render both final stills; verify dimensions and file sizes.
- [x] Export dedicated scene; verify source can reopen in background Blender.

### Task 3 — Handoff
Files: `README.md`, `docs/validation.md`.
- [x] Document actual render settings, timing and attribution.
- [ ] Show proof paths and request visual approval for the next stage.
