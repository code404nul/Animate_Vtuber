"""
Exemple d'utilisation du VTuber - Ultra simple.
"""

import vtuber
import time

vtuber.init()


vtuber.send_text("i love you")
start = time.time()
vtuber.send_text("i hate you")
print(f"Temps écoulé: {time.time() - start:.2f} secondes")

# IMPORTANT
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nBye!")