import subprocess

def add_bgm_to_video(video_path, bgm_path, output_path, volume=0.5):
    """
    Adds background music to a video, matching the video's duration.

    :param video_path: Path to the input video file
    :param bgm_path: Path to the background music file
    :param output_path: Path to save the output video with background music
    """
    try:
        command = [
            "ffmpeg",
            "-i", video_path,  # Input video
            "-i", bgm_path,    # Input background music
            "-filter_complex", f"[1:a]volume={volume},aloop=loop=-1:size=2e+09[a1];[0:a][a1]amix=inputs=2:duration=shortest",
            "-c:v", "copy",  # Copy video codec
            "-c:a", "aac",   # Audio codec
            "-b:a", "192k",  # Audio bitrate
            "-shortest",     # Trim to the shortest stream (video length)
            output_path
        ]
        subprocess.run(command, check=True)
        print(f"Video with BGM saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error adding BGM to video: {e}")
        return None