"""Create a Direct Upload archive containing only the public static web root."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)
files = sorted(p for p in WEB.rglob('*') if p.is_file())
assert len(files) <= 1000
assert all(not p.is_symlink() and not any(s.startswith('.') for s in p.relative_to(WEB).parts) for p in files)
assert all(p.stat().st_size < 25 * 1024 * 1024 for p in files)
archive = OUT / 'moc-coffee-demo.zip'
with ZipFile(archive, 'w', ZIP_DEFLATED) as bundle:
    for path in files:
        bundle.write(path, path.relative_to(WEB))
report = {'archive': str(archive), 'files': len(files), 'bytes': archive.stat().st_size,
          'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}
(OUT / 'release.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
