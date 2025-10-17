from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# 1. Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("./models/sarcasm-detection")
model = AutoModelForSequenceClassification.from_pretrained("./models/sarcasm-detection")

# 2. Define your input text
text = "Oh great, another meeting that could’ve been an email."

# 3. Tokenize the input text
inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

# 4. Run the model (get logits)
with torch.no_grad():
    outputs = model(**inputs)

# 5. Convert logits to probabilities
logits = outputs.logits
probs = torch.nn.functional.softmax(logits, dim=-1)

# 6. Get predicted label
predicted_class_id = torch.argmax(probs, dim=-1).item()

# 7. Get labels (if available)
labels = model.config.id2label  # e.g., {0: 'not_sarcastic', 1: 'sarcastic'}

print("Text:", text)
print("Predicted label:", labels[predicted_class_id])
print("Probabilities:", probs)
