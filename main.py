import vtuber
import time
from speech.STT import transcription_loop
import threading


vtuber.init()

print("[MAIN] Vtuber lancé.")


def handle_transcription(text):
    "callback pour gérer la transcription reçue"
    
    is_success = vtuber.send_text(text)

    print(f"[MAIN] Transcription received : {text[15:]}... !")
    if not is_success:
        handle_transcription(text)

thread = threading.Thread(
    target=transcription_loop,
    args=(10, handle_transcription),
    daemon=True
)
thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\\nArrêt du VTuber...")