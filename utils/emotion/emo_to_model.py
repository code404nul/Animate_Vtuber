from utils.manage_model import ModelManager
from utils.emotion.get_emotion import corresp_emotion
model = "mao"

def init(model_name, text):
    global model
    model = ModelManager(model_name)
    return corresp_emotion(model.expressions, text)

def get_expression():
    global model
    if model is None:
        raise ValueError("Model not initialized. Call init() first.")
    return [exp["Name"] for exp in model.expressions]