#!/usr/bin/env python3
"""
Create a zip archive of this plugin folder while excluding the following items:
  - .git directory
  - .gitignore file
  - confg.py and config.py
  - this script itself (build_zip.py)

Usage:
  python build_zip.py [output.zip]

If output is omitted, creates route_planner_plugin.zip in the plugin folder.
"""

from pathlib import Path
import os
import sys
import zipfile

ROOT = Path(__file__).resolve().parent


def make_zip(output_path: Path):
    excludes = {'.gitignore', 'confg.py', 'config.py', Path(__file__).name}
    skip_dirs = {'.git', '.idea', '.venv', '__pycache__'}

    output_path = Path(output_path).resolve()
    if output_path.exists():
        output_path.unlink()

    with zipfile.ZipFile(str(output_path), 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            for d in list(dirnames):
                if d in skip_dirs:
                    dirnames.remove(d)

            dirpath = Path(dirpath)
            for fname in filenames:
                if fname in excludes:
                    continue

                # skip zip files
                if fname.lower().endswith('.zip'):
                    continue

                full = dirpath / fname
                if full.resolve() == output_path.resolve():
                    continue

                rel = full.relative_to(ROOT)
                # Place all files under top-level folder 'route_planner' in the ZIP
                arcname = Path('route_planner') / rel
                zf.write(str(full), arcname=arcname.as_posix())

    print(f'Created ZIP: {output_path}')


def read_version_from_metadata(metadata_path: Path) -> str:
    text = metadata_path.read_text(encoding='utf-8')

    for line in text.splitlines():
        line = line.strip()

        if line.startswith('version='):
            return line.split('=', 1)[1].strip()

    return ''

if __name__ == '__main__':
    metadata_file = ROOT / 'metadata.txt'
    version = read_version_from_metadata(metadata_file)

    if not version:
        print('Error: Could not read version from metadata.txt. Aborting.')
        sys.exit(1)

    safe_version = ''.join(c for c in version if c.isalnum() or c in ('.', '-', '_'))
    out = ROOT / f'route_planner_v{safe_version}.zip'

    make_zip(out)
