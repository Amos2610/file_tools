#!/usr/bin/env python3
"""
Plot waveform & spectrogram of an audio file.
Usage:
    python visualize_audio.py input.wav [-o OUT_DIR]
"""
import argparse, pathlib, numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

def plot_waveform(y, sr, out):
    t = np.arange(len(y)) / sr
    plt.figure()
    plt.plot(t, y)
    plt.title("Waveform")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.savefig(out / "waveform.png", dpi=200)

def plot_spectrogram(y, sr, out):
    plt.figure()
    plt.specgram(y, NFFT=1024, Fs=sr, noverlap=512)
    plt.title("Spectrogram")
    plt.xlabel("Time [s]")
    plt.ylabel("Frequency [Hz]")
    plt.tight_layout()
    plt.savefig(out / "spectrogram.png", dpi=200)

def main():
    ap = argparse.ArgumentParser(description="Audio visualiser")
    ap.add_argument("audio", type=pathlib.Path, help="Input WAV/FLAC/OGG …")
    ap.add_argument("-o", "--out", type=pathlib.Path, default=".", help="Output dir")
    args = ap.parse_args()

    out_dir = args.out.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    y, sr = sf.read(args.audio)               # y: numpy array, sr: sample-rate
    if y.ndim > 1:                            # stereo → mono (average L/R)
        y = y.mean(axis=1)

    plot_waveform(y, sr, out_dir)
    plot_spectrogram(y, sr, out_dir)

    print(f"  ✓ waveform.png\n  ✓ spectrogram.png  →  saved in {out_dir}")

if __name__ == "__main__":
    main()
