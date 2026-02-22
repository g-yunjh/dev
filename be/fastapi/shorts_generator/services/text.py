import re

# the function takes a script and splits it into sentences
def split_script_into_sentences(script: str):
    sentences = re.split(r"(?<=[.!?~。！？])[\"'”’]*\s*", script.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]