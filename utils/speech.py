
from kokoro import KPipeline
import soundfile as sf
import streamlit as st
from config import VOICE
from time import sleep, time

pipeline = KPipeline(lang_code='a')

def text_to_speech(text, voice=VOICE, data_path='.'):
    """
    Convert text to speech using the specified voice and save audio files.
    """
    generator = pipeline(text, voice=voice)
    for i, (gs, ps, audio) in enumerate(generator):
        audio_file = f'{data_path}/{i}.wav'
        sf.write(audio_file, audio, 24000)
        st.audio(audio_file, format="audio/wav")


def stream_text_and_speech_generator(text_generator, voice=VOICE, data_path='.'):
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

            if token in ('.', '!', '?', '\n') and count > 10:
                generator = pipeline(current_text, voice=voice)
                for i, (_, _, audio) in enumerate(generator):
                    audio_path = f'{data_path}/{i}.wav'
                    sf.write(audio_path, audio, 24000)
                    # wait for the audio to finish playing
                    if (audio_start_time > 0 and duration_seconds > 0) and (time() - audio_start_time < duration_seconds):
                        sleep(duration_seconds - (time() - audio_start_time))
                    audio_container.audio(audio_path, format="audio/wav", autoplay=True)
                    duration_seconds = len(audio) / 24000
                    audio_start_time = time()
                current_text = ""
    cleanup_audio_files(data_path)


def cleanup_audio_files(data_path='.'):
    """
    Clean up audio files in the specified directory.
    """
    import os
    for file in os.listdir(data_path):
        if file.endswith('.wav'):
            os.remove(os.path.join(data_path, file))


    