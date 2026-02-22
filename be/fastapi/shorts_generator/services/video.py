import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

def wrap_text_for_image(text: str, font: ImageFont, max_width: int) -> str:
    """
    Wraps text to fit within the specified width in pixels.

    :param text: The input text to wrap
    :param font: The font used for rendering the text
    :param max_width: The maximum width in pixels for each line
    :return: The wrapped text with line breaks
    """
    lines = []
    words = text.split(" ")
    current_line = ""

    for word in words:
        # Check the width of the current line with the new word
        test_line = f"{current_line} {word}".strip()
        text_width = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), test_line, font=font)[2]

        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)

def overlay_image_and_text(
    background_path, overlay_path, output_path, text, title
):
    """
    Creates a composite image with a background, overlay image, and text.
    :param background_path: Path to the background image
    :param overlay_path: Path to the overlay image
    :param output_path: Path to save the resulting image
    :param text: Text to display
    :param title: 윗부분에 들어갈 제목
    """
    try:
        # Load the background and overlay images
        background = Image.open(background_path).resize((720, 1280)).convert("RGBA")
        overlay = Image.open(overlay_path).resize((600, 600)).convert("RGBA")

        # Create a drawing object
        draw = ImageDraw.Draw(background)

        # Load font
        title_font = ImageFont.truetype("resource/anemone.ttf", 55)
        text_font = ImageFont.truetype("resource/anemone.ttf", 48)
        max_width = background.width - 40  # 20 pixels padding on each side

        # Add the title at the top, left-aligned with some padding
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (background.width - title_width) // 2
        title_y = 155
        draw.text((title_x, title_y), title, font=title_font, fill="black")

        # Wrap the text to fit the image
        wrapped_text = wrap_text_for_image(text, text_font, max_width)

        # Calculate text dimensions
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=text_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Center text horizontally and vertically
        text_x = (background.width - text_width) // 2
        text_y = 300

        # Add wrapped text
        draw.multiline_text((text_x, text_y), wrapped_text, font=text_font, fill="black", align="center")

        # Add overlay image in the center
        overlay_x = (background.width - overlay.width) // 2  # Center horizontally
        overlay_y = text_y + text_height + 75  # Vertical position for the image
        background.paste(overlay, (overlay_x, overlay_y), overlay)

        # Save the final image
        background.save(output_path)
        print(f"Image saved to {output_path}")
    except Exception as e:
        print(f"Error creating layout: {e}")


def get_audio_duration(audio_path):
    """
    Gets the duration of an audio file using FFmpeg.
    """
    try:
        command = [
            "ffprobe",
            "-i", audio_path,
            "-show_entries", "format=duration",
            "-v", "quiet",
            "-of", "csv=p=0"
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return 0

def create_video_from_image_and_audio(image_path, audio_path, output_path, shorten_by):
    """
    Combines an image and an audio file to create a video using FFmpeg.
    The video duration is explicitly set to the audio duration.
    """
    duration = get_audio_duration(audio_path)
    if duration == 0:
        print("Error: Could not determine audio duration.")
        return None

    adjusted_duration = max(0, duration - shorten_by)

    try:
        command = [
            "ffmpeg",
            "-loop", "1",  # 반복 이미지를 활성화
            "-i", image_path,  # 입력 이미지
            "-i", audio_path,  # 입력 오디오
            "-c:v", "libx264",  # 비디오 코덱 설정
            "-c:a", "aac",  # 오디오 코덱 설정
            "-b:a", "192k",  # 오디오 비트레이트
            "-pix_fmt", "yuv420p",  # 비디오 픽셀 포맷 설정
            "-t", str(adjusted_duration),  # 비디오 길이를 오디오 길이로 제한
            output_path
        ]
        subprocess.run(command, check=True)
        return output_path
    except Exception as e:
        print(f"Error creating video: {e}")
        return None

def merge_videos(video_files, output_path, temp_dir):
    """
    Merges multiple video files into a single video and creates file_list.txt in the temporary directory.

    :param video_files: List of video file paths to merge
    :param output_path: Path to save the merged video
    :param temp_dir: Temporary directory where file_list.txt will be created
    """
    file_list_path = os.path.join(temp_dir, "file_list.txt")
    try:
        # Create a temporary file list for FFmpeg
        with open(file_list_path, "w") as file_list:
            for video_file in video_files:
                file_list.write(f"file '{os.path.abspath(video_file)}'\n")

        # FFmpeg command to concatenate videos
        command = [
            "ffmpeg",
            "-f", "concat",  # Concatenate mode
            "-safe", "0",    # Allow unsafe file paths
            "-i", file_list_path,  # Input file list
            "-c", "copy",    # Copy codec (no re-encoding)
            output_path
        ]

        # Run the FFmpeg command
        subprocess.run(command, check=True)
        print(f"Videos merged successfully into {output_path}")

    except Exception as e:
        print(f"Error merging videos: {e}")
    finally:
        # Delete the temporary file list
        if os.path.exists(file_list_path):
            os.remove(file_list_path)
            print(f"Temporary file {file_list_path} deleted.")