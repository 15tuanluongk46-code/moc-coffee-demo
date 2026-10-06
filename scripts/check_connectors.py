"""Validate every replacement frame and build time-labelled transition evidence."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'renders' / 'no-connectors-v2'
SAMPLES = (1, 38, 53, 70, 97, 134, 149, 166, 193, 229, 245, 261)
reports = []
for view, size in [('desktop', (1280, 800)), ('mobile', (720, 1440))]:
    frames = OUTPUT / f'frames-{view}'
    for frame in range(1, 289):
        path = frames / f'{frame:04}.png'
        with Image.open(path) as image:
            image.load()
            assert image.size == size, (path, image.size)
            assert max(ImageStat.Stat(image.resize((64, 64))).stddev) > 3, path
    sheet = Image.new('RGB', (900, 690), '#eeeae2')
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(SAMPLES):
        with Image.open(frames / f'{frame:04}.png') as image:
            image.thumbnail((225, 200))
            x, y = index % 4 * 225, index // 4 * 230
            sheet.paste(image, (x + (225-image.width)//2, y+23))
            draw.text((x+5, y+4), f'{view} f{frame:03} {(frame-1)/24:.2f}s', fill='#173c32')
    sheet.save(OUTPUT / f'transitions-{view}.jpg', quality=85)
    reports.append(dict(view=view, frames=288, size=size, all_frames_decoded=True))
(OUTPUT/'frame-check.json').write_text(json.dumps(reports, indent=2))
print(json.dumps(reports, indent=2))
