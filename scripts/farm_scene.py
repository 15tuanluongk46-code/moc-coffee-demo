"""Deterministic, isolated MOC farm art source. Execute stages via Blender MCP."""
import bpy
import math
import random
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SCENE = 'MOC - Coffee Origin'
PREFIX = 'MOC-'


def enum(obj, key, value):
    choices = [e.identifier for e in obj.bl_rna.properties[key].enum_items]
    if value not in choices:
        raise ValueError(f'{key}: {value} not in {choices}')
    setattr(obj, key, value)


def scene():
    return bpy.data.scenes[SCENE]


def material(name, color, roughness=.65, noise=False, metal=0):
    mat = bpy.data.materials.new('MAT-MOC-' + name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bs = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metal
    if noise:
        tex = nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 35
        tex.inputs['Detail'].default_value = 3
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .16
        bump.inputs['Distance'].default_value = .035
        mat.node_tree.links.new(tex.outputs['Fac'], bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    return mat


def mat(name):
    return bpy.data.materials['MAT-MOC-' + name]


def mesh(name, verts, faces, material_name, smooth=False):
    data = bpy.data.meshes.new('MOC-' + name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new('GEO-MOC-' + name, data)
    scene().collection.objects.link(obj)
    obj.data.materials.append(mat(material_name))
    for face in data.polygons:
        face.use_smooth = smooth
    return obj


def bevel(obj, width=.06, segments=3):
    types = [x.identifier for x in bpy.types.Modifier.bl_rna.properties['type'].enum_items]
    assert 'BEVEL' in types
    mod = obj.modifiers.new('Soft crafted edges', 'BEVEL')
    mod.width, mod.segments = width, segments
    return obj


def box(name, position, size, material_name, radius=.04):
    x, y, z = (v / 2 for v in size)
    verts = [(-x,-y,-z), (x,-y,-z), (x,y,-z), (-x,y,-z),
             (-x,-y,z), (x,-y,z), (x,y,z), (-x,y,z)]
    faces = [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    obj = mesh(name, verts, faces, material_name)
    obj.location = position
    if radius:
        bevel(obj, radius)
    return obj


def tube(name, points, radius, material_name):
    data = bpy.data.curves.new('MOC-' + name, 'CURVE')
    enum(data, 'dimensions', '3D')
    data.bevel_depth, data.bevel_resolution = radius, 2
    sp = data.splines.new('POLY')
    sp.points.add(len(points)-1)
    for p, co in zip(sp.points, points):
        p.co = (*co, 1)
    obj = bpy.data.objects.new('GEO-MOC-' + name, data)
    scene().collection.objects.link(obj)
    data.materials.append(mat(material_name))
    return obj


def beam(name, a, b, width, material_name):
    a, b = Vector(a), Vector(b)
    obj = box(name, (a+b)/2, (width, width, (b-a).length), material_name, width*.2)
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return obj


def island(name, center, axes, bottom, top, material_name, phase=0):
    n = 72
    verts = []
    for z in (bottom, top):
        for i in range(n):
            t = math.tau*i/n
            r = 1 + .028*math.sin(3*t+phase) + .022*math.cos(5*t)
            verts.append((center[0]+axes[0]*r*math.cos(t), center[1]+axes[1]*r*math.sin(t), z))
    faces = [tuple(reversed(range(n))), tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return bevel(mesh(name, verts, faces, material_name), .09)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def setup():
    if bpy.data.scenes.get(SCENE):
        raise RuntimeError('MOC scene already exists; reuse stages rather than rebuilding over user work.')
    s = bpy.data.scenes.new(SCENE)
    bpy.context.window.scene = s
    palette = {
        'cream':(.73,.66,.53), 'clay':(.27,.13,.065), 'soil':(.15,.069,.032),
        'moss':(.18,.245,.072), 'grass':(.27,.34,.105),
        'leaf':(.033,.16,.07), 'leaf-light':(.075,.255,.092),
        'wood':(.24,.115,.052), 'wood-light':(.46,.28,.12),
        'plaster':(.73,.58,.36), 'roof':(.025,.09,.057),
        'cherry':(.49,.024,.016), 'cherry-gold':(.7,.23,.035),
        'copper':(.42,.18,.07), 'path':(.57,.405,.225), 'dark':(.02,.038,.024),
    }
    for name, color in palette.items():
        material(name,color, .38 if name.startswith('leaf') or name=='cherry' else .7,
                 noise=name in {'soil','clay','wood','plaster','cream'},
                 metal=.65 if name=='copper' else 0)
    world = bpy.data.worlds.new('MOC-Warm Studio')
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (.7,.77,.88,1)
    bg.inputs['Strength'].default_value = .35
    s.world = world
    for name, loc, power, size, color in [
        ('key',(-4,-6,11),1900,7,(1,.84,.63)),
        ('fill',(6,-1,7),1100,8,(.8,.9,1)),
        ('rim',(1,7,9),2300,6,(1,.92,.72)),
    ]:
        data = bpy.data.lights.new('LGT-MOC-'+name,'AREA')
        data.energy, data.size, data.color = power, size, color
        obj = bpy.data.objects.new(data.name,data)
        s.collection.objects.link(obj)
        obj.location = loc
        look_at(obj,(0,0,0))
    for name in ('desktop','mobile'):
        data = bpy.data.cameras.new('CAM-MOC-'+name)
        enum(data,'type','ORTHO')
        obj = bpy.data.objects.new(data.name,data)
        s.collection.objects.link(obj)
        obj.location=(10,-16,12)
        look_at(obj,(0,0,1))
    box('studio-ground',(0,0,-.82),(200,200,.1),'cream',0)
    configure('desktop',True)
    print('MOC setup complete; isolated scene and materials created.')


def landscape():
    island('earth-core',(0,0),(4.7,3.6),-.55,.05,'clay')
    island('earth-band',(0,0),(4.62,3.53),-.22,.10,'soil')
    island('living-ground',(0,0),(4.65,3.52),.08,.29,'moss')
    for k, (c,a,z) in enumerate([
        ((-1.6,.65),(2.7,2.45),.61),
        ((-1.9,1.1),(2.30,1.92),.96),
        ((-2.05,1.6),(1.80,1.30),1.29),
    ]):
        island(f'terrace-earth-{k}',c,a,.24,z,'soil',k*.5)
        island(f'terrace-green-{k}',c,a,z-.04,z+.10,'grass',k*.5)
    # Farm shed: open porch, generous roof, deep window reveals.
    box('shed-body',(1.45,1.75,1.29),(2.0,1.6,2),'plaster')
    box('shed-foundation',(1.45,1.6,.36),(2.6,2.3,.20),'wood-light')
    x,y,z = 1.45,1.75,2.32
    verts=[(x-1.2,y-1.10,z),(x+1.2,y-1.10,z),(x+1.2,y+1.10,z),
           (x-1.2,y+1.10,z),(x,y-1.10,z+.86),(x,y+1.10,z+.86)]
    mesh('shed-gables',verts,[(0,1,4),(3,5,2)],'plaster')
    for side in (-1,1):
        panel=box(f'roof-{side}',(x+side*.65,y,2.72),(1.61,2.45,.13),'roof')
        panel.rotation_euler[1]=side*math.radians(34)
        for j in range(13):
            yy=y-1.17+j*.195
            beam(f'roof-seam-{side}-{j}',(x,yy,3.2),(x+side*1.32,yy,2.31),.022,'copper')
    box('door',(1.5,.94,1.10),(.62,.065,1.5),'dark')
    for xx in (.9,2.05):
        box('window',(xx,.92,1.8),(.4,.08,.42),'roof')
        beam('window-sill',(xx-.25,.85,1.56),(xx+.25,.85,1.56),.065,'wood-light')
    box('porch-awning',(1.45,.43,2.05),(2.55,1.15,.11),'roof')
    for xx in (.30,2.60):
        beam('porch-post',(xx,.0,.40),(xx,.0,2.05),.09,'wood')
    for i in range(4):
        box(f'entry-step-{i}',(1.45,-.40+i*.15,.30+i*.035),(1.05,.18,.07),'wood-light')
    # Winding footpath kept clear through the farm.
    centers=[(3.5,-2.35),(3.0,-1.8),(2.25,-1.1),(1.45,-.45)]
    for i in range(len(centers)-1):
        a,b=centers[i],centers[i+1]
        for j in range(6):
            t=j/6
            xx,yy=a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t
            stone=box(f'path-{i}-{j}',(xx,yy,.32),(.48,.35,.06),'path',.10)
            stone.rotation_euler[2]=-.5+i*.35
    print('MOC landscape + shed complete.')


def plants():
    rng = random.Random(231)
    verts, faces, indices = [], [], []
    materials=['wood','leaf','leaf-light','cherry','cherry-gold']
    def face(points, index):
        base=len(verts); verts.extend(points)
        faces.append(tuple(range(base,base+len(points)))); indices.append(index)
    def branch(a,b,r):
        a,b=Vector(a),Vector(b)
        q=(b-a).to_track_quat('Z','Y')
        loops=[]
        for center in (a,b):
            loops.append([center+q@Vector((r*math.cos(i*math.tau/6),r*math.sin(i*math.tau/6),0)) for i in range(6)])
        for i in range(6): face([loops[0][i],loops[0][(i+1)%6],loops[1][(i+1)%6],loops[1][i]],0)
    def berry(center,r,index):
        center=Vector(center)
        for k in range(6):
            for j in range(8):
                pts=[]
                for kk,jj in [(k,j),(k,j+1),(k+1,j+1),(k+1,j)]:
                    p=math.pi*kk/6; t=math.tau*jj/8
                    pts.append(center+Vector((r*math.sin(p)*math.cos(t),r*math.sin(p)*math.sin(t),r*1.15*math.cos(p))))
                face(pts,index)
    def leaf(start,angle,length,width,index):
        start=Vector(start); d=Vector((math.cos(angle),math.sin(angle),0)); side=Vector((-d.y,d.x,0))
        for i in range(8):
            for half in (-1,1):
                pts=[]
                for t,e in [(i/8,0),(i/8,half),((i+1)/8,half),((i+1)/8,0)]:
                    w=math.sin(math.pi*t)**.8*width*(1+.045*math.sin(10*math.pi*t))
                    pts.append(start+d*(length*t)+side*(w*e)+Vector((0,0,.15*math.sin(math.pi*t)-.15*t-.055*abs(e)*math.sin(math.pi*t))))
                face(pts,index)
    branch((0,0,0),(.025,.015,1.1),.035)
    for level in range(5):
        z=.30+level*.17
        for side in (0,1):
            ang=level*1.6+side*math.pi
            d=Vector((math.cos(ang),math.sin(ang),.18))
            a=Vector((0,0,z)); b=a+d*(.42-level*.045)
            branch(a,b,.012)
            for pos in (.45,.90):
                for sign in (-1,1):
                    start=a+(b-a)*pos
                    leaf(start,ang+sign*.85,.38-level*.028,.11,1+(level+side)%2)
            for j in range(3):
                center=a+(b-a)*(.25+j*.18)+Vector((.045*(-1)**j,-.01,-.015))
                berry(center,.060,3 if j!=2 or level%2 else 4)
    proto=mesh('coffee-shrub-00',verts,faces,'wood',True)
    for name in materials[1:]: proto.data.materials.append(mat(name))
    for poly,idx in zip(proto.data.polygons,indices): poly.material_index=idx
    positions=[]
    for yy,z,xs in [(-2.3,.30,[-2.65,-1.7,-.7,.3]),(-1.45,.71,[-3,-2,-1]),
                    (-.55,1.06,[-3.25,-2.35,-1.4]),(.45,1.39,[-3,-2.1,-1.2]),
                    (1.55,1.39,[-3,-2.1,-1.2]),(2.35,1.39,[-2.6,-1.65]),
                    (-2.65,.30,[1.35]),(2.85,.30,[.15,.95,2.1])]:
        positions += [(xx,yy,z) for xx in xs]
    for i,position in enumerate(positions):
        px,py,_=position
        ground=.29
        for center,axes,height,phase in [((-1.6,.65),(2.7,2.45),.71,0),((-1.9,1.1),(2.3,1.92),1.06,.5),((-2.05,1.6),(1.8,1.3),1.39,1)]:
            dx,dy=(px-center[0])/axes[0],(py-center[1])/axes[1]
            angle=math.atan2(dy,dx)
            edge=1+.028*math.sin(3*angle+phase)+.022*math.cos(5*angle)
            if math.hypot(dx,dy)<edge-.045:
                ground=height
        position=(px,py,ground)
        obj=proto if i==0 else bpy.data.objects.new(f'GEO-MOC-coffee-shrub-{i:02}',proto.data)
        if i: scene().collection.objects.link(obj)
        obj.location=position
        scale=rng.uniform(.83,1.14)
        obj.scale=(scale,scale,scale)
        obj.rotation_euler[2]=rng.uniform(0,math.tau)
    print(f'MOC coffee plantation: {len(positions)} linked shrubs; {len(verts)} vertices/prototype.')


def details():
    rng=random.Random(42)
    # Raised drying beds with a layer of cherries.
    for j,(x,y) in enumerate([(0,-1.28),(1,-1.70)]):
        box(f'drying-bed-{j}',(x,y,.70),(.75,1.25,.08),'wood')
        box(f'cherry-bed-{j}',(x,y,.76),(.62,1.10,.06),'cherry')
        for dx in (-.36,.36):
            box('tray-rail',(x+dx,y,.81),(.035,1.25,.15),'wood-light')
            for dy in (-.55,.55):
                beam('tray-leg',(x+dx,y+dy,.3),(x+dx,y+dy,.72),.045,'wood')
        for dx in (-.2,0,.2):
            for dy in (-.43,-.22,0,.22,.43):
                box('drying-cherries',(x+dx,y+dy,.81),(.13,.14,.075),'cherry-gold' if rng.random()<.13 else 'cherry',.035)
    # Fence follows the right side of the farm.
    fence=[(3.90,-1.40,.30),(4.12,-.5,.30),(4.0,.50,.30),(3.65,1.45,.30),(3.05,2.20,.30)]
    for i,(x,y,z) in enumerate(fence):
        box('fence-post',(x,y,z+.37),(.10,.10,.8),'wood-light')
        if i:
            for dz in (.25,.55):
                a=fence[i-1]; beam('fence-rail',(a[0],a[1],a[2]+dz),(x,y,z+dz),.055,'wood-light')
    # Stack harvest boxes at the porch.
    for k,(x,y,z) in enumerate([(2.8,.75,.52),(2.85,1.4,.52),(2.85,1.4,.97)]):
        box('harvest-crate',(x,y,z),(.55,.48,.42),'wood')
        for h in (-.13,0,.13):
            box('crate-slat',(x,y-.25,z+h),(.57,.035,.07),'wood-light',.012)
    for i in range(45):
        a=rng.uniform(0,math.tau)
        x,y=4.4*math.cos(a),3.28*math.sin(a)
        for j in range(3):
            end=(x+rng.uniform(-.1,.1),y+rng.uniform(-.1,.1),.45+rng.random()*.14)
            beam('grass-blade',(x,y,.27),end,.022,'leaf-light')
    print('MOC drying racks, harvest crates, fence and grasses complete.')


def configure(view='desktop', preview=False):
    s=scene(); cam=bpy.data.objects['CAM-MOC-'+view]; s.camera=cam
    desktop=view=='desktop'
    cam.data.ortho_scale=19.0 if desktop else 17.0
    cam.data.shift_x=-.16 if desktop else 0
    cam.data.shift_y=.025 if desktop else .17
    s.render.resolution_x=1600 if desktop else 900
    s.render.resolution_y=1000 if desktop else 1200
    s.render.resolution_percentage=50 if preview else 100
    enum(s.render.image_settings,'file_format','PNG')
    enum(s.render.image_settings,'color_mode','RGB')
    try: s.render.engine='CYCLES'
    except TypeError: pass
    if s.render.engine=='CYCLES':
        s.cycles.samples=24 if preview else 64
        s.cycles.use_denoising=True
    (ROOT/'renders').mkdir(exist_ok=True)
    s.render.filepath=str(ROOT/'renders'/f'farm-{view}{"-preview" if preview else ""}.png')
    return s


def export():
    out=ROOT/'source'/'moc-farm-v01.blend'
    out.parent.mkdir(exist_ok=True)
    bpy.data.libraries.write(str(out),{scene()},fake_user=True,compress=True)
    print(f'MOC standalone scene exported: {out}')
