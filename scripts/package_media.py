"""Encode all 288 frames per view; reject incomplete render sequences."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'web' / 'media'
STOPS = (1, 97, 193, 288)

def run(args):
    subprocess.run([str(a) for a in args], check=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--posters-only', action='store_true')
    p.add_argument('--render-root', type=Path, default=ROOT / 'renders')
    p.add_argument('--media-subdir', default='')
    p.add_argument('--posters-from-frames', action='store_true')
    args = p.parse_args()
    output_dir = OUT / args.media_subdir
    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which('ffmpeg')
    ffprobe = shutil.which('ffprobe')
    reports = []
    for view in ('desktop', 'mobile'):
        for i, frame in enumerate(STOPS, 1):
            source = args.render_root / f'{"frames" if args.posters_from_frames else "proof"}-{view}' / f'{frame:04}.png'
            run(['convert', source, '-quality', '86', output_dir / f'{view}-{i:02}.webp'])
        if args.posters_only:
            continue
        frames = args.render_root / f'frames-{view}'
        missing = [i for i in range(1, 289) if not (frames / f'{i:04}.png').exists()]
        if missing:
            raise SystemExit(f'{view}: missing {len(missing)} frames; first={missing[0]}')
        output = output_dir / f'journey-{view}.mp4'
        run([ffmpeg, '-y', '-loglevel', 'warning', '-framerate', '24', '-start_number', '1',
             '-i', frames / '%04d.png', '-frames:v', '288', '-c:v', 'libx264', '-preset', 'medium',
             '-crf', '20', '-pix_fmt', 'yuv420p', '-g', '6', '-keyint_min', '6', '-sc_threshold', '0',
             '-movflags', '+faststart', '-an', output])
        probe = json.loads(subprocess.check_output([ffprobe, '-v', 'error', '-show_streams',
                                                  '-show_format', '-of', 'json', str(output)]))
        stream = probe['streams'][0]
        assert int(stream['nb_frames']) == 288
        assert abs(float(probe['format']['duration']) - 12) < .05
        reports.append(dict(view=view, bytes=output.stat().st_size, probe=probe))
    if reports:
        report_path = (args.render_root if args.media_subdir else ROOT / 'docs') / 'media-report.json'
        report_path.write_text(json.dumps(reports, indent=2))

if __name__ == '__main__':
    main()
