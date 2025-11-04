import whisper
import torch
from time import time

# Vérifie si CUDA est dispo
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"✅ Appareil utilisé : {device}")

# Charge le modèle sur le bon appareil
model = whisper.load_model("medium", device=device)

start = time()
result = model.transcribe("output.wav")
end = time()

print("\n🗣️ Transcription :")
print(result["text"])
print(f"\n⏱️ Temps de transcription : {end - start:.2f} secondes")
