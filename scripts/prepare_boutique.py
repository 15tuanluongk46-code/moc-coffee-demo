"""Fetch OFL fonts and package original Blender studio renders for the web."""
from pathlib import Path
from urllib.request import urlretrieve
from urllib.parse import quote
import argparse
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def fonts():
    dest = ROOT / 'web/fonts'
    dest.mkdir(parents=True, exist_ok=True)
    files = {
        'BeVietnamPro-Regular.ttf': ('bevietnampro', 'BeVietnamPro-Regular.ttf'),
        'BeVietnamPro-SemiBold.ttf': ('bevietnampro', 'BeVietnamPro-SemiBold.ttf'),
        'Fraunces.ttf': ('fraunces', 'Fraunces[SOFT,WONK,opsz,wght].ttf'),
        'BeVietnamPro-OFL.txt': ('bevietnampro', 'OFL.txt'),
        'Fraunces-OFL.txt': ('fraunces', 'OFL.txt'),
    }
    for name, (family, source) in files.items():
        path = dest / name
        if not path.exists():
            urlretrieve('https://raw.githubusercontent.com/google/fonts/main/ofl/' + family + '/' + quote(source), path)
        print(name, path.stat().st_size)


def images(version=1):
    folder = 'product-v2' if version == 2 else 'product'
    dest = ROOT / 'web/media' / folder
    (dest/'spin').mkdir(parents=True, exist_ok=True)
    source = ROOT/'renders'/folder
    for name in ('hero-desktop', 'hero-mobile', 'macro'):
        with Image.open(source/(name+'.png')) as im:
            im.convert('RGB').save(dest/(name+'.webp'), quality=88, method=6)
    for i in range(24):
        with Image.open(source/'spin'/f'{i:02}.png') as im:
            im.convert('RGB').save(dest/'spin'/f'{i:02}.webp', quality=83, method=6)
    print('Packaged 3 studio images and 24 turntable frames')


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--fonts-only',action='store_true')
    parser.add_argument('--version',type=int,choices=(1,2),default=1)
    args=parser.parse_args();fonts()
    if not args.fonts_only: images(args.version)
