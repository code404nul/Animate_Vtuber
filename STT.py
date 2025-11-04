import whisper
from time import time
from utils.config_manager import size_stt, device

model = whisper.load_model(size_stt(), device=device())

start = time()
result = model.transcribe("output.wav")
end = time()

print("\n🗣️ Transcription :")
print(result["text"])
print(f"\n⏱️ Temps de transcription : {end - start:.2f} secondes")
