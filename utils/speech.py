
from kokoro import KPipeline
import soundfile as sf
import streamlit as st
import re
from time import sleep, time

pipeline = KPipeline(lang_code='a')

def text_to_speech(text, data_path='.'):
    """
    Convert text to speech using the specified voice and save audio files.
    """
    generator = pipeline(text, voice=st.session_state['voice'])
    for i, (gs, ps, audio) in enumerate(generator):
        audio_file = f'{data_path}/{i}.wav'
        sf.write(audio_file, audio, 24000)
        st.audio(audio_file, format="audio/wav")
        

def stream_text_and_speech_generator(text_generator):
    """
    Stream text and speech generation, updating the UI with the generated text
    and playing audio as it becomes available.
    """
    full_text, current_text, count = "", "", 0
    audio_start_time, duration_seconds = -1, -1
    audio_container = st.empty()

    with st.empty():        
        for chunk in text_generator:
            count += 1
            token = chunk['response']
            full_text += token
            current_text += token
            st.write(full_text)
            if (token in ('.', '!', '?', '\n') and count > 10) or chunk['done']:
                speech_text = cleanup_prompt(current_text.strip())
                generator = pipeline(speech_text, voice=st.session_state['voice'])
                for i, (_, _, audio) in enumerate(generator):
                    audio_path = f'./{i}.wav'
                    sf.write(audio_path, audio, 24000)
                    # wait for the audio to finish playing
                    if (audio_start_time > 0 and duration_seconds > 0) and (time() - audio_start_time < duration_seconds):
                        sleep(duration_seconds - (time() - audio_start_time))
                    audio_container.audio(audio_path, format="audio/wav", autoplay=True)
                    duration_seconds = len(audio) / 24000
                    audio_start_time = time()
                current_text = ""
    cleanup_audio_files()


def cleanup_audio_files():
    """
    Clean up audio files in the specified directory.
    """
    import os
    for file in os.listdir('.'):
        if file.endswith('.wav'):
            os.remove(os.path.join('.', file))


def cleanup_prompt(text):
    """
    Clean up the prompt by removing unnecessary whitespace and newlines.
    """
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002700-\U000027BF"  # Dingbats
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U00002600-\U000026FF"  # Misc symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U000025A0-\U000025FF"  # Geometric Shapes
        "]+", 
        flags=re.UNICODE
    )
    text = emoji_pattern.sub(r'', text)
    text.replace('*', '')
    return text