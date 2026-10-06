"""Turn the isolated scene library into a directly openable Blender project."""
import bpy
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
journey='--journey' in sys.argv
product='--product' in sys.argv
scene=bpy.data.scenes['MOC - Boutique Studio' if product else ('MOC - Complete Journey' if journey else 'MOC - Coffee Origin')]
bpy.context.window.scene=scene
if product:
    scene.render.resolution_x=1600
    scene.render.resolution_y=1100
    scene.cycles.samples=96
    for font in bpy.data.fonts:
        if font.filepath and font.filepath!='<builtin>': font.pack()
if journey:
    sys.path.insert(0,str(root/'scripts'))
    import journey_scene as j
    j.configure('mobile')
    j.configure('desktop')
    scene.frame_set(1)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                j.f.enum(area.spaces.active.shading,'type','MATERIAL')
                j.f.enum(area.spaces.active.region_3d,'view_perspective','CAMERA')
for other in list(bpy.data.scenes):
    if other!=scene and not other.objects:
        bpy.data.scenes.remove(other)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'source'/('moc-product-v01.blend' if product else ('moc-journey-v01.blend' if journey else 'moc-farm-v01.blend'))))
print({'saved_scene':scene.name,'objects':len(scene.objects),'scenes':list(bpy.data.scenes.keys())})
