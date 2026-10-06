"""Original MOC studio assets. Run in background on the journey source file."""
import bpy
import math
import random
import sys
import json
import time
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import farm_scene as f
import journey_scene as j

NAME='MOC - Boutique Studio'


def label(name,body,position,size,material='studio-paper',font=None):
    obj=j.text('studio-'+name,body,position,size,material)
    if font: obj.data.font=font
    obj.data.extrude=.0003
    return obj


def build():
    scene=bpy.data.scenes.new(NAME)
    bpy.context.window.scene=scene
    j.NAME=f.SCENE=NAME
    f.material('studio-green',(.022,.082,.056),.52,True)
    f.material('studio-paper',(.79,.71,.55),.75,True)
    f.material('studio-ink',(.015,.04,.025),.72)
    f.material('studio-stone',(.55,.49,.39),.85,True)
    f.material('studio-floor',(.71,.665,.575),.83)
    # Soft rectangular cross-sections form a sealed, gusseted coffee pouch.
    rings=[(0,.49,.23),(.06,.57,.29),(.30,.62,.34),(1.25,.57,.29),
           (1.68,.53,.23),(1.87,.51,.075),(1.96,.51,.068)]
    verts=[];n=64
    for z,rx,ry in rings:
        for i in range(n):
            a=math.tau*i/n
            x=math.copysign(abs(math.cos(a))**.30,math.cos(a))*rx
            y=math.copysign(abs(math.sin(a))**.30,math.sin(a))*ry
            verts.append((x,y,z))
    faces=[tuple(reversed(range(n)))]
    for k in range(len(rings)-1):
        for i in range(n):
            faces.append((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i))
    faces.append(tuple((len(rings)-1)*n+i for i in range(n)))
    bag=f.mesh('studio-pouch',verts,faces,'studio-green',True)
    f.bevel(bag,.025,3)
    f.box('studio-top-seal',(0,0,1.94),(1.04,.15,.055),'studio-green',.018)
    f.box('studio-front-label',(0,-.315,1.01),(.86,.035,.94),'studio-paper',.018)
    for x in (-.505,.505):
        f.tube('studio-fold',[(x,.065,1.90),(x*1.12,.26,1.34),(x*1.1,.30,.23)],.005,'studio-green')
    sans=bpy.data.fonts.load(str(ROOT/'web/fonts/BeVietnamPro-Regular.ttf'))
    # Blender does not consistently support variable TTF fonts; use the static Vietnamese font for labels.
    label('brand','MỘC',(0,-.34,1.20),.26,'studio-ink',sans)
    label('origin','CẦU ĐẤT',(0,-.34,.98),.092,'studio-ink',sans)
    label('species','ARABICA',(0,-.34,.81),.065,'studio-ink',sans)
    label('weight','250 g  /  Rang vừa',(0,-.34,.64),.048,'studio-ink',sans)
    label('back','MỘC COFFEE',(0,.305,1.21),.12,'studio-paper',sans).rotation_euler=(math.pi/2,0,math.pi)
    back=label('back-copy','Chậm một nhịp.\nĐậm một chút.',(0,.305,.99),.066,'studio-paper',sans)
    back.rotation_euler=(math.pi/2,0,math.pi)
    label('side','M',( .605,0,.73),.14,'studio-paper',sans).rotation_euler=(math.pi/2,0,math.pi/2)
    product=list(scene.objects)
    pivot=bpy.data.objects.new('GEO-MOC-studio-turntable',None);scene.collection.objects.link(pivot)
    for obj in product: obj.parent=pivot
    j.cup('studio-latte',(1.17,-.43,.02),.68,True)
    random.seed(21)
    for i in range(20):
        x=random.uniform(-1.1,1.65);y=random.uniform(-.85,.6)
        if abs(x)<.68 and abs(y)<.39: continue
        bean=j.bean('studio-bean',(x,y,.065),.07,random.uniform(0,math.tau))
        f.tube('studio-bean-groove',[(x-.046,y,.116),(x,y+.012,.124),(x+.045,y,.116)],.005,'studio-ink')
    f.box('studio-floor',(0,0,-.10),(200,200,.18),'studio-floor',.025)
    world=bpy.data.worlds.new('WORLD-MOC-studio');world.use_nodes=True;scene.world=world
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
    bg.inputs['Color'].default_value=(.73,.78,.83,1);bg.inputs['Strength'].default_value=.35
    for name,pos,energy,size,color in [('key',(-3,-4,6),550,4,(1,.86,.70)),('fill',(4,-1,3),180,3,(.80,.88,1)),('rim',(1,3,5),700,2,(1,.92,.78))]:
        data=bpy.data.lights.new('LGT-MOC-studio-'+name,'AREA');data.energy=energy;data.size=size;data.color=color
        ob=bpy.data.objects.new(data.name,data);scene.collection.objects.link(ob);ob.location=pos;f.look_at(ob,(0,0,1))
    data=bpy.data.cameras.new('CAM-MOC-studio');cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam)
    scene.camera=cam;data.type='PERSP';data.lens=65
    try: scene.render.engine='CYCLES'
    except TypeError as e: raise RuntimeError(str(e))
    scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.render.use_persistent_data=True
    scene.render.resolution_percentage=100
    f.enum(scene.render.image_settings,'file_format','PNG');f.enum(scene.render.image_settings,'color_mode','RGB')
    scene.cycles.device='CPU'
    prefs=bpy.context.preferences.addons['cycles'].preferences
    try:
        prefs.compute_device_type='OPTIX';prefs.get_devices()
        for device in prefs.devices: device.use=device.type=='OPTIX'
        if any(d.use for d in prefs.devices): scene.cycles.device='GPU'
    except (TypeError,RuntimeError): pass
    return scene,pivot,product


def render(scene,path,size,position,target,samples=64):
    path.parent.mkdir(parents=True,exist_ok=True)
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.camera.location=position;f.look_at(scene.camera,target)
    scene.cycles.samples=samples;scene.render.filepath=str(path)
    try: bpy.ops.render.render(write_still=True,scene=NAME)
    except RuntimeError:
        scene.cycles.device='CPU';bpy.ops.render.render(write_still=True,scene=NAME)


if __name__=='__main__':
    start=time.time();scene,pivot,product=build();dest=ROOT/'renders/product'
    render(scene,dest/'hero-desktop.png',(1600,1100),(3.6,-6.6,3.4),(.38,0,.85),96)
    render(scene,dest/'hero-mobile.png',(900,1200),(3.3,-7.2,3.6),(.4,0,.95),96)
    render(scene,dest/'macro.png',(1200,900),(1.7,-2.9,1.85),(.08,-.15,1.03),96)
    keep=set(product+[pivot,scene.camera])
    for ob in scene.objects:
        if ob not in keep and ob.type not in {'LIGHT','CAMERA'} and ob.name!='GEO-MOC-studio-floor': ob.hide_render=True
    for i in range(24):
        pivot.rotation_euler[2]=i*math.tau/24
        render(scene,dest/'spin'/f'{i:02}.png',(800,900),(0,-5.5,2.5),(0,0,1),32)
    pivot.rotation_euler[2]=0
    for ob in scene.objects: ob.hide_render=False
    scene.camera.location=(3.6,-6.6,3.4);f.look_at(scene.camera,(.38,0,.85))
    # Library export scopes the saved asset to the new scene and its dependencies.
    bpy.data.libraries.write(str(ROOT/'source/moc-product-v01.blend'),{scene},fake_user=True,compress=True)
    (dest/'report.json').write_text(json.dumps({'scene':NAME,'objects':len(scene.objects),'seconds':round(time.time()-start,2),'turntable_frames':24,'device':scene.cycles.device},indent=2))
    print('BOUTIQUE_RENDER_DONE',round(time.time()-start,2))
