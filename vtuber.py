"""
Module VTuber ultra-simple.
Usage:
    import vtuber
    vtuber.init()
    vtuber.send_text("hello")
"""

import threading
from model_viewer import main, Live2DViewer
from utils import split_sentence

_initialized = False
_viewer_thread = None


def init(model_name: str = "mao", timeout: float = 15.0):
    """
    Initialiser le VTuber en arrière-plan.
    
    Args:
        model_name: Nom du modèle à charger
        timeout: Temps d'attente maximum (secondes)
    """
    global _initialized, _viewer_thread
    
    if _initialized:
        print("[VTuber] Déjà initialisé")
        return
    
    print(f"[VTuber] Démarrage...")
    
    # Lancer le viewer en thread daemon
    _viewer_thread = threading.Thread(target=main, daemon=True)
    _viewer_thread.start()
    
    # Attendre qu'il soit prêt
    viewer = Live2DViewer.wait_for_instance(timeout=timeout)
    
    if viewer:
        _initialized = True
        print(f"[VTuber] ✓ Prêt!")
    else:
        print(f"[VTuber] ✗ Échec de l'initialisation")


def send_text(texts: str):
    """
    Envoyer un texte au VTuber.
    
    Args:
        text: Texte pour l'analyse émotionnelle
    """
    if not _initialized:
        print("[VTuber] Erreur: Appelez vtuber.init() d'abord!")
        return
    
    for text in split_sentence(texts): Live2DViewer.send_text(text)


def is_ready() -> bool:
    """Vérifier si le VTuber est prêt."""
    return _initialized