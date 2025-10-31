import vtuber
import time


vtuber.init()
time.sleep(2)


vtuber.send_text("Oups, j'ai laisser le bébé dans le micro onde ! UWU")
time.sleep(3)
vtuber.send_text("Oups, j'ai laisser le bébé dans le micro onde !")

print("VTuber actif - Appuyez sur Ctrl+C pour quitter")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\\nArrêt du VTuber...")