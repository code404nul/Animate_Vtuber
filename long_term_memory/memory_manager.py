import json
from os.path import dirname, join, exists
from datetime import datetime
from utils.get_emotion import higgest_emotion, index_emotionnal_charge

BASE_DIR = dirname(__file__)
MEMORY_PATH = join(BASE_DIR, "memory.json")

def add_new_memory(input_text: str):
    if not exists(MEMORY_PATH):
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    new_index = max((entry["index"] for entry in data), default=0) + 1

    emotion_result = higgest_emotion(input_text)
    new_entry = {
        "output": input_text,
        "registration_time": datetime.timestamp(datetime.now()),
        "emotion": emotion_result,
        "IEC": index_emotionnal_charge(emotion_result),
        "repition" : 1,
        "index": new_index
    }

    data.append(new_entry)

    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("✅ Nouvelle entrée ajoutée avec succès !")

def repetition_add(index):
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    found = False
    for entry in data:
        if entry["index"] == index:
            entry["repition"] = entry.get("repition", 0) + 1
            found = True
            break

    if not found:
        print(f"❌ Aucune entrée avec l'index {index} n'a été trouvée.")
        return

    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_label(index, label):

    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data:
        if entry["index"] == index:
            return entry.get(label, 0)
        
    return ""
        
def get_index():
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return len(data)

def get_index_by_output(output_text: str):
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data:
        if entry["output"] == output_text:
            return entry["index"]
