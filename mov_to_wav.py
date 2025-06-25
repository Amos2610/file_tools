#!/usr/bin/env python3
"""
Batch-convert MOV (or any video) files to WAV via FFmpeg.

Usage:
    python mov_to_wav.py clip1.mov clip2.mov ...                 \
           [-o OUTPUT_DIR] [--rate 44100] [--mono]

Options:
    -o, --output   Output directory (default: current directory)
    --rate         Output sample-rate in Hz (default: 44100)
    --mono         Force mono (1-channel) output

You can still pass MP4 / M4V / MKV …; FFmpeg handles them transparently.
"""
import argparse
import pathlib
from concurrent.futures import ThreadPoolExecutor

import ffmpeg
from tqdm import tqdm


def convert_one(src: pathlib.Path, dst_dir: pathlib.Path,
                rate: int, channels: int) -> pathlib.Path:
    """Convert one video file to WAV and return destination path."""
    dst = dst_dir / src.with_suffix(".wav").name
    (
        ffmpeg
        .input(str(src))
        .output(
            str(dst),
            format="wav",
            acodec="pcm_s16le",       # raw 16-bit PCM
            ar=rate,                  # sample-rate
            ac=channels,              # channels
            vn=None                   # drop video stream
        )
        .overwrite_output()
        .run(quiet=True)              # suppress FFmpeg spam
    )
    return dst


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Convert MOV (or any video) files to WAV."
    )
    ap.add_argument(
        "inputs",
        nargs="+",
        type=pathlib.Path,
        help="Video files (*.mov, *.mp4, *.mkv, …)",
    )
    ap.add_argument(
        "-o", "--output",
        type=pathlib.Path,
        default=".",
        help="Output directory",
    )
    ap.add_argument(
        "--rate",
        type=int,
        default=44100,
        help="Sampling rate (Hz)",
    )
    ap.add_argument(
        "--mono",
        action="store_true",
        help="Force mono (1-channel) output",
    )
    args = ap.parse_args()

    out_dir = args.output.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    channels = 1 if args.mono else 2

    with ThreadPoolExecutor() as pool:
        futures = [
            pool.submit(
                convert_one,
                src.resolve(),
                out_dir,
                args.rate,
                channels,
            )
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
