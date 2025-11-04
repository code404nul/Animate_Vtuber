import whisper
import sounddevice as sd
import numpy as np
from time import time
import threading
from queue import Queue
from utils.config_manager import size_stt, device

# Chargement du modèle une seule fois (optimisation)
model = None
model_lock = threading.Lock()

def load_model():
    """Charge le modèle Whisper une seule fois (thread-safe)"""
    global model
    with model_lock:
        if model is None:
            print("🔄 Chargement du modèle Whisper...")
            model = whisper.load_model(size_stt(), device=device())
            print("✓ Modèle chargé")
    return model

def record_audio(duration=30, sample_rate=16000):
    """
    Enregistre l'audio depuis le microphone
    Args:
        duration: durée d'enregistrement en secondes
        sample_rate: fréquence d'échantillonnage (16kHz recommandé pour Whisper)
    """
    print(f"🎤 Enregistrement en cours ({duration}s)...")
    audio = sd.rec(int(duration * sample_rate), 
                   samplerate=sample_rate, 
                   channels=1, 
                   dtype='float32')
    sd.wait()  # Attend la fin de l'enregistrement
    print("✓ Enregistrement terminé")
    return audio.flatten()

def recording_worker(audio_queue, duration, stop_event):
    """
    Thread worker pour l'enregistrement continu
    Args:
        audio_queue: file d'attente pour stocker les audios enregistrés
        duration: durée de chaque enregistrement
        stop_event: événement pour arrêter le thread proprement
    """
    while not stop_event.is_set():
        try:
            audio = record_audio(duration=duration)
            audio_queue.put(audio)
        except Exception as e:
            print(f"❌ Erreur lors de l'enregistrement : {e}")
            if not stop_event.is_set():
                continue

def transcription_worker(audio_queue, stop_event):
    """
    Thread worker pour la transcription
    Args:
        audio_queue: file d'attente contenant les audios à transcrire
        stop_event: événement pour arrêter le thread proprement
    """
    mdl = load_model()
    
    while not stop_event.is_set() or not audio_queue.empty():
        try:
            # Attend un audio avec timeout pour vérifier stop_event régulièrement
            audio = audio_queue.get(timeout=1)
            
            print("🔄 Transcription en cours...")
            start = time()
            result = mdl.transcribe(audio, fp16=False)
            end = time()
            
            print(f"⏱️  Temps de transcription : {end - start:.2f} secondes")
            print(f"📝 Transcription : {result['text']}\n")
            
            audio_queue.task_done()
        except Exception as e:
            if "Empty" not in str(type(e).__name__):  # Ignore les timeouts de queue vide
                print(f"❌ Erreur pendant la transcription : {e}")

def transcription_loop(interval=30):
    """
    Boucle de transcription continue avec enregistrement et analyse en parallèle
    Args:
        interval: durée d'enregistrement (en secondes)
    """
    audio_queue = Queue(maxsize=3)  # Limite à 3 audios en attente max
    stop_event = threading.Event()
    
    # Créer les threads
    recorder_thread = threading.Thread(
        target=recording_worker,
        args=(audio_queue, interval, stop_event),
        daemon=True
    )
    transcriber_thread = threading.Thread(
        target=transcription_worker,
        args=(audio_queue, stop_event),
        daemon=True
    )
    
    print("🚀 Démarrage de la transcription continue...")
    print("   (Appuyez sur Ctrl+C pour arrêter)\n")
    
    # Démarrer les threads
    recorder_thread.start()
    transcriber_thread.start()
    
    try:
        # Attendre indéfiniment (les threads tournent en arrière-plan)
        while True:
            recorder_thread.join(timeout=1)
            if not recorder_thread.is_alive():
                break
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de la transcription...")
        stop_event.set()
        
        # Attendre que les threads se terminent proprement
        recorder_thread.join(timeout=5)
        transcriber_thread.join(timeout=10)
        
        print("✓ Arrêt terminé")

def transcribe_audio(duration=30):
    """
    Enregistre et transcrit l'audio du microphone (mode simple, non-continu)
    Args:
        duration: durée d'enregistrement en secondes
    """
    # Enregistrer depuis le micro
    audio = record_audio(duration=duration)
    
    # Charger le modèle
    mdl = load_model()
    
    # Transcrire
    start = time()
    result = mdl.transcribe(audio, fp16=False)
    end = time()
    
    print(f"⏱️  Temps de transcription : {end - start:.2f} secondes")
    print(f"📝 Transcription : {result['text']}\n")
    
    return result["text"]

if __name__ == "__main__":
    # Mode continu avec enregistrement et transcription en parallèle
    transcription_loop(interval=30)