"""V2 studio: original soft pouch, conforming paper and directional light.

Run with Blender --factory-startup --background --python this_file.py.
Keeps the rejected v1 renders and blend intact.
"""
import bpy
import math
import sys
import json
import time
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import farm_scene as f
import journey_scene as j

NAME = 'MOC - Atelier V2'


def material(name, color, roughness, scale=0, depth=0, coat=0):
    mat = f.material(name, color, roughness)
    bs = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Coat Weight'].default_value = coat
    bs.inputs['Coat Roughness'].default_value = .22
    if scale:
        noise = mat.node_tree.nodes.new('ShaderNodeTexNoise')
        noise.noise_dimensions = '3D'
        noise.noise_type = 'FBM'
        noise.normalize = True
        noise.inputs['Scale'].default_value = scale
        bump = mat.node_tree.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .22
        bump.inputs['Distance'].default_value = depth
        mat.node_tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    return mat


def dims(z):
    keys = [(0,.49,.20),(.10,.57,.28),(.36,.60,.32),(1.25,.57,.29),
            (1.70,.54,.23),(1.92,.53,.042),(2.04,.53,.038)]
    for (a,x,y),(b,xx,yy) in zip(keys,keys[1:]):
        if z <= b:
            t=max(0,(z-a)/(b-a));t=t*t*(3-2*t)
            return x+(xx-x)*t,y+(yy-y)*t
    return keys[-1][1:]


def front(x,z):
    rx,ry=dims(z)
    width=min(.999,abs(x)/rx)
    y=-ry*max(0,1-width**6)**(1/6)
    # Minute, localized shoulder/foot creases. Centre remains calm for the label.
    edge=width**7
    y += edge*.018*math.sin(z*19+x*9)*math.sin(math.pi*z/2.04)
    return y


def grid(name,x0,x1,z0,z1,offset,mat,nx=44,nz=64):
    verts=[]
    for k in range(nz+1):
        z=z0+(z1-z0)*k/nz
        for i in range(nx+1):
            x=x0+(x1-x0)*i/nx
            verts.append((x,front(x,z)-offset,z))
    faces=[(k*(nx+1)+i,k*(nx+1)+i+1,(k+1)*(nx+1)+i+1,(k+1)*(nx+1)+i)
           for k in range(nz) for i in range(nx)]
    return f.mesh(name,verts,faces,mat,True)


def inscription(name,body,z,size,font,mat='atelier-ink'):
    obj=j.text(name,body,(0,-.4,z),size,mat)
    obj.data.font=font;obj.data.extrude=.00015;obj.data.resolution_u=12
    # Turn each glyph into a mesh and conform it to the same surface as the paper.
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    obj=bpy.context.object
    world=obj.matrix_world.copy()
    for v in obj.data.vertices:
        p=world@v.co
        v.co=(p.x,front(p.x,p.z)-.004,p.z)
    obj.location=(0,0,0);obj.rotation_euler=(0,0,0)
    obj.select_set(False)
    return obj


def build():
    scene=bpy.data.scenes.new(NAME);bpy.context.window.scene=scene
    j.NAME=f.SCENE=NAME
    material('atelier-green',(.018,.048,.034),.43,220,.0016,.12)
    material('atelier-paper',(.76,.68,.51),.84,340,.0009)
    material('atelier-ink',(.025,.039,.027),.65)
    material('atelier-floor',(.39,.345,.275),.83,120,.001)
    material('atelier-stone',(.19,.205,.165),.88,95,.0028)
    material('atelier-porcelain',(.74,.70,.61),.25,280,.0005,.32)
    material('atelier-coffee',(.10,.032,.008),.24)
    material('atelier-crema',(.34,.15,.035),.51,180,.001)
    # 10k vertices, enough to describe soft gussets rather than a beveled box.
    n=128;rows=80;verts=[]
    for k in range(rows+1):
        z=2.04*k/rows;rx,ry=dims(z)
        for i in range(n):
            a=i*math.tau/n
            x=rx*math.copysign(abs(math.cos(a))**(1/3),math.cos(a))
            y=ry*math.copysign(abs(math.sin(a))**(1/3),math.sin(a))
            if y<0:y=front(x,z)
            else:y+=.009*math.sin(z*13+a*6)*math.sin(math.pi*k/rows)
            verts.append((x,y,z))
    faces=[tuple(reversed(range(n)))]
    faces += [(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i)
              for k in range(rows) for i in range(n)]
    faces.append(tuple(rows*n+i for i in range(n)))
    f.mesh('atelier-pouch',verts,faces,'atelier-green',True)
    # Paper is a conforming surface only 0.002 art units above the bag.
    grid('atelier-paper-label',-.405,.405,.40,1.59,.002,'atelier-paper')
    font=bpy.data.fonts.load(str(ROOT/'web/fonts/BeVietnamPro-Regular.ttf'))
    for name,body,z,size in [('mark','MỘC',1.30,.26),('origin','CẦU ĐẤT',1.035,.105),
                            ('species','A R A B I C A',.865,.043),('roast','Rang vừa',.61,.053),('weight','250 g',.48,.045)]:
        inscription('atelier-'+name,body,z,size,font)
    grid('atelier-label-rule',-.30,.30,.758,.762,.004,'atelier-ink',30,1)
    # Heat seal: narrow parallel pressed lines, not a separate thick block.
    for k in range(6):
        grid('atelier-seal-'+str(k),-.525,.525,1.935+k*.016,1.938+k*.016,.001,'atelier-green',60,1)
    # Rear printed typography follows the rear face; no floating text through the bag.
    back=j.text('atelier-back','MỘC COFFEE\n\nChậm một nhịp.\nĐậm một chút.',(0,.326,.98),.065,'atelier-paper')
    back.data.font=font;back.rotation_euler=(math.pi/2,0,math.pi)
    product=list(scene.objects)
    pivot=bpy.data.objects.new('GEO-MOC-atelier-pivot',None);scene.collection.objects.link(pivot)
    for ob in product:ob.parent=pivot
    # Low stone slab anchors the pack; single espresso cup gives scale without clutter.
    f.box('atelier-stone-slab',(0,.04,-.11),(1.60,1.02,.22),'atelier-stone',.027)
    j.lathe('atelier-saucer',(1.02,-.62,-.215),[(0,0),(.50,0),(.54,.035),(.51,.065),(.28,.07),(0,.045)],'atelier-porcelain',96)
    j.lathe('atelier-cup',(1.02,-.62,-.15),[(0,0),(.22,0),(.25,.04),(.33,.38),(.33,.405),(.308,.410),(.305,.38),(.21,.05),(0,.05)],'atelier-porcelain',96)
    j.lathe('atelier-espresso',(1.02,-.62,.213),[(0,0),(.301,0)],'atelier-coffee',96)
    j.lathe('atelier-crema-edge',(1.02,-.62,.214),[(.285,0),(.300,0)],'atelier-crema',96)
    f.tube('atelier-handle',[(1.31+.17*math.sin(math.pi*i/48),-.62,.05+.14*math.cos(math.pi*i/48)) for i in range(49)],.033,'atelier-porcelain')
    f.box('atelier-ground',(0,0,-.245),(200,200,.05),'atelier-floor',0)
    world=bpy.data.worlds.new('WORLD-MOC-atelier');world.use_nodes=True;scene.world=world
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
    bg.inputs['Color'].default_value=(.64,.71,.77,1);bg.inputs['Strength'].default_value=.12
    for name,pos,power,size,color in [('window',(-3.3,-4.5,5.5),650,2.4,(1,.91,.79)),('edge',(2.4,1.5,3.8),420,1.5,(1,.96,.86)),('bounce',(3,-4,2),65,3,(.78,.86,1))]:
        d=bpy.data.lights.new('LGT-MOC-atelier-'+name,'AREA');d.energy=power;d.size=size;d.color=color
        ob=bpy.data.objects.new(d.name,d);scene.collection.objects.link(ob);ob.location=pos;f.look_at(ob,(0,0,.9))
    d=bpy.data.cameras.new('CAM-MOC-atelier');f.enum(d,'type','PERSP');d.lens=68
    camera=bpy.data.objects.new(d.name,d);scene.collection.objects.link(camera);scene.camera=camera
    try:scene.render.engine='CYCLES'
    except TypeError:raise
    scene.cycles.use_denoising=True;scene.render.use_persistent_data=True
    scene.render.resolution_percentage=100
    f.enum(scene.render.image_settings,'file_format','PNG');f.enum(scene.render.image_settings,'color_mode','RGB')
    scene.cycles.device='CPU'
    prefs=bpy.context.preferences.addons['cycles'].preferences
    try:
        prefs.compute_device_type='OPTIX';prefs.get_devices()
        for device in prefs.devices:device.use=device.type=='OPTIX'
        if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
    except (TypeError,RuntimeError):pass
    return scene,pivot,product


def render(scene,path,size,pos,target,samples):
    path.parent.mkdir(parents=True,exist_ok=True)
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.camera.location=pos;f.look_at(scene.camera,target)
    scene.cycles.samples=samples;scene.render.filepath=str(path)
    try:bpy.ops.render.render(write_still=True,scene=NAME)
    except RuntimeError:
        scene.cycles.device='CPU';bpy.ops.render.render(write_still=True,scene=NAME)


if __name__=='__main__':
    started=time.time();scene,pivot,product=build();dest=ROOT/'renders/product-v2'
    render(scene,dest/'hero-desktop.png',(1600,1500),(3.0,-6.5,2.8),(.20,0,.86),128)
    render(scene,dest/'hero-mobile.png',(1000,1200),(2.7,-6.8,2.9),(.22,0,.88),128)
    render(scene,dest/'macro.png',(1600,900),(.95,-2.70,1.75),(0,-.18,1.12),160)
    keep=set(product+[pivot,scene.camera])
    for ob in scene.objects:
        if ob not in keep and ob.type not in {'LIGHT','CAMERA'} and ob.name not in {'GEO-MOC-atelier-ground','GEO-MOC-atelier-stone-slab'}:ob.hide_render=True
    for i in range(24):
        pivot.rotation_euler[2]=i*math.tau/24
        render(scene,dest/'spin'/f'{i:02}.png',(900,1050),(0,-5.7,2.0),(0,0,.96),64)
    pivot.rotation_euler[2]=0
    for ob in scene.objects:ob.hide_render=False
    scene.camera.location=(3.0,-6.5,2.8);f.look_at(scene.camera,(.20,0,.86))
    scene.render.resolution_x=1600;scene.render.resolution_y=1500;scene.cycles.samples=128
    for font in bpy.data.fonts:
        if font.filepath and font.filepath!='<builtin>':font.pack()
    # Export just this scene, then make the standalone file's active scene explicit.
    path=ROOT/'source/moc-product-v02.blend'
    bpy.data.libraries.write(str(path),{scene},fake_user=True,compress=True)
    for other in list(bpy.data.scenes):
        if other!=scene:bpy.data.scenes.remove(other)
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    (dest/'report.json').write_text(json.dumps({'scene':NAME,'objects':len(scene.objects),'seconds':round(time.time()-started,2),'frames':24,'device':scene.cycles.device},indent=2))
    print('ATELIER_RENDER_DONE',flush=True)
