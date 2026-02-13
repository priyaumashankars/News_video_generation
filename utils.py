import os
import subprocess

def ensure_directories():
    os.makedirs("output/images", exist_ok=True)
    os.makedirs("output/audio", exist_ok=True)
    os.makedirs("output/videos", exist_ok=True)

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        raise RuntimeError("FFmpeg is not installed")
