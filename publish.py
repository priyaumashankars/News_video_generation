def post_video(platform, video_path):
    if platform == "instagram":
        return "Posted to Instagram (mock)"
    elif platform == "youtube":
        return "Posted to YouTube (mock)"
    else:
        return "Unsupported platform"
