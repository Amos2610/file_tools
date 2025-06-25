#!/usr/bin/env python3
"""
Batch-convert MP4 (or any video) files to WAV using ffmpeg.

Usage:
    python mp4_to_wav.py file1.mp4 file2.mp4 ... [-o OUTPUT_DIR] [--rate 44100] [--mono]
"""
import argparse
import pathlib
from concurrent.futures import ThreadPoolExecutor

import ffmpeg
from tqdm import tqdm


def convert_one(src: pathlib.Path, dst_dir: pathlib.Path, rate: int, channels: int):
    dst = dst_dir / src.with_suffix(".wav").name
    (
        ffmpeg
        .input(str(src))
        .output(
            str(dst),
            format="wav",
            acodec="pcm_s16le",
            ar=rate,
            ac=channels,
            vn=None  # drop video
        )
        .overwrite_output()
        .run(quiet=True)  # suppress ffmpeg console spam
    )
    return dst


def main():
    p = argparse.ArgumentParser(description="Convert MP4 to WAV via ffmpeg.")
    p.add_argument("inputs", nargs="+", type=pathlib.Path, help="Video files (*.mp4, *.mov, …)")
    p.add_argument("-o", "--output", type=pathlib.Path, default=".", help="Output directory")
    p.add_argument("--rate", type=int, default=44100, help="Sampling rate (Hz), default 44100")
    p.add_argument("--mono", action="store_true", help="Force mono (1-channel) output")
    args = p.parse_args()

    out_dir = args.output.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    ch = 1 if args.mono else 2

    # Convert in parallel
    with ThreadPoolExecutor() as pool:
        futures = [
            pool.submit(convert_one, src.resolve(), out_dir, args.rate, ch)
            for src in args.inputs
        ]
        for f in tqdm(futures, desc="Converting", unit="file"):
            try:
                dst = f.result()
                tqdm.write(f"✓ {dst.name}")
            except ffmpeg.Error as e:
                tqdm.write(f"✗ {e.stderr.decode()}")
                continue


if __name__ == "__main__":
    main()
