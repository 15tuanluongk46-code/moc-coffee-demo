"""Create a scoped source variant; assert every surviving object/camera is unchanged."""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.data.scenes['MOC - Complete Journey']
bpy.context.window.scene = scene
prefix = 'GEO-MOC-journey-stepping-stone'
targets = [o for o in scene.objects if o.name.startswith(prefix)]
assert len(targets) == 24, f'Expected only 24 connectors, found {len(targets)}'

def state(obj):
    return (obj.type, obj.data.name if obj.data else None,
            tuple(tuple(row) for row in obj.matrix_world), obj.hide_render,
            tuple(m.name if m else None for m in getattr(obj.data, 'materials', [])))

survivors = {o.name: state(o) for o in scene.objects if o not in targets}
camera_motion = {}
for frame in range(1, 289):
    scene.frame_set(frame)
    camera_motion[frame] = {
        o.name: (tuple(tuple(row) for row in o.matrix_world), o.data.ortho_scale,
                 o.data.shift_x, o.data.shift_y, o.data.lens)
        for o in scene.objects if o.type == 'CAMERA'
    }
scene.frame_set(1)
# Capture surviving transforms at the same frame before and after removal.
survivors = {o.name: state(o) for o in scene.objects if o not in targets}
removed = [o.name for o in targets]
before_count = len(scene.objects)
for obj in targets:
    bpy.data.objects.remove(obj, do_unlink=True)
assert {o.name: state(o) for o in scene.objects} == survivors
for frame, expected in camera_motion.items():
    scene.frame_set(frame)
    actual = {o.name: (tuple(tuple(row) for row in o.matrix_world), o.data.ortho_scale,
                       o.data.shift_x, o.data.shift_y, o.data.lens)
              for o in scene.objects if o.type == 'CAMERA'}
    assert actual == expected, f'Camera changed at frame {frame}'
scene.frame_set(1)
output = ROOT / 'source' / 'moc-journey-no-connectors-v02.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output))
report = dict(source='source/moc-journey-v01.blend', output=str(output),
              source_sha256=hashlib.sha256((ROOT/'source/moc-journey-v01.blend').read_bytes()).hexdigest(),
              removed=removed, before_objects=before_count, after_objects=len(scene.objects),
              survivors_unchanged=True, camera_frames_verified=288)
(ROOT/'docs'/'connector-removal.json').write_text(json.dumps(report, indent=2))
print('CONNECTORS_REMOVED', json.dumps(report), flush=True)
