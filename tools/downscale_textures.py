"""Downscale all PBR textures in a folder to a target max dimension.

Usage:
    python tools/downscale_textures.py <folder> [target_size]

Default target is 2048 (2K). Files larger than that on the long edge are
resized; smaller files are left alone. Aspect ratio is preserved. Output
overwrites the input by default.

Recommended sizes for FS25 buildings:
    2K (2048) - default, plenty for hall walls
    1K (1024) - small details, distant LODs
    4K (4096) - hero closeups only

Example:
    python tools/downscale_textures.py D:/cl/fs25_halle_addon/fs25_textures
    python tools/downscale_textures.py D:/cl/fs25_halle_addon/fs25_textures 1024
"""
import os
import sys
from PIL import Image

EXTS = {'.png', '.jpg', '.jpeg', '.tga', '.tif', '.tiff', '.bmp'}


def downscale(folder, target_max=2048, out_folder=None, dry_run=False):
    if not os.path.isdir(folder):
        print(f"FAIL: not a directory: {folder}")
        return

    out_folder = out_folder or folder
    if out_folder != folder and not os.path.isdir(out_folder):
        os.makedirs(out_folder, exist_ok=True)

    total_before = 0
    total_after = 0
    files_changed = 0

    for fname in sorted(os.listdir(folder)):
        ext = os.path.splitext(fname)[1].lower()
        if ext not in EXTS:
            continue

        in_path = os.path.join(folder, fname)
        out_path = os.path.join(out_folder, fname)

        size_before = os.path.getsize(in_path)
        total_before += size_before

        try:
            img = Image.open(in_path)
        except Exception as e:
            print(f"  SKIP {fname}: {e}")
            continue

        w, h = img.size
        long_side = max(w, h)
        if long_side <= target_max:
            print(f"  KEEP {fname}: {w}x{h} (already <= {target_max})")
            total_after += size_before
            continue

        scale = target_max / long_side
        new_w = int(w * scale)
        new_h = int(h * scale)

        if dry_run:
            print(f"  WOULD {fname}: {w}x{h} -> {new_w}x{new_h}")
            continue

        # Resize with high-quality LANCZOS
        resized = img.resize((new_w, new_h), Image.LANCZOS)

        # Save with reasonable quality settings
        if ext in {'.jpg', '.jpeg'}:
            resized.save(out_path, format='JPEG', quality=92, optimize=True)
        elif ext == '.png':
            resized.save(out_path, format='PNG', optimize=True)
        else:
            resized.save(out_path)

        size_after = os.path.getsize(out_path)
        total_after += size_after

        delta_mb = (size_before - size_after) / 1024 / 1024
        print(f"  RESIZE {fname}: {w}x{h} -> {new_w}x{new_h}  "
              f"({size_before/1024/1024:.1f}MB -> {size_after/1024/1024:.1f}MB, "
              f"saved {delta_mb:.1f}MB)")
        files_changed += 1

    print(f"\nTotal: {total_before/1024/1024:.1f}MB -> {total_after/1024/1024:.1f}MB "
          f"({files_changed} files resized)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    folder = sys.argv[1]
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 2048
    print(f"Downscaling textures in {folder} to max {target}x{target}\n")
    downscale(folder, target_max=target)


if __name__ == "__main__":
    main()
