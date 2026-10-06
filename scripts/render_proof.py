"""Background render of the dedicated farm scene, using detected local GPU."""
import bpy
import importlib.util
import json
import sys
import time
from pathlib import Path

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('farm_scene',root/'scripts/farm_scene.py')
farm=importlib.util.module_from_spec(spec)
spec.loader.exec_module(farm)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['desktop']
view=args[0]
s=farm.configure(view,'--preview' in args)
prefs=bpy.context.preferences.addons['cycles'].preferences
supported=[x.identifier for x in prefs.bl_rna.properties['compute_device_type'].enum_items]
for backend in ('OPTIX','CUDA'):
    try:
        prefs.compute_device_type=backend
        prefs.get_devices()
        devices=[d for d in prefs.devices if d.type==backend]
        if devices:
            for d in prefs.devices: d.use=d.type==backend
            s.cycles.device='GPU'
            break
    except (TypeError,RuntimeError):
        continue
start=time.monotonic()
if '--cpu' in args:
    farm.enum(s.cycles,'device','CPU')
bpy.ops.render.render(write_still=True,scene=s.name)
report={'view':view,'seconds':round(time.monotonic()-start,2),'engine':s.render.engine,
        'device':s.cycles.device,'samples':s.cycles.samples,'path':s.render.filepath,
        'width':s.render.resolution_x*s.render.resolution_percentage//100,
        'height':s.render.resolution_y*s.render.resolution_percentage//100,
        'objects':len(s.objects)}
Path(s.render.filepath).with_suffix('.json').write_text(json.dumps(report,indent=2))
print('MOC_RENDER_REPORT '+json.dumps(report))
