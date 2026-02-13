from fastapi import FastAPI
import uvicorn
from news import fetch_news
from ai import generate_script_and_scenes
from media import generate_voice, generate_images, generate_ai_videos
from video import create_video
from utils import ensure_directories, check_ffmpeg

app = FastAPI()

@app.post("/generate-video")
def generate_video(category: str):
    ensure_directories()
    check_ffmpeg()

    # 1. Fetch news
    news_text = fetch_news(category)

    # 2. Generate script and scene descriptions
    ai_output = generate_script_and_scenes(news_text)
    script = ai_output["script"]
    scenes = ai_output["scenes"]

    # 3. Generate audio voiceover
    audio_path = generate_voice(script)

    # 4. Generate visual images for scenes
    image_paths = generate_images(scenes)

    # 5. Generate AI video clips from images (Sora 2)
    video_clips = generate_ai_videos(image_paths, scenes)

    # 6. Create final video by concatenating clips and adding audio
    # Fallback to images if Sora failed to generate any clips
    if video_clips:
        video_path = create_video(video_clips, audio_path)
    else:
        # If Sora failed, we might need a fallback or return error
        # For now, let's assume we return success with what we have or handle it
        return {"status": "error", "message": "Failed to generate AI video clips"}

    return {
        "status": "success",
        "video_path": video_path,
        "audio_path": audio_path,
        "scenes_used": len(scenes),
        "clips_generated": len(video_clips),
        "script": script
    }

if __name__ == "__main__":
    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
