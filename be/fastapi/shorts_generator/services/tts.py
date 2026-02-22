import os
import edge_tts

# Generate TTS for a given sentence
async def generate_tts(sentence: str, output_path: str):
    """
    Generate TTS for a given sentence and save to the specified output path.

    :param sentence: The text to convert to speech
    :param output_path: The full path where the TTS file will be saved
    :return: The output file path or an error message
    """
    try:
        communicator = edge_tts.Communicate(
            text=sentence, 
            voice="ko-KR-SunHiNeural",
            rate="+20%"
        )
        await communicator.save(output_path)
        return output_path
    except Exception as e:
        return f"Error generating TTS: {e}"

# Generate TTS files for a given sentence in the user's temp directory
async def generate_tts_files(sentence: str, index: int, output_dir: str):
    """
    Generate TTS file for a given sentence and save in the specified directory.

    :param sentence: The text to convert to speech
    :param index: The index of the sentence (for file naming)
    :param output_dir: The directory where the TTS file will be saved
    :return: The output file path
    """
    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate file name and full path
    file_name = f"sentence_{index + 1}.mp3"
    output_path = os.path.join(output_dir, file_name)
    
    # Generate the TTS file
    return await generate_tts(sentence, output_path)