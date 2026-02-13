import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

print(f"Using API Key starting with: {api_key[:10]}...")

try:
    print("Testing Sora 2 availability...")
    if hasattr(client, 'videos'):
        print(f"Signature of client.videos.create: {inspect.signature(client.videos.create)}")
        # Inspect the Video class directly from the openai types
        try:
            from openai.types.video import Video
            print("\nAttributes of Video class (from openai.types.video):")
            print([a for a in dir(Video) if not a.startswith('_')])
        except Exception as e:
            print(f"Error importing Video class: {e}")

except Exception as e:
    print(f"Test failed: {e}")
