"""Build only the approved page and temporary Pages adapter into a chosen directory."""
from pathlib import Path
import shutil
import sys

root = Path(__file__).resolve().parents[1]
output = Path(sys.argv[1]).expanduser().resolve()
output.mkdir(parents=True, exist_ok=True)
if any(p.name not in {'index.html', '_worker.js'} for p in output.iterdir()):
    raise SystemExit('Use a dedicated output directory containing no other files.')
shutil.copyfile(root / 'index.html', output / 'index.html')
shutil.copyfile(root / 'hosting/worker.mjs', output / '_worker.js')
print(output)
