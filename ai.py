from openai import OpenAI
from config import OPENAI_API_KEY
import json

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_script_and_scenes(news_text: str) -> dict:
    prompt = f"""
You are creating a short news video.

From the news below:
1. Write a short narration (max 60 seconds)
2. Split it into 6 visual scenes
3. For each scene, generate a realistic image description. 
   - IMPORTANT: Keep descriptions safe, neutral, and professional. 
   - Avoid generating specific real people, gore, violence, or controversial political symbolism to ensure they pass safety filters.
   - Focus on cinematic, high-quality environmental scenes or generic professional settings.

Return STRICT JSON in this format:
{{
  "script": "full narration text",
  "scenes": [
    {{ "scene": 1, "image_prompt": "..." }},
    {{ "scene": 2, "image_prompt": "..." }},
    {{ "scene": 3, "image_prompt": "..." }},
    {{ "scene": 4, "image_prompt": "..." }},
    {{ "scene": 5, "image_prompt": "..." }},
    {{ "scene": 6, "image_prompt": "..." }}
  ]
}}

News:
{news_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return json.loads(response.choices[0].message.content)
