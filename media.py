import uuid
import os
import time
import base64
import requests
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from config import OPENAI_API_KEY, ELEVENLABS_API_KEY

client_ai = OpenAI(api_key=OPENAI_API_KEY)
client_voice = ElevenLabs(api_key=ELEVENLABS_API_KEY)

VOICE_ID = "SAz9YHcvj6GT2YYXdXww"  # River
MODEL_ID = "eleven_flash_v2"

# -------------------------
# AUDIO
# -------------------------
def generate_voice(script: str) -> str:
    os.makedirs("output/audio", exist_ok=True)
    path = f"output/audio/{uuid.uuid4()}.mp3"

    audio_stream = client_voice.text_to_speech.convert(
        text=script,
        voice_id=VOICE_ID,
        model_id=MODEL_ID
    )

    with open(path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)

    return path

# -------------------------
# IMAGES (SCENE BASED)
# -------------------------
def generate_images(scene_prompts: list) -> list:
    os.makedirs("output/images", exist_ok=True)
    image_paths = []

    for scene in scene_prompts:
        prompt = scene["image_prompt"]
        image_path = f"output/images/{uuid.uuid4()}.png"

        try:
            image = client_ai.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1536"  # Max vertical supported by DALL-E
            )

            image_base64 = image.data[0].b64_json
            image_data = base64.b64decode(image_base64)
            
            # Resize image to match Sora requirements (720x1280)
            try:
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(image_data))
                # Resize with LANCZOS for quality
                img_resized = img.resize((720, 1280), Image.Resampling.LANCZOS)
                img_resized.save(image_path)
                print(f"DEBUG: Resized {image_path} to 720x1280")
            except Exception as e:
                print(f"WARNING: Pillow resize failed, saving original: {e}")
                with open(image_path, "wb") as f:
                    f.write(image_data)

            image_paths.append(image_path)
        except Exception as e:
            if "moderation_blocked" in str(e):
                print(f"CRITICAL: Scene {scene['scene']} blocked by moderation: {prompt}")
            else:
                print(f"ERROR generating image for scene {scene['scene']}: {e}")
            continue

    return image_paths

# -------------------------
# AI VIDEOS (SORA)
# -------------------------
def generate_ai_videos(image_paths: list, scene_prompts: list) -> list:
    """Generates short AI video clips from images using OpenAI Sora."""
    os.makedirs("output/videos/clips", exist_ok=True)
    video_paths = []

    for img_path, scene in zip(image_paths, scene_prompts):
        prompt = scene["image_prompt"]
        video_clip_path = f"output/videos/clips/{uuid.uuid4()}.mp4"

        try:
            print(f"DEBUG: Starting Sora generation for {img_path} with prompt: {prompt[:50]}...")
            # Initiate Sora 2 video generation (Image-to-Video)
            with open(img_path, "rb") as image_file:
                # The dir(client.videos) showed 'create' is a direct method
                # Signature check showed 'input_reference' is the correct param for iamge
                # Explicitly set size to match the image resolution
                generation = client_ai.videos.create(
                    model="sora-2",
                    prompt=prompt,
                    input_reference=image_file,
                    size="720x1280"
                )
            
            job_id = generation.id
            print(f"DEBUG: Sora job created. ID: {job_id}")

            # Polling for completion
            retry_count = 0
            while True:
                # The dir(client.videos) showed 'retrieve' is a direct method
                status_update = client_ai.videos.retrieve(job_id)
                print(f"DEBUG: Job {job_id} status: {status_update.status}")
                
                if status_update.status == "completed":
                    video_url = status_update.video.url
                    print(f"DEBUG: Video ready at {video_url}")
                    video_response = requests.get(video_url)
                    with open(video_clip_path, "wb") as f:
                        f.write(video_response.content)
                    video_paths.append(video_clip_path)
                    break
                elif status_update.status in ["failed", "cancelled"]:
                    error_msg = getattr(status_update, 'error', 'Unknown error')
                    print(f"ERROR: Sora generation {status_update.status} for job {job_id}: {error_msg}")
                    break
                
                retry_count += 1
                if retry_count > 60: # 10 minutes timeout
                    print(f"ERROR: Sora job {job_id} timed out.")
                    break

                time.sleep(10)

        except Exception as e:
            import traceback
            print(f"EXCEPTION in generate_ai_videos: {e}")
            traceback.print_exc()
            continue

    return video_paths
