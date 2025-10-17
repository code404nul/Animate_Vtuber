import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained('./models/ModernBERT-large-go-emotions')
model = AutoModelForSequenceClassification.from_pretrained('./models/ModernBERT-large-go-emotions')

best_thresholds = [0.5510204081632653, 0.26530612244897955, 0.14285714285714285, 0.12244897959183673, 0.44897959183673464, 0.22448979591836732, 0.2040816326530612, 0.4081632653061224, 0.5306122448979591, 0.22448979591836732, 0.2857142857142857, 0.3061224489795918, 0.2040816326530612, 0.14285714285714285, 0.1020408163265306, 0.4693877551020408, 0.24489795918367346, 0.3061224489795918, 0.2040816326530612, 0.36734693877551017, 0.2857142857142857, 0.04081632653061224, 0.3061224489795918, 0.16326530612244897, 0.26530612244897955, 0.32653061224489793, 0.12244897959183673, 0.2040816326530612]

LABELS = ['admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring', 'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval', 'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief', 'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization', 'relief', 'remorse', 'sadness', 'surprise', 'neutral']

ID2LABEL = dict(enumerate(LABELS))

def detect_emotions(text):
    inputs = tokenizer(text, truncation=True, add_special_tokens=True, max_length=128, return_tensors='pt')
    with torch.no_grad():
        logits = model(**inputs).logits
    probas = torch.sigmoid(logits).squeeze(dim=0)
    class_binary_labels = (probas > torch.tensor(best_thresholds)).int()
    return [ID2LABEL[label_id] for label_id, value in enumerate(class_binary_labels) if value == 1]

def predict(text):
    inputs = tokenizer(text, truncation=True, add_special_tokens=True, max_length=128, return_tensors='pt')
    with torch.no_grad():
        logits = model(**inputs).logits
    probas = torch.sigmoid(logits).squeeze(dim=0).tolist()
    probas = [round(proba, 3) for proba in probas]
    labels2probas = dict(zip(LABELS, probas))
    probas_dict_sorted = dict(sorted(labels2probas.items(), key=lambda x: x[1], reverse=True))
    return probas_dict_sorted

def predict_with_detection(text):
    """
    Combine la détection d'émotions (avec seuils) et les probabilités détaillées.
    
    Returns:
        dict: {
            'detected_emotions': list des émotions détectées (au-dessus du seuil),
            'all_probabilities': dict de toutes les probabilités (triées),
            'detected_details': dict des émotions détectées avec leurs probabilités et seuils
        }
    """
    inputs = tokenizer(text, truncation=True, add_special_tokens=True, max_length=128, return_tensors='pt')
    with torch.no_grad():
        logits = model(**inputs).logits
    
    probas = torch.sigmoid(logits).squeeze(dim=0)
    probas_list = probas.tolist()
    probas_rounded = [round(proba, 3) for proba in probas_list]
    
    # Toutes les probabilités
    labels2probas = dict(zip(LABELS, probas_rounded))
    all_probas_sorted = dict(sorted(labels2probas.items(), key=lambda x: x[1], reverse=True))
    
    # Émotions détectées avec seuils
    class_binary_labels = (probas > torch.tensor(best_thresholds)).int()
    detected_emotions = [ID2LABEL[label_id] for label_id, value in enumerate(class_binary_labels) if value == 1]
    
    # Détails des émotions détectées
    detected_details = {}
    for label_id, value in enumerate(class_binary_labels):
        if value == 1:
            emotion = ID2LABEL[label_id]
            detected_details[emotion] = {
                'probability': probas_rounded[label_id],
                'threshold': round(best_thresholds[label_id], 3),
                'above_threshold': probas_rounded[label_id] > best_thresholds[label_id]
            }
    
    # Trier detected_details par probabilité
    detected_details = dict(sorted(detected_details.items(), key=lambda x: x[1]['probability'], reverse=True))
    
    return {
        'detected_emotions': detected_emotions,
        'all_probabilities': all_probas_sorted,
        'detected_details': detected_details
    }


if __name__ == "__main__":
    print("=" * 80)
    text1 = 'I am so happy to see that the meeting is at 3 am.'
    result1 = predict_with_detection(text1)
    print(result1)

