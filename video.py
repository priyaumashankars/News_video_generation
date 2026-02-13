import uuid
import subprocess
import os

def get_audio_duration(audio_path: str) -> float:
    """Gets the duration of an audio file using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())

def create_video(video_paths: list, audio_path: str) -> str:
    """Concatenates video clips and overlays audio."""
    os.makedirs("output/videos", exist_ok=True)
    output_path = f"output/videos/{uuid.uuid4()}.mp4"

    # Create FFmpeg concat file for videos
    file_list = "output/videos/clips.txt"
    with open(file_list, "w") as f:
        for vid in video_paths:
            f.write(f"file '{os.path.abspath(vid)}'\n")

    cmd = [
        "ffmpeg", "-y",

        # Videos
        "-f", "concat",
        "-safe", "0",
        "-i", file_list,

        # Audio
        "-i", audio_path,

        # 🔥 FORCE STREAM MAPPING
        "-map", "0:v:0",
        "-map", "1:a:0",

        # Video settings (Ensure consistent format)
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1080:1920",

        # 🔥 AUDIO SETTINGS
        "-c:a", "aac",
        "-b:a", "192k",
        "-af", "volume=1.0",

        # Duration - match audio exactly
        "-shortest",

        output_path
    ]

    subprocess.run(cmd, check=True)
    return output_path
