"""Original espresso studio, isolated from the user's interactive Blender file."""
import bpy, math, sys, json, time
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import farm_scene as f
import journey_scene as j
NAME='MOC - Extraction Studio'

def build():
    s=bpy.data.scenes.new(NAME);bpy.context.window.scene=s;j.NAME=f.SCENE=NAME
    for name,color,rough,metal in [('forest',(.025,.064,.048),.3,.15),('brass',(.38,.24,.10),.29,.8),('chrome',(.50,.55,.53),.23,.9),('porcelain',(.83,.79,.70),.23,0),('espresso',(.15,.047,.01),.24,0),('foam',(.43,.23,.07),.5,0),('stone',(.30,.32,.28),.72,0),('backdrop',(.72,.685,.62),.86,0),('dark',(.012,.019,.015),.55,0)]:
        f.material('studio-'+name,color,rough,metal=metal)
    box=lambda name,pos,size,mat,r=.025:f.box('studio-'+name,pos,size,'studio-'+mat,r)
    tube=lambda name,pts,r,mat:f.tube('studio-'+name,pts,r,'studio-'+mat)
    box('base',(0,0,.10),(2.6,1.46,.2),'forest',.07)
    box('body',(0,.30,1.04),(2.4,.84,1.58),'forest',.12)
    box('face',(0,-.14,1.10),(2.16,.045,1.23),'brass',.03)
    box('tray',(0,-.55,.24),(2.40,.91,.11),'chrome',.035)
    for x in range(23):box('tray-slot-'+str(x),((x-11)*.092,-.54,.299),(.025,.72,.003),'dark',.003)
    box('top',(0,.3,1.88),(2.50,.92,.09),'chrome',.03)
    for x in [-1.02,1.02]:tube('cup-rail',[(x,-.02,1.96),(x,.64,1.96)],.023,'chrome')
    tube('rear-rail',[(-1.02,.64,1.96),(1.02,.64,1.96)],.023,'chrome')
    for x in [-.68,.68]:
        g=j.cylinder('studio-gauge',(x,-.182,1.47),.18,.038,'studio-chrome');g.rotation_euler[0]=math.pi/2
        d=j.cylinder('studio-dial',(x,-.209,1.47),.145,.018,'studio-porcelain');d.rotation_euler[0]=math.pi/2
        for n in range(9):
            a=math.radians(30+n*30)
            tube('tick',[(x+.12*math.cos(a),-.222,1.47+.12*math.sin(a)),(x+.1*math.cos(a),-.223,1.47+.1*math.sin(a))],.006,'dark')
        tube('needle',[(x,-.229,1.47),(x+.055,-.229,1.55)],.008,'forest')
    j.text('studio-mark','M O C',(0,-.175,1.40),.13,'studio-porcelain')
    group=j.cylinder('studio-group',(0,-.38,1.05),.24,.39,'studio-chrome');group.rotation_euler[0]=math.pi/2
    tube('handle',[(.10,-.52,1.0),(.55,-.91,.98)],.065,'dark')
    tube('spout',[(0,-.55,.96),(0,-.57,.87)],.026,'brass')
    tube('steam-wand',[(.94,-.18,1.09),(1.08,-.36,.87),(1.03,-.55,.62)],.028,'chrome')
    cup=(0,-.58,.31)
    j.lathe('studio-cup',cup,[(0,0),(.18,0),(.21,.04),(.29,.35),(.29,.38),(.266,.385),(.262,.35),(.17,.045),(0,.045)],'studio-porcelain',96)
    tube('cup-handle',[(.27+.15*math.sin(math.pi*i/32),-.58,.50+.115*math.cos(math.pi*i/32)) for i in range(33)],.032,'porcelain')
    j.lathe('studio-coffee',(0,-.58,.655),[(0,0),(.253,0)],'studio-espresso',96)
    j.lathe('studio-crema',(0,-.58,.657),[(.219,0),(.253,0)],'studio-foam',96)
    stream=tube('flow',[(0,-.57,.879),(0,-.58,.662)],.012,'espresso')
    ripples=[]
    for k in range(3):
        ob=tube('ripple-'+str(k),[(math.cos(i*math.tau/64),math.sin(i*math.tau/64),0) for i in range(65)],.007,'foam')
        ob.location=(0,-.58,.66);ripples.append(ob)
    box('counter',(0,0,-.055),(3.4,2.1,.11),'stone',.025)
    box('floor',(0,0,-.13),(200,200,.04),'backdrop',0)
    world=bpy.data.worlds.new('WORLD-Extraction');world.use_nodes=True;s.world=world
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.7,.75,.8,1);bg.inputs['Strength'].default_value=.22
    for name,pos,power,size,color in [('window',(-3,-4,6),700,3,(1,.91,.77)),('rim',(3,2,4),550,2,(1,.93,.83)),('fill',(3,-4,2),110,3,(.78,.86,1))]:
        d=bpy.data.lights.new('LGT-'+name,'AREA');d.energy=power;d.size=size;d.color=color
        o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=pos;f.look_at(o,(0,0,1))
    d=bpy.data.cameras.new('CAM-Extraction');f.enum(d,'type','ORTHO')
    cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);s.camera=cam
    cam.location=(3.1,-6.7,3.5);f.look_at(cam,(0,-.1,.9))
    try:s.render.engine='CYCLES'
    except TypeError:raise
    s.cycles.samples=32;s.cycles.use_denoising=True;s.render.use_persistent_data=True
    f.enum(s.render.image_settings,'file_format','PNG');f.enum(s.render.image_settings,'color_mode','RGB')
    s.cycles.device='CPU'
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
        for device in prefs.devices:device.use=device.type=='OPTIX'
        if any(d.use for d in prefs.devices):s.cycles.device='GPU'
    except (TypeError,RuntimeError):pass
    return s,stream,ripples

if __name__=='__main__':
    start=time.time();s,stream,ripples=build();s.render.fps=24
    for view in ['desktop','mobile']:
        dest=ROOT/'renders/extraction'/view;dest.mkdir(parents=True,exist_ok=True)
        s.render.resolution_x,s.render.resolution_y=(1280,800) if view=='desktop' else (720,1440)
        s.camera.data.ortho_scale=6.6 if view=='desktop' else 9.8
        s.camera.data.shift_x=-.20 if view=='desktop' else 0
        s.camera.data.shift_y=.01 if view=='desktop' else .19
        for frame in range(72):
            if (dest/f'{frame:04}.png').exists():
                continue
            phase=frame*math.tau/72
            stream.data.bevel_depth=.012*(1+.13*math.sin(phase*6))
            for k,ob in enumerate(ripples):
                radius=.10+.055*math.sin(phase*2+k*math.tau/3)
                ob.scale=(radius,radius,.22)
            s.render.filepath=str(dest/f'{frame:04}.png')
            try:bpy.ops.render.render(write_still=True,scene=NAME)
            except RuntimeError:s.cycles.device='CPU';bpy.ops.render.render(write_still=True,scene=NAME)
    for other in list(bpy.data.scenes):
        if other!=s:bpy.data.scenes.remove(other)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/moc-extraction-v01.blend'))
    (ROOT/'renders/extraction/report.json').write_text(json.dumps({'scene':NAME,'objects':len(s.objects),'frames_per_view':72,'seconds':round(time.time()-start,2)},indent=2))
    print('EXTRACTION_DONE',flush=True)
