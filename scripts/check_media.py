"""Frame integrity, sampled contact sheets, and measured image differences (not visual approval)."""
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT=Path(__file__).resolve().parents[1]
reports=[]
for view,size in [('desktop',(1280,800)),('mobile',(720,1440))]:
    folder=ROOT/'renders'/('frames-'+view)
    sample_frames=[1,30,48,68,97,126,145,165,193,222,250,288]
    sheet=Image.new('RGB',(960,720),'#eeeae2')
    previous=None
    differences=[]
    for frame in range(1,289):
        with Image.open(folder/f'{frame:04}.png') as image:
            assert image.size==size,(view,frame,image.size)
            image.load()
            tiny=image.convert('RGB').resize((160,100))
            assert max(ImageStat.Stat(tiny).stddev)>4,(view,frame,'Near-uniform frame')
            if previous is not None:
                differences.append({'frame':frame,'mean_rgb_delta':round(sum(ImageStat.Stat(ImageChops.difference(previous,tiny)).mean)/3,4)})
            previous=tiny
            if frame in sample_frames:
                i=sample_frames.index(frame);thumb=image.convert('RGB');thumb.thumbnail((240,214))
                x=(i%4)*240+(240-thumb.width)//2;y=(i//4)*240+20
                sheet.paste(thumb,(x,y))
                ImageDraw.Draw(sheet).text(((i%4)*240+8,(i//4)*240+4),f'{frame:03} / {(frame-1)/24:.2f}s',fill='#173c32')
    sheet.save(ROOT/'renders'/f'contact-{view}.jpg',quality=82)
    reports.append({'view':view,'frames':288,'size':size,'top_deltas':sorted(differences,key=lambda d:d['mean_rgb_delta'],reverse=True)[:12],
                    'all_deltas':differences,'sampled_frames':sample_frames,
                    'interpretation':'Integrity and measured pixel deltas only. Does not establish absence of flicker or visual artifacts.'})
(ROOT/'docs'/'frame-check.json').write_text(json.dumps(reports,indent=2))
print(json.dumps([{k:v for k,v in r.items() if k!='all_deltas'} for r in reports],indent=2))
