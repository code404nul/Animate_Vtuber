"""
Module VTuber ultra-simple.
Usage:
    import vtuber
    vtuber.init()
    vtuber.send_text("hello")
"""
from utils.model_viewer import main, Live2DViewer
from utils.toxic_eval import MultilingualToxicityEvaluator
from utils import split_sentence
from long_term_memory.memory_manager import *

import threading

_initialized = False
_viewer_thread = None

_toxicity_evaluator = MultilingualToxicityEvaluator(model_type="multilingual")

def init(model_name: str = "mao", timeout: float = 15.0):
    """
    Initialiser le VTuber en arrière-plan.
    
    Args:
        model_name: Nom du modèle à charger
        timeout: Temps d'attente maximum (secondes)
    """
    global _initialized, _viewer_thread, _model_tts
    
    
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
        return False
    
    try:
        _toxicity_evaluator.filter_toxic_content(texts)
        
        if _toxicity_evaluator.filter_toxic_content(texts)["toxic"]:
            print("[VTuber] Texte détecté comme toxique. Abandon.")
            return False
        else:
            for text in split_sentence(texts): 
                Live2DViewer.send_text(text)
                add_new_memory(text)
            return True
    except:
        return False


def is_ready() -> bool:
    """Vérifier si le VTuber est prêt."""
    return _initialized