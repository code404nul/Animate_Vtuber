"""
Exemple d'utilisation du VTuber - Ultra simple.
"""

import vtuber
import time

vtuber.init()


vtuber.send_text("I hate you. But i love you!!! Do you know that yesturday i get it by a car? Seriously can you imagine that??? Mo one have mercy in this world.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nBye!")