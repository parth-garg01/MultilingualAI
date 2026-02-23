# 🌐 LinguaFlow

> **Real-Time Multilingual Translation with Emotional Intelligence**

A desktop AI application that provides low-latency speech-to-speech translation for **English**, **Hindi**, and **Tamil** — with a focus on preserving emotional nuance and cultural context.

---

## ✨ Features

- 🎤 **Real-Time Speech Recognition** — Powered by OpenAI Whisper (local, no API key)
- 🌐 **Neural Translation** — Helsinki-NLP MarianMT models for high-quality translation
- 🔊 **Natural Text-to-Speech** — Edge-TTS with emotion-aware prosody
- 🎭 **Emotion Detection** — Combined text sentiment + audio prosody analysis
- 📖 **Idiom Mapping** — Cultural equivalent translation (30+ idioms across 3 languages)
- 🎵 **Live Waveform Visualizer** — Real-time audio visualization
- 💜 **Premium Dark UI** — CustomTkinter-powered desktop app

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- A microphone
- Internet (for first-time model download only)

### Installation

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the app
python main.py
```

> ⚡ First launch will download ML models (~2-3 GB). Subsequent launches are offline.

## 🏗️ Architecture

```
LinguaFlow/
├── core/                    # 🧠 AI Engine (UI-independent)
│   ├── asr/                 # Speech-to-Text (Whisper)
│   ├── translator/          # Translation (MarianMT)
│   ├── tts/                 # Text-to-Speech (Edge-TTS)
│   ├── emotion/             # Sentiment + Audio Analysis
│   ├── idiom_mapper/        # Cultural Idiom Mapping
│   └── pipeline.py          # Full pipeline orchestration
├── ui/                      # 🖥️ Desktop App
│   ├── components/          # UI widgets
│   ├── themes/              # Dark/Light themes
│   └── app.py               # Main application window
├── api/                     # 🌐 Future API server
├── config.py                # Global configuration
└── main.py                  # Entry point
```

## 🤖 AI Models (All Open-Source)

| Component | Model | Runs On |
|-----------|-------|---------|
| ASR | OpenAI Whisper (small) | Local CPU/GPU |
| Translation | Helsinki-NLP MarianMT | Local CPU/GPU |
| TTS | Microsoft Edge-TTS | Streaming |
| Sentiment | Multilingual BERT | Local CPU |

## 📋 Supported Languages

| Language | Dialect | Nuance Focus |
|----------|---------|-------------|
| English | Global / Indian English | Sarcasm & Professionalism |
| Hindi | Modern Urban & Formal | Respect levels (Tu/Tum/Aap) & Idioms |
| Tamil | Colloquial vs. Formal | Cultural metaphors & Phonetics |

## 📄 License

This project is for educational purposes.
