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

    output_path = Path(output_path).resolve()
    if output_path.exists():
        output_path.unlink()

    with zipfile.ZipFile(str(output_path), 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            # Skip .git directory entirely
            if '.git' in dirnames:
                dirnames.remove('.git')

            dirpath = Path(dirpath)
            for fname in filenames:
                if fname in excludes:
                    continue

                full = dirpath / fname
                # Do not include the output zip if it is created inside the repo
                try:
                    if full.resolve() == output_path.resolve():
                        continue
                except Exception:
                    pass

                rel = full.relative_to(ROOT)
                # Use posix-style path inside the ZIP
                zf.write(str(full), arcname=rel.as_posix())

    print(f'Created ZIP: {output_path}')


if __name__ == '__main__':
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'route_planner_plugin_v1.0.zip'
    make_zip(out)
