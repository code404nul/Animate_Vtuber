---

# 🧠 H.A.AI.E — Help Against Anxiety (Experimental)

### Local Emotional Companion — Private • Lightweight • Humanized

---

## 🌱 Overview

**H.A.AI.E** is an experimental AI companion designed to help people overcome social anxiety and loneliness — locally, without internet access, and without monetizing personal data.

It’s *not* meant to replace human interaction, but to help users **relearn communication and emotional expression** in a safe, private, and non-commercial way.

---

## 🎯 Goals

* 🗣️ **Conversational companion**: Interact naturally with emotion-based feedback.
* 🔒 **Privacy first**: Everything runs **locally** (no cloud, no data collection).
* 🧍‍♀️ **Humanized interface**: Live2D-based Vtuber for visual expression.
* 🧩 **Lightweight and accessible**: Optimized for low-resource systems.
* 🧘‍♂️ **Emotional support**: Non-judgmental presence to help practice communication.

---

## ⚙️ Current Development Status

✅ Facial and expression reactions based on text
⚙️ Live2D model integrated
❌ No voice or LLM integration yet
🚧 `main.py` is the current entry point for testing

---

## 🧩 Model Dependencies

To run **H.A.AI.E**, you’ll need to download or clone the following models:

### 🗣️ Text-to-Speech

```
OuteTTS-0.2-500M
```

### 💬 Emotion Detection

```
ModernBERT-large-go-emotions
multilingual_go_emotions_V1.2
```

### 😏 Sarcasm & Irony Detection

```
sarcasm-detection-RoBERTa-base-CR
twitter-roberta-base-irony
```

### 🧍‍♀️ Speech Model (French Example)

```
fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx
fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx.json
```

These include:

* `MODEL_CARD`
* Example voice samples (`speaker_0.mp3`, `speaker_1.mp3`)

---

## 🧰 Installation & Run

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/HAAIE.git
cd HAAIE
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the test script

```bash
python test.py
```

---

## 🧠 Architecture Summary

**Pipeline:**

1. User input → Emotion detection
2. Emotion classification → Expression control
3. Live2D animation → Visual feedback
4. (Planned) Speech-to-text + LLM → Intelligent reply
5. (Planned) TTS → Voice output
---

## 🚀 Roadmap

| Feature            | Status         | Notes                             |
| ------------------ | -------------- | --------------------------------- |
| Expression mapping | ✅ Done        | Based on sentence analysis        |
| Live2D integration | ✅ Done        | Animated avatar                   |
| Voice output       | ✅ Done        | Local TTS via Piper               |
| Offline LLM        | 🔜 Planned     | Compact conversational model      |
| Emotion dataset    | 🧩 In progress | Based on Reddit/Discord data      |
| Code optimization  | 🚧 Planned     | Improve modularity and efficiency |

---

## 💡 Philosophy

> “Your loneliness is not a product.”

H.A.AI.E is open-source and built for **mental health awareness**, **privacy**, and **social reconnection**, not profit.

---

## 🧑‍💻 Author

Independent developer — France
Contact: perso[aroba]archibarbu[dot]com

---

#### Please check license before use it in commercial project.