import whisper
import sounddevice as sd
import numpy as np
import tempfile

def record_audio(duration=5, samplerate=16000):
    print("🎤 Говорите...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    audio = np.squeeze(audio)
    return audio, samplerate

def transcribe_whisper(duration=5, model_name="base", language="ru"):
    audio, samplerate = record_audio(duration, samplerate=16000)

    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        import soundfile as sf
        sf.write(f.name, audio, samplerate)
        model = whisper.load_model(model_name)
        result = model.transcribe(f.name, language=language)
        text = result["text"]

    return text.strip()
