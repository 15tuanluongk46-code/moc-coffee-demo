# Farm proof validation — 2026-10-05

## Artifact
- Scene `MOC - Coffee Origin`: 304 objects, 22 shrubs sharing one mesh, 3 area lights, 2 orthographic cameras.
- Total mesh vertices counting each instance: 192,286. Shared shrub prototype: 8,584 vertices.
- Original procedural materials: 16; terrain/plaster/wood use noise-driven bump.
- Blender 5.2.1 LTS; Cycles, 64 samples, denoising.

## Actual renders
| View | Size | Device | Render time |
|---|---|---|---|
| Desktop | 1600×1000 | CPU, 8 threads | 44.46 s |
| Mobile | 900×1200 | CPU, 8 threads | 28.45 s |

The early blockout GPU render succeeded in 2.81 s. Detailed GPU render failed with out-of-memory; nvidia-smi reported 11,342 MiB used and 571 MiB free on a 12 GiB RTX 3060. No other application was stopped. CPU was used for the final stills.

## Framing checks
Conservative world-space object bounding boxes projected into normalized camera coordinates, excluding studio floor:
- Desktop: x 0.350–0.973, y 0.105–0.749; left region reserved for HTML copy.
- Mobile: x 0.038–0.966, y 0.082–0.532; upper region reserved for HTML copy.
- First detailed desktop composition had bounds beyond 1.0 on the right; orthographic scale increased from 16.2 to 19.0 before final render.
- Shrub base heights calculated from the terrace footprints to avoid floating plants.

## Visual evidence
Current host cannot read image input; local vision agent reviewed resized actual rendered images. Reported desktop island fully inside frame, visible left empty space, readable plants/house; mobile island/house fully inside frame. Vision output is limited, so human art-direction approval remains the checkpoint. No claim of validated motion or website performance is made from stills.

## Preservation
Live Blender source path remains `/home/sss/Downloads/Elle_Streetwear/Elle_Streetwear_levitation_pose_v02.blend`. `Monster Showcase - Meshy` retains its 2 objects. The farm exported as an isolated dependency library and was reopened/finalized with background Blender into a standalone project containing only the farm scene.
