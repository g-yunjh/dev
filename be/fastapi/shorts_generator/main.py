import os
import time
import shutil
from fastapi import FastAPI
from pydantic import BaseModel
from services.text import split_script_into_sentences
from services.tts import generate_tts_files
from services.image import generate_image
from services.video import overlay_image_and_text, create_video_from_image_and_audio, merge_videos
from services.upload import upload_to_google_drive, authenticate_with_drive
from services.bgm import add_bgm_to_video

app = FastAPI()

class ScriptInput(BaseModel):
    user_id: str
    title: str
    script: str

@app.post("/process-script/")
async def process_script(data: ScriptInput):
    # Create a temporary directory for the user
    timestamp = int(time.time())
    temp_dir = os.path.join("output", f"{data.user_id}_{timestamp}")
    os.makedirs(temp_dir, exist_ok=True)
    
    results = []
    video_files = []

    try:
        sentences = split_script_into_sentences(data.script)

        for index, sentence in enumerate(sentences):  
            # 문장별 이미지 생성      
            image_file_path = generate_image(sentence, index, output_dir=temp_dir)
            
            final_image_path = os.path.join(temp_dir, f"layout_{index + 1}.png")
            overlay_image_and_text(
                background_path="resource/background.png",
                overlay_path=image_file_path,
                output_path=final_image_path,
                text=sentence,
                title = data.title
            )
            
            # TTS 파일 생성 & 기존 이미지와 TTS 파일 결합하여 동영상 문장별 동영상 생성
            tts_file_path = await generate_tts_files(sentence, index, output_dir=temp_dir)
            video_file_path = os.path.join(temp_dir, f"video_{index + 1}.mp4")
            create_video_from_image_and_audio(
                final_image_path, 
                tts_file_path, 
                video_file_path,
                shorten_by = 0.2
                )

            video_files.append(video_file_path)

            results.append({
                "original": sentence,
                "tts_file": tts_file_path,
                "image_file": final_image_path,
                "video_file": video_file_path
            })

        final_video_path = os.path.join(temp_dir, "final_video.mp4")
        merge_videos(video_files, final_video_path, temp_dir)

        # 브금 추가
        bgm_path = "resource/bgm.mp3"
        final_video_with_bgm = os.path.join(temp_dir, f"{data.user_id}_{timestamp}.mp4")
        add_bgm_to_video(
            final_video_path, 
            bgm_path, 
            final_video_with_bgm,
            volume = 0.1
            )

        credentials_json = "credentials.json"
        token_file = "token.json"
        drive_service = authenticate_with_drive(credentials_json, token_file)
        drive_file_id = upload_to_google_drive(drive_service, final_video_with_bgm, f"{data.user_id}_{timestamp}.mp4")
        
        return {
            "results": results,
            "final_video": final_video_path,
            "drive_file_id": drive_file_id
            }
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Temporary directory {temp_dir} deleted.")