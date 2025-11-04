import vtuber
import time
from speech.STT import transcription_loop
import threading

vtuber.init()
time.sleep(2)


vtuber.send_text("Oups, j'ai laisser le bébé dans le micro onde ! UWU")
time.sleep(3)
vtuber.send_text("Oups, j'ai laisser le bébé dans le micro onde !")

print("VTuber actif - Appuyez sur Ctrl+C pour quitter")

"""
thread = threading.Thread(target=transcription_loop, args=(30,), daemon=True)
thread.start()
"""

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\\nArrêt du VTuber...")