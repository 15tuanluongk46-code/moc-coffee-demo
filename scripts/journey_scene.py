"""Original MOC art: four physically connected stations and a baked camera journey."""
import bpy
import math
import random
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import farm_scene as f

NAME = 'MOC - Complete Journey'
CENTERS = [Vector((i * 14 * .848, i * 14 * .53, 0)) for i in range(4)]
FRAMES = 288
STOPS = [1, 97, 193, 288]


def s():
    return bpy.data.scenes[NAME]


def lathe(name, position, profile, material, n=64):
    verts = [(r * math.cos(i * math.tau/n), r * math.sin(i * math.tau/n), z)
             for r, z in profile for i in range(n)]
    faces = [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)
             for j in range(len(profile)-1) for i in range(n)]
    o = f.mesh(name, verts, faces, material, True)
    o.location = position
    return o


def cylinder(name, pos, radius, height, material):
    return lathe(name, pos, [(0,0),(radius,0),(radius,height),(0,height)], material)


def text(name, body, pos, size, material='cream'):
    d = bpy.data.curves.new('MOC-'+name, 'FONT')
    d.body, d.size, d.extrude = body, size, .002
    f.enum(d, 'align_x', 'CENTER')
    o = bpy.data.objects.new('GEO-MOC-'+name,d)
    s().collection.objects.link(o)
    d.materials.append(f.mat(material))
    o.location=pos
    o.rotation_euler=(math.pi/2,0,0)
    return o


def bean(name, pos, scale=.12, angle=0):
    o=lathe(name,pos,[(0,-.10),(.13,-.07),(.17,0),(.13,.07),(0,.10)],'bean',24)
    o.scale=(scale/.12,scale/.12*.65,scale/.12)
    o.rotation_euler[2]=angle
    return o


def cup(name, pos, scale=1, latte=False):
    start=set(s().objects)
    x,y,z=pos
    lathe(name+'-saucer',(x,y,z),[(0,0),(.82,0),(.88,.06),(.85,.11),(.5,.12),(0,.08)],'ceramic')
    lathe(name+'-cup',(x,y,z+.1),[(0,0),(.38,0),(.43,.08),(.59,.64),(.58,.70),(.53,.71),(.52,.65),(.36,.12),(0,.12)],'ceramic')
    lathe(name+'-coffee',(x,y,z+.70),[(0,0),(.525,0)],'crema' if latte else 'coffee')
    f.tube(name+'-handle',[(x+.50+.33*math.sin(math.pi*i/24),y,z+.46+.27*math.cos(math.pi*i/24)) for i in range(25)],.073,'ceramic')
    if latte:
        for k in range(5):
            yy=y-.19+k*.072
            width=.21*(1-k*.14)
            f.tube(name+'-latte',[(x+width*math.sin(math.tau*j/40),yy+.045*math.cos(math.tau*j/40),z+.709) for j in range(41)],.015,'milk')
        f.tube(name+'-latte-stem',[(x,y-.25,z+.714),(x,y+.19,z+.714)],.013,'milk')
    # Scaling about the cup origin, not world origin.
    for o in set(s().objects)-start:
        o.location=Vector(pos)+(o.location-Vector(pos))*scale
        o.scale*=scale
        if o.type=='CURVE':
            # Curves have baked world-space points.
            for spline in o.data.splines:
                for p in spline.points:
                    v=Vector(p.co[:3]); p.co=(*((v-Vector(pos))*scale+Vector(pos)),1)
            o.scale=(1,1,1)


def platform(name):
    f.island(name+'-base',(0,0),(4.45,3.3),-.55,.1,'clay')
    f.island(name+'-top',(0,0),(4.43,3.28),.08,.3,'plaster')
    for i in range(13):
        x=-3.8+i*.6
        length=5.7*math.sqrt(max(0,1-(x/4.4)**2))
        f.box(name+'-floor-board',(x,0,.31),(.56,length,.05),'wood-light',.018)


def roast():
    platform('roastery')
    # Solid framed roasting drum with brass barrel, intake hopper and chimney.
    for x in (-1.15,1.15):
        for y in (-.2,1.2):
            f.box('roaster-leg',(x,y,1.05),(.22,.24,1.48),'roof')
    f.box('roaster-plinth',(0,.5,.52),(3,2,.24),'roof')
    drum=lathe('roasting-drum',(0,1.6,1.85),[(0,0),(1.04,0),(1.12,.12),(1.12,1.8),(1.03,1.92),(0,1.92)],'copper')
    drum.rotation_euler[0]=math.pi/2
    front=cylinder('drum-front',(0,-.35,1.85),.99,.13,'roof'); front.rotation_euler[0]=math.pi/2
    center=cylinder('drum-brass-hub',(0,-.50,1.85),.29,.12,'copper'); center.rotation_euler[0]=math.pi/2
    for i in range(12):
        a=i*math.tau/12
        bolt=cylinder('drum-bolt',(.86*math.cos(a),-.505,1.85+.86*math.sin(a)),.04,.055,'steel'); bolt.rotation_euler[0]=math.pi/2
    lathe('hopper',(0,.55,2.8),[(.23,0),(.28,.3),(.9,.92),(.9,.97),(.84,.97),(.24,.3)],'copper')
    f.tube('roaster-flue',[(.65,1.5,2.5),(.65,1.5,4.4),(1.3,1.5,4.4)],.21,'roof')
    lathe('cooling-tray',(0,-1.6,.9),[(0,0),(1.15,0),(1.2,.1),(1.2,.4),(1.12,.42),(1.10,.14),(0,.14)],'steel')
    cylinder('cooling-coffee',(0,-1.6,1.05),1.10,.055,'bean')
    f.beam('tray-stirrer',(-1,-1.6,1.19),(1,-1.6,1.19),.08,'steel')
    cylinder('tray-base',(0,-1.6,.32),.45,.7,'roof')
    # Control face with gauge and knob.
    f.box('control-box',(1.65,.3,1.55),(.55,.5,1.3),'roof')
    gauge=cylinder('roast-gauge',(1.65,.02,1.83),.19,.03,'ceramic'); gauge.rotation_euler[0]=math.pi/2
    f.beam('gauge-needle',(1.65,-.022,1.83),(1.74,-.022,1.95),.015,'dark')
    text('roast-brand','MOC',(0,-.52,2.30),.23)
    for x,y in [(-2.65,1.4),(-2.8,.4),(-2.2,2)]:
        lathe('jute-sack',(x,y,.35),[(.35,0),(.48,.15),(.45,.95),(.3,1.16),(.28,1.25),(0,1.28)],'plaster',32)
    rng=random.Random(9)
    for i in range(44):
        a=rng.random()*math.tau; r=rng.random()**.5*.95
        bean('cooling-bean',(r*math.cos(a),-1.6+r*math.sin(a),1.14),.055,a)
    f.box('roast-back-sign',(0,2.65,2.3),(2.8,.12,.65),'roof')
    text('roast-sign','THE ROASTERY',(0,2.57,2.20),.21)


def espresso():
    platform('espresso')
    f.box('bar-cabinet',(0,0,1.13),(5.7,1.85,1.6),'roof',.1)
    for x in [i*.22-2.6 for i in range(25)]:
        f.box('bar-flute',(x,-.945,1.12),(.055,.055,1.37),'wood-light',.02)
    f.box('stone-counter',(0,0,2),(6.05,2.1,.20),'ceramic',.06)
    f.box('espresso-machine',(0,.2,2.81),(2.8,1.20,1.3),'roof',.15)
    f.box('machine-brass-face',(0,-.425,2.99),(2.56,.065,.72),'copper',.04)
    f.box('machine-driptray',(0,-.50,2.2),(2.70,.65,.1),'steel')
    for x in (-.7,0,.7):
        group=cylinder('group-head',(x,-.68,2.76),.17,.23,'steel');group.rotation_euler[0]=math.pi/2
        f.beam('portafilter',(x,-.75,2.62),(x,-1.12,2.59),.07,'wood')
        gauge=cylinder('espresso-dial',(x,-.465,3.08),.125,.035,'ceramic');gauge.rotation_euler[0]=math.pi/2
        f.beam('pressure-needle',(x,-.51,3.08),(x+.06,-.51,3.14),.012,'roof')
    for x in (-.68,.68):
        cup('espresso-cup',(x,-.59,2.27),.33)
        f.tube('espresso-stream',[(x,-.62,2.64),(x,-.62,2.5)],.013,'coffee')
    f.tube('steam-wand',[(1.3,-.5,2.9),(1.5,-.75,2.65),(1.5,-.75,2.38)],.035,'steel')
    text('machine-wordmark','MOC',(0,-.475,2.78),.18,'cream')
    # Grinder with a transparent-free readable hopper and beans.
    f.box('grinder-body',(-2.15,.10,2.48),(.64,.7,.74),'copper')
    lathe('grinder-hopper',(-2.15,.10,2.83),[(.22,0),(.38,.13),(.4,.7),(.36,.73),(0,.73)],'roof')
    cylinder('grinder-base',(-2.15,.08,2.1),.48,.08,'steel')
    cup('bar-latte',(2.15,-.32,2.11),.48,True)
    # Open cafe frame, overhead warm lamps and two stools.
    for x in (-3.25,3.25):
        f.beam('cafe-upright',(x,1.45,.3),(x,1.45,4.6),.12,'wood')
    f.beam('cafe-header',(-3.3,1.45,4.6),(3.3,1.45,4.6),.16,'wood')
    for x in (-1.8,1.8):
        f.tube('pendant-cord',[(x,1.4,4.6),(x,.55,3.95)],.019,'dark')
        lathe('pendant-shade',(x,.55,3.8),[(.48,0),(.48,.04),(.15,.32),(.12,.34)],'copper')
        cylinder('stool-seat',(x,-2.15,1.03),.48,.16,'wood')
        for dx,dy in [(-.25,-.25),(.25,-.25),(0,.28)]:
            f.beam('stool-leg',(x+dx*1.4,-2.15+dy*1.4,.32),(x+dx,-2.15+dy,1.04),.085,'roof')


def ritual():
    f.island('ritual-island',(0,0),(4.3,3.2),-.55,.18,'clay')
    f.island('ritual-plinth',(0,0),(4.28,3.18),.15,.35,'plaster')
    cylinder('display-block',(0,-.2,.35),2.65,.40,'roof')
    cylinder('display-top',(0,-.2,.74),2.67,.08,'wood-light')
    cup('hero-latte',(.55,-1.04,.82),1.75,True)
    f.box('coffee-bag',(-1.15,.55,2.05),(1.65,.9,2.48),'roof',.16)
    f.box('bag-fold',(-1.15,.55,3.32),(1.68,.25,.22),'roof',.04)
    f.box('bag-seal',(-1.15,.37,3.34),(1.37,.06,.06),'copper',.012)
    f.box('bag-label',(-1.15,.08,2.10),(1.34,.035,1.57),'ceramic',.012)
    text('bag-brand','MOC',(-1.15,.055,2.38),.46,'roof')
    text('bag-origin','CAU DAT',(-1.15,.05,1.98),.15,'roof')
    text('bag-kind','ARABICA',(-1.15,.05,1.75),.12,'roof')
    text('bag-weight','250 g',(-1.15,.05,1.50),.12,'roof')
    rng=random.Random(16)
    for i in range(15):
        x=rng.uniform(1.5,2.1);y=rng.uniform(.1,1.2)
        bean('scattered-bean',(x,y,.9),.10,rng.random()*math.tau)
    # Quiet botanical echo of the beginning.
    proto=bpy.data.objects.get('GEO-MOC-coffee-shrub-00')
    if proto:
        plant=bpy.data.objects.new('GEO-MOC-ritual-coffee-plant',proto.data)
        s().collection.objects.link(plant);plant.location=(2,1.5,.72);plant.scale=(1.4,)*3
        lathe('planter',(2,1.5,.35),[(.34,0),(.44,.55),(.40,.60),(.36,.58)],'ceramic')


def build():
    if NAME in bpy.data.scenes:
        raise RuntimeError('Journey already exists; do not overwrite it implicitly.')
    dest=bpy.data.scenes.new(NAME)
    dest.world=bpy.data.scenes['MOC - Coffee Origin'].world.copy()
    source=bpy.data.scenes['MOC - Coffee Origin']
    for o in source.objects:
        if o.type not in {'CAMERA','LIGHT'} and o.name!='GEO-MOC-studio-ground':
            dup=o.copy(); dest.collection.objects.link(dup)
    f.SCENE=NAME
    bpy.context.window.scene=dest
    for name,color,rough,metal in [
        ('ceramic',(.87,.80,.65),.24,0),('steel',(.4,.45,.43),.26,.8),
        ('bean',(.075,.025,.010),.65,0),('coffee',(.055,.012,.003),.2,0),
        ('crema',(.40,.18,.05),.38,0),('milk',(.95,.87,.70),.3,0)]:
        f.material(name,color,rough,metal=metal)
    f.box('journey-ground',(24,15,-.83),(220,180,.10),'cream',0)
    for i,fn in enumerate((roast,espresso,ritual),1):
        before=set(dest.objects);fn()
        for obj in set(dest.objects)-before:
            obj.location+=CENTERS[i]
    # Three-point light rigs repeat with identical color and exposure per station.
    for center in CENTERS:
        for o in source.objects:
            if o.type=='LIGHT':
                dup=o.copy();dup.data=o.data.copy();dest.collection.objects.link(dup)
                dup.location+=center
    # Stations connect through camera travel; connector stepping stones removed.
    camera_tracks()
    dest.frame_set(1)
    print({'scene':NAME,'objects':len(dest.objects),'frames':FRAMES})


def progress(frame):
    # Readable slow orbit on a chapter, then smooth physical travel to the next.
    t=(frame-1)/(FRAMES-1)*3
    chapter=min(2,int(t)); local=t-chapter
    move=max(0,min(1,(local-.28)/.55))
    move=move*move*(3-2*move)
    return chapter,move


def camera_tracks():
    dest=s(); dest.frame_start=1;dest.frame_end=FRAMES;dest.render.fps=24
    for view in ('desktop','mobile'):
        d=bpy.data.cameras.new('CAM-MOC-journey-'+view);f.enum(d,'type','ORTHO')
        cam=bpy.data.objects.new(d.name,d);dest.collection.objects.link(cam)
        d.ortho_scale=19.8 if view=='desktop' else 18.0
        d.shift_x=-.13 if view=='desktop' else 0
        d.shift_y=.035 if view=='desktop' else .15
        for frame in range(1,FRAMES+1):
            i,t=progress(frame)
            center=CENTERS[i].lerp(CENTERS[i+1],t)
            sway=.35*math.sin((frame-1)/FRAMES*math.tau)
            cam.location=center+Vector((10+sway,-16,12))
            f.look_at(cam,center+Vector((0,0,1.05)))
            cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame)
        action=cam.animation_data.action
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for key in fc.keyframe_points:
                            f.enum(key,'interpolation','LINEAR')
    configure('desktop')


def configure(view):
    dest=s();dest.camera=bpy.data.objects['CAM-MOC-journey-'+view]
    if view=='mobile':
        dest.camera.data.ortho_scale=29
        dest.camera.data.shift_y=.12
    dest.render.resolution_x=1280 if view=='desktop' else 720
    dest.render.resolution_y=800 if view=='desktop' else 1440
    dest.render.resolution_percentage=100
    try: dest.render.engine='CYCLES'
    except TypeError: pass
    dest.cycles.samples=16;dest.cycles.use_denoising=True
    dest.render.use_persistent_data=True
    f.enum(dest.render.image_settings,'file_format','PNG')
    f.enum(dest.render.image_settings,'color_mode','RGB')
    return dest


def export():
    path=ROOT/'source'/'moc-journey-v01.blend'
    bpy.data.libraries.write(str(path),{s()},fake_user=True,compress=True)
    print(str(path))
