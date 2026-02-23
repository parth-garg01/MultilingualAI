"""
LinguaFlow — Global Configuration
"""

import os
from pathlib import Path

# ============================================================
# Path Configuration
# ============================================================
BASE_DIR = Path(__file__).parent.resolve()
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "ui" / "assets"
TEMP_DIR = BASE_DIR / "temp"

# Ensure directories exist
for d in [MODELS_DIR, DATA_DIR, ASSETS_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ============================================================
# Language Configuration
# ============================================================
LANGUAGES = {
    "English": {
        "code": "en",
        "whisper_code": "en",
        "tts_voice": "en-US-GuyNeural",
        "tts_voice_female": "en-US-JennyNeural",
        "dialect": "Global Standard / Indian English",
        "nuance": "Sarcasm & Professionalism",
        "flag": "🇺🇸",
    },
    "Hindi": {
        "code": "hi",
        "whisper_code": "hi",
        "tts_voice": "hi-IN-MadhurNeural",
        "tts_voice_female": "hi-IN-SwaraNeural",
        "dialect": "Modern Urban & Formal",
        "nuance": "Respect (Tu/Tum/Aap) & Idioms",
        "flag": "🇮🇳",
    },
    "Tamil": {
        "code": "ta",
        "whisper_code": "ta",
        "tts_voice": "ta-IN-ValluvarNeural",
        "tts_voice_female": "ta-IN-PallaviNeural",
        "dialect": "Spoken (Colloquial) vs. Formal",
        "nuance": "Cultural metaphors & Phonetic accuracy",
        "flag": "🇮🇳",
    },
}

# Helper: get language config by code
LANG_BY_CODE = {v["code"]: {**v, "name": k} for k, v in LANGUAGES.items()}

# ============================================================
# Model Configuration
# ============================================================
ASR_MODEL_SIZE = "small"  # Options: tiny, base, small, medium, large

TRANSLATION_MODELS = {
    ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
    ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
    ("en", "ta"): "Helsinki-NLP/opus-mt-en-mul",
    ("ta", "en"): "Helsinki-NLP/opus-mt-mul-en",
    # hi<->ta uses English as pivot (handled in code)
}

SENTIMENT_MODEL = "nlptown/bert-base-multilingual-uncased-sentiment"

# ============================================================
# Audio Configuration
# ============================================================
SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_DTYPE = "float32"
CHUNK_DURATION_SEC = 0.5  # Duration of each audio chunk in seconds
MAX_RECORDING_SEC = 60    # Maximum recording duration
SILENCE_THRESHOLD = 0.01  # Amplitude threshold for silence detection
SILENCE_DURATION_SEC = 2.0  # Seconds of silence before auto-stop

# ============================================================
# Application Configuration
# ============================================================
APP_NAME = "LinguaFlow"
APP_VERSION = "1.0.0"
APP_TAGLINE = "Real-Time Multilingual Translation with Emotional Intelligence"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 820
MIN_WINDOW_WIDTH = 900
MIN_WINDOW_HEIGHT = 650

# ============================================================
# Performance
# ============================================================
TARGET_LATENCY_MS = 1500  # Target max latency in milliseconds
USE_GPU = True            # Use GPU if available (falls back to CPU)
