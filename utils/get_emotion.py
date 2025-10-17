import torch
from transformers import pipeline
from utils.get_feeling import predict_with_detection as emotion_analyzer
from random import choice
import time

if torch.cuda.is_available():
    device = 0  # Premier GPU
    device_name = torch.cuda.get_device_name(0)
    print(f"GPU detecter : {device_name}")
    print(f"    - CUDA: {torch.cuda.is_available()}")
    print(f"    - Vram : {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} Go\n")
else:
    device = -1
    print("⚠️ Aucun GPU détecté, exécution sur CPU.\n")

POST_IRONY = {
    'joy': -0.7,  # L'ironie inverse souvent la joie
    'excitement': -0.5,  # L'excitation ironique est atténuée
    'approval': -0.8,  # L'approbation ironique signifie souvent le contraire
    'gratitude': -0.9,  # "Merci beaucoup!" ironique = pas vraiment reconnaissant
    'admiration': -0.8,  # L'admiration ironique = critique
    'realization': 1.2,  # L'ironie peut amplifier la prise de conscience
    'relief': -0.6,  # Le soulagement ironique = anxiété
    'desire': 0.3,  # Moins affecté par l'ironie
    'sadness': 1.5,  # L'ironie peut masquer ou amplifier la tristesse
    'curiosity': 0.8,  # Peu affectée
    'optimism': -0.9,  # L'optimisme ironique = pessimisme
    'neutral': 1.0,  # Pas d'effet
    'amusement': 1.3,  # L'ironie augmente l'amusement
    'anger': 1.4,  # L'ironie peut masquer la colère
    'annoyance': 1.5,  # Souvent exprimé avec ironie
    'caring': -0.7,  # "Je m'en soucie tellement..." ironique
    'confusion': 0.9,  # Peu affectée
    'disappointment': 1.6,  # Souvent exprimée ironiquement
    'disapproval': 1.4,  # Amplifiée par l'ironie
    'disgust': 1.3,  # Renforcé par l'ironie
    'embarrassment': 0.7,  # Peut être masqué
    'fear': 0.8,  # Rarement ironique
    'grief': 0.5,  # Rarement exprimé avec ironie
    'love': -0.8,  # "Je t'aime" ironique = le contraire
    'nervousness': 0.9,  # Peu affectée
    'pride': -0.6,  # La fierté ironique = auto-dérision
    'remorse': 0.4,  # Rarement ironique
    'surprise': 1.1   # "Quelle surprise!" peut être ironique
}


print("⏳ Chargement des modèles...\n")
t0 = time.time()

irony_detector_1 = pipeline(
    "text-classification",
    model="./models/twitter-roberta-base-irony",
    top_k=None,
    device=device
)

irony_detector_2 = pipeline(
    "text-classification",
    model="./models/sarcasm-detection-RoBERTa-base-CR",
    top_k=None,
    device=device
)

if device >= 0:
    print("[INFO] Passage des modèles en FP16 (half precision) pour accélérer l'inférence. Verfier compatibilité GPU si erreur.")
    irony_detector_1.model.half()
    irony_detector_2.model.half()


print("WARM UP des modeles...")
_ = irony_detector_1("Warm up test")
_ = irony_detector_2("Warm up test")

print(f"cook en {time.time() - t0:.1f} secondes.\n")



def get_irony_score(detector, results):
    """Extrait le score d'ironie d'un détecteur."""
    for result in results:
        label = result["label"].lower()
        if ("irony" in label and "non" not in label) or \
           "sarcasm" in label or label == "label_1":
            return result["score"]
    return 0.0


def analyse_texte(texte: str, seuil_ironie: float = 0.5, mode: str = "strict"):
    """
    Analyse le texte pour détecter les émotions et l'ironie avec deux modèles.
    Args:
        texte: Le texte à analyser
        seuil_ironie: Seuil de détection d'ironie
        mode: "strict", "moyenne", ou "union"
    """
    emotion_scores = emotion_analyzer(texte)
    emotion_dict = emotion_scores["all_probabilities"]

    irony_results_1 = irony_detector_1(texte)[0]
    irony_results_2 = irony_detector_2(texte)[0]
    
    irony_score_1 = get_irony_score(irony_detector_1, irony_results_1)
    irony_score_2 = get_irony_score(irony_detector_2, irony_results_2)

    sarcasm_markers = [
        "oh", "yeah", "sure", "great", "wonderful", "perfect", "amazing", 
        "brilliant", "fantastic", "...", "really", "totally", "absolutely",
        "of course", "obviously"
    ]
    
    has_sarcasm_marker = any(marker in texte.lower() for marker in sarcasm_markers)
    high_joy = emotion_dict.get("joy", 0) > 0.7
    short_text = len(texte.split()) < 12
    
    if high_joy and not has_sarcasm_marker and short_text:
        irony_score_1 *= 0.3
        irony_score_2 *= 0.3
    
    if mode == "strict":
        is_irony = (irony_score_1 > seuil_ironie) and (irony_score_2 > seuil_ironie)
        irony_score = min(irony_score_1, irony_score_2)
    elif mode == "moyenne":
        irony_score = (irony_score_1 + irony_score_2) / 2
        is_irony = irony_score > seuil_ironie
    elif mode == "union":
        is_irony = (irony_score_1 > seuil_ironie) or (irony_score_2 > seuil_ironie)
        irony_score = max(irony_score_1, irony_score_2)
    else:
        raise ValueError(f"Mode inconnu: {mode}")
    
    if is_irony:
        adjusted_emotions = {
            emotion: score * POST_IRONY.get(emotion, 1.0)
            for emotion, score in emotion_dict.items()
        }
        total = sum(adjusted_emotions.values())
        if total > 0:
            emotion_dict = {k: v / total for k, v in adjusted_emotions.items()}
    
    print(f"\n{'='*60}")
    print(f"Texte: {texte}")
    print(f"{'='*60}")
    print(f"Détection ironie (mode: {mode}):")
    print(f"  - Modèle 1 (CardiffNLP): {irony_score_1:.4f}")
    print(f"  - Modèle 2 (jkhan447):   {irony_score_2:.4f}")
    print(f"  - Score final:           {irony_score:.4f}")
    print(f"  - Ironie détectée:       {'OUI ✓' if is_irony else 'NON ✗'}")
    print(f"\nÉmotions {'(ajustées pour ironie)' if is_irony else ''}:")
    
    sorted_emotions = sorted(emotion_dict.items(), key=lambda x: x[1], reverse=True)
    for emotion, score in sorted_emotions:
        bar = "█" * int(score * 50)
        print(f"  {emotion:10s} {score:.4f} {bar}")
    
    return emotion_dict


def corresp_emotion(text):
    """Retourne l’expression la plus proche de l’émotion dominante."""
    emotions = analyse_texte(text)
    max_emotion = max(emotions, key=emotions.get)
    expression = {
    'approval': 'happy/IDLE',
    'neutral': 'happy/IDLE1',
    'realization': 'surpirse/embarrased',
    'optimism': 'impressed',
    'admiration': 'impressed',
    'pride': 'impressed',
    'relief': 'happy/IDLE',
    'curiosity': 'surpirse/embarrased',
    'joy': 'happy/IDLE',
    'amusement': 'happy/IDLE',
    'annoyance': 'angry',
    'desire': 'blush',
    'excitement': 'impressed',
    'remorse': 'sad',
    'surprise': 'surpirse/embarrased',
    'anger': 'angry',
    'caring': 'blush',
    'confusion': 'surpirse/embarrased',
    'disappointment': 'sad',
    'disapproval': 'angry',
    'disgust': 'angry',
    'embarrassment': 'blush',
    'fear': 'surpirse/embarrased',
    'gratitude': 'impressed',
    'grief': 'sad',
    'love': 'blush',
    'nervousness': 'surpirse/embarrased',
    'sadness': 'sad'
    }[max_emotion]
    
    return choice(expression) if isinstance(expression, list) else expression


if __name__ == "__main__":
    print(analyse_texte("I love to have meeting at 3am", mode="moyenne"))
