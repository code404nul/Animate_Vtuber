import threading
import time
from model_viewer import main, Live2DViewer, viewer

# Lancer le viewer dans un thread
t = threading.Thread(target=main, daemon=True)
t.start()

# Attendre que le viewer soit initialisé
time.sleep(5)  # Ajuster le temps si nécessaire
# Maintenant tu peux interagir avec l'instance réelle
Live2DViewer.process_external_text(viewer, "i hate you")
