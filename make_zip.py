"""Erstellt eine installierbare .zip aus dem fs25_halle_generator/-Ordner.

Nach dem Build kann die .zip über:
    Blender > Edit > Preferences > Add-ons > Install...
ausgewählt werden.

Usage:
    python make_zip.py

Output:
    fs25_halle_generator-{version}.zip
"""
import os
import re
import sys
import zipfile
import pathlib

HERE = pathlib.Path(__file__).parent
PKG = HERE / "fs25_halle_generator"


def read_version():
    init = (PKG / "__init__.py").read_text(encoding='utf-8')
    m = re.search(r'"version":\s*\((\d+),\s*(\d+),\s*(\d+)\)', init)
    if not m:
        return "unknown"
    return f"{m.group(1)}.{m.group(2)}.{m.group(3)}"


def main():
    if not PKG.is_dir():
        print(f"FAIL: package folder not found: {PKG}")
        sys.exit(1)

    version = read_version()
    out = HERE / f"fs25_halle_generator-{version}.zip"
    if out.exists():
        out.unlink()

    file_count = 0
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PKG):
            # Skip __pycache__
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for fname in files:
                if fname.endswith('.pyc'):
                    continue
                full = pathlib.Path(root) / fname
                rel = full.relative_to(HERE)
                zf.write(full, rel.as_posix())
                file_count += 1

    print(f"Created: {out}")
    print(f"  {file_count} files, {out.stat().st_size / 1024:.1f} KB")
    print(f"  Version: {version}")
    print()
    print("Install:")
    print("  Blender > Edit > Preferences > Add-ons > Install...")
    print(f"  Pick: {out.name}")


if __name__ == "__main__":
    main()
