import os
import requests
from googletrans import Translator

def translate_to_english(text: str) -> str:
    """
    Translates the given text to English using googletrans.

    :param text: The text to translate
    :return: Translated text in English
    """
    try:
        translator = Translator()
        translation = translator.translate(text, src="ko", dest="en")
        return translation.text
    except Exception as e:
        return f"Error translating text: {e}"

def generate_image(prompt: str, index: int, output_dir: str) -> str:
    """
    Generates an AI image using the given prompt (translated to English) and saves it to the specified output directory.

    :param prompt: The prompt to generate the image (in Korean or any language)
    :param index: The index of the image (used for file naming)
    :param output_dir: The directory where the image will be saved
    :return: The path to the saved image or an error message
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Translate the prompt to English
    translated_prompt = translate_to_english(prompt)
    
    # Define the image file path
    output_path = os.path.join(output_dir, f"image_{index + 1}.png")
    url = f"https://image.pollinations.ai/prompt/{translated_prompt}?nologo=true"
    
    try:
        # Fetch the image from the API
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Save the image to the specified directory
        with open(output_path, "wb") as image_file:
            for chunk in response.iter_content(1024):
                image_file.write(chunk)
        
        return output_path
    except Exception as e:
        return f"Error generating image: {e}"