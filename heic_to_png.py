#!/usr/bin/env python3
"""
Convert HEIC images to PNG.

Usage:
    python heic2png.py input1.heic input2.heic ... [-o OUTPUT_DIR]
"""

import argparse
import pathlib
from PIL import Image
import pillow_heif


def heic_to_png(src_path: pathlib.Path, out_dir: pathlib.Path) -> pathlib.Path:
    """Convert a single HEIC file to PNG and return the output path."""
    heif = pillow_heif.read_heif(src_path)
    img = Image.frombytes(
        heif.mode,
        heif.size,
        heif.data,
        "raw",
    )

    out_path = out_dir / src_path.with_suffix(".png").name
    img.save(out_path, format="PNG")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Convert HEIC to PNG.")
    parser.add_argument(
        "inputs",
        nargs="+",
        type=pathlib.Path,
        help="One or more .heic files (wildcards OK, e.g. *.heic)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        default=".",
        help="Output directory (default: current directory)",
    )
    args = parser.parse_args()

    out_dir = args.output.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for src in args.inputs:
        for file in src.glob("*.heic") if src.is_dir() else [src]:
            try:
                out_path = heic_to_png(file.resolve(), out_dir)
                print(f"✓ {file.name}  →  {out_path.relative_to(pathlib.Path.cwd())}")
            except Exception as e:
                print(f"✗ {file}: {e}")


if __name__ == "__main__":
    main()

