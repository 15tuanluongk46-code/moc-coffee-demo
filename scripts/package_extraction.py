"""Package the native 3s cycle as a smooth 6s, 24fps studio loop."""
import json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'web/media/extraction';out.mkdir(parents=True,exist_ok=True)
reports=[]
for view in ['desktop','mobile']:
    source=ROOT/'renders/extraction'/view
    files=[source/f'{i:04}.png' for i in range(72)]
    missing=[str(p) for p in files if not p.exists()]
    if missing:raise SystemExit(f'{view}: {len(missing)} frames missing')
    with Image.open(files[0]) as image:image.save(out/f'{view}.webp',quality=88)
    subprocess.run(['ffmpeg','-y','-framerate','12','-i',str(source/'%04d.png'),'-vf','minterpolate=fps=24:mi_mode=blend,tpad=stop_mode=clone:stop_duration=0.2,setpts=N/(24*TB)','-frames:v','144','-r','24','-fps_mode','cfr','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(out/f'{view}.mp4')],check=True,capture_output=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out/f'{view}.mp4')]))
    assert int(probe['streams'][0]['nb_frames'])==144
    assert probe['streams'][0]['avg_frame_rate']=='24/1'
    assert abs(float(probe['format']['duration'])-6)<.01
    sheet=Image.new('RGB',(900,600),'#eeeae2');draw=ImageDraw.Draw(sheet)
    for i,frame in enumerate([0,12,24,36,48,60]):
        with Image.open(files[frame]) as im:
            im.thumbnail((300,270));x=(i%3)*300+(300-im.width)//2;y=(i//3)*300
            sheet.paste(im,(x,y));draw.text(((i%3)*300+8,y+277),f'{frame/12:.1f}s',fill='#173c32')
    sheet.save(ROOT/f'renders/extraction/contact-{view}.jpg',quality=80)
    reports.append({'view':view,'bytes':(out/f'{view}.mp4').stat().st_size,'probe':probe})
(ROOT/'renders/extraction/media-report.json').write_text(json.dumps(reports,indent=2))
print(json.dumps([{'view':r['view'],'bytes':r['bytes']} for r in reports]))
