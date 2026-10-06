"""Render reproducible, resumable journey frames from the isolated blend."""
import bpy
import argparse
import json
import sys
import time
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import journey_scene as j

p = argparse.ArgumentParser()
p.add_argument('--view', choices=['desktop', 'mobile'], default='desktop')
p.add_argument('--proof', action='store_true')
p.add_argument('--cpu', action='store_true')
p.add_argument('--start', type=int, default=1)
p.add_argument('--end', type=int, default=j.FRAMES)
p.add_argument('--output-root', type=Path, default=ROOT / 'renders')
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
s = j.configure(a.view)
j.f.enum(s.cycles, 'device', 'CPU')
if not a.cpu:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for backend in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
            if any(d.type == backend for d in prefs.devices):
                for d in prefs.devices:
                    d.use = d.type == backend
                j.f.enum(s.cycles, 'device', 'GPU')
                break
        except (TypeError, RuntimeError):
            continue
out = a.output_root / ('proof-' + a.view if a.proof else 'frames-' + a.view)
out.mkdir(parents=True, exist_ok=True)
frames = j.STOPS if a.proof else range(a.start, a.end + 1)
start = time.monotonic()
for frame in frames:
    path = out / f'{frame:04}.png'
    if path.exists():
        with path.open('rb') as existing:
            header=existing.read(24)
        if len(header)==24 and struct.unpack('>II',header[16:24]) == (s.render.resolution_x,s.render.resolution_y):
            continue
    s.frame_set(frame)
    s.render.filepath = str(path)
    try:
        bpy.ops.render.render(write_still=True, scene=s.name)
    except RuntimeError:
        if s.cycles.device != 'GPU':
            raise
        j.f.enum(s.cycles, 'device', 'CPU')
        bpy.ops.render.render(write_still=True, scene=s.name)
    print(f'MOC_FRAME {a.view} {frame}/{j.FRAMES}', flush=True)
report = dict(view=a.view, device=s.cycles.device, seconds=round(time.monotonic()-start,2),
              frames=len(list(out.glob('*.png'))), width=s.render.resolution_x,
              height=s.render.resolution_y, fps=s.render.fps, samples=s.cycles.samples)
(out / 'report.json').write_text(json.dumps(report, indent=2))
print('MOC_REPORT', json.dumps(report), flush=True)
