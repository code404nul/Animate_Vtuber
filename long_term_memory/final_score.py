from long_term_memory.memory_manager import get_index_by_output, get_label
from long_term_memory.FAISS import SemanticSearchEngine
from utils.emotion.get_emotion import higgest_emotion, index_emotionnal_charge

import matplotlib.pyplot as plt
import math

#query = "I'm going to buy some coffee"
#query = "I'm going to kill myself"
#query = "I'm going go hiking"

def similarity_total(query):
    """
    Find similarities in past memory
    input : query
    output : [score, memory (str)]
    """
    engine = SemanticSearchEngine()
    results = engine.search(query, 0)
    iec_query = index_emotionnal_charge(higgest_emotion(query))

    outputs = []
    scores = []

    def final_score(iec_out, faiss_score, iec_query):
        # Produit émotionnel signé
        emotion_similarity = iec_query * iec_out

        # Atténuation progressive si les émotions sont opposées (pas de coupe brutale à 0)
        # → Plus les signes sont opposés, plus la pénalité est forte (mais jamais 100%)
        penalty = 1 - abs(math.tanh(iec_query - iec_out))  # valeur entre 0 (opposés forts) et 1 (mêmes)
        emotion_similarity *= penalty

        # Pondération dynamique : plus l’émotion est forte, plus elle pèse
        weight_emotion = abs(iec_query) ** 5
        weight_faiss = 1 - weight_emotion

        # Score final pondéré
        return weight_emotion * emotion_similarity + weight_faiss * faiss_score

    if results:
        for output_text, faiss_score in results:
            idx = get_index_by_output(output_text)
            iec = get_label(idx, "IEC")
            repetition = get_label(idx, "repetition")
            registration_time = get_label(idx, "registration_time")

            if None in (iec, repetition, registration_time):
                continue

            score = final_score(
                iec_query=iec_query,
                iec_out=iec,
                faiss_score=faiss_score,
            )

            scores.append(score)
            outputs.append(output_text)

            print(f"Memory item:\n"
                f"  FAISS score: {faiss_score:.4f}\n"
                f"  IEC: {iec:.4f}\n"
                f"  Final score: {score:.4f}\n"
                f"  Output: {output_text}\n------\n")
            
        return [scores, outputs]
    else:
        return ""

def show_resut_similarity(outputs, scores, query):
    plt.figure(figsize=(10, 6))
    plt.barh(outputs, scores, color='skyblue')
    plt.xlabel("IEC Adjusted Score")
    plt.title(f"Semantic Matches for Query: \"{query}\"")
    plt.tight_layout()
    plt.show()
