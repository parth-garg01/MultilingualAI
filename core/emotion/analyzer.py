"""
LinguaFlow — Emotion & Sentiment Analyzer
Combines text-based sentiment analysis (multilingual BERT) with
audio feature extraction (pitch, energy, speech rate) for
comprehensive emotion detection.
"""

import logging
import numpy as np
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class EmotionAnalyzer:
    """
    Multi-modal emotion analyzer combining text sentiment
    and audio prosodic features for holistic emotion detection.
    """

    # Star rating → emotion mapping
    EMOTION_MAP = {
        1: {
            "label": "Very Negative",
            "emoji": "😠",
            "color": "#ff4444",
            "description": "Angry / Very Upset",
        },
        2: {
            "label": "Negative",
            "emoji": "😟",
            "color": "#ff8844",
            "description": "Sad / Concerned",
        },
        3: {
            "label": "Neutral",
            "emoji": "😐",
            "color": "#9090b0",
            "description": "Neutral / Calm",
        },
        4: {
            "label": "Positive",
            "emoji": "🙂",
            "color": "#44cc88",
            "description": "Happy / Pleased",
        },
        5: {
            "label": "Very Positive",
            "emoji": "😊",
            "color": "#00e676",
            "description": "Excited / Very Happy",
        },
    }

    # Audio-based emotion heuristics
    AUDIO_EMOTION_THRESHOLDS = {
        "high_energy_high_pitch": {
            "label": "Excited",
            "emoji": "🤩",
            "color": "#ffaa00",
        },
        "high_energy_low_pitch": {
            "label": "Angry",
            "emoji": "😠",
            "color": "#ff4444",
        },
        "low_energy_high_pitch": {
            "label": "Anxious",
            "emoji": "😰",
            "color": "#ff8844",
        },
        "low_energy_low_pitch": {
            "label": "Sad",
            "emoji": "😢",
            "color": "#4488ff",
        },
    }

    def __init__(self):
        self.text_analyzer = None
        self._loaded = False

        logger.info("Emotion Analyzer initialized")

    def load_model(self, callback: Optional[Callable] = None):
        """Load the sentiment analysis model."""
        try:
            from transformers import pipeline

            if callback:
                callback("Loading emotion analysis model...")

            logger.info("Loading multilingual sentiment model...")

            self.text_analyzer = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                device=-1,  # CPU (sentiment is fast enough on CPU)
            )
            self._loaded = True

            if callback:
                callback("Emotion analysis model loaded!")
            logger.info("Sentiment model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            if callback:
                callback(f"Error loading emotion model: {e}")
            raise

    def analyze_text(self, text: str) -> dict:
        """
        Analyze text sentiment using multilingual BERT.

        Args:
            text: Input text (supports English, Hindi, Tamil).

        Returns:
            dict with label, emoji, color, score, stars, description.
        """
        if not text or not text.strip():
            return self._neutral_result()

        if not self._loaded:
            logger.warning("Sentiment model not loaded, returning neutral.")
            return self._neutral_result()

        try:
            # Truncate to model's max length
            truncated = text[:512]
            result = self.text_analyzer(truncated)[0]

            # Parse star rating (e.g., "3 stars" → 3)
            stars = int(result["label"].split()[0])
            emotion = self.EMOTION_MAP[stars]

            return {
                "label": emotion["label"],
                "emoji": emotion["emoji"],
                "color": emotion["color"],
                "description": emotion["description"],
                "score": round(result["score"], 3),
                "stars": stars,
            }

        except Exception as e:
            logger.error(f"Text sentiment analysis failed: {e}")
            return self._neutral_result()

    def analyze_audio(self, audio_data: np.ndarray, sr: int = 16000) -> dict:
        """
        Analyze audio features for emotion cues.

        Extracts pitch, energy, speech rate, and spectral features
        to infer emotional state from vocal prosody.

        Args:
            audio_data: NumPy array of audio samples (float32).
            sr: Sample rate (default 16000).

        Returns:
            dict with audio feature values and inferred emotion.
        """
        try:
            import librosa

            # Ensure float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # Flatten to mono if needed
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)

            # --- Feature Extraction ---

            # 1. Pitch (F0) analysis
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr)
            pitch_values = pitches[pitches > 0]

            avg_pitch = float(np.mean(pitch_values)) if len(pitch_values) > 0 else 0.0
            pitch_std = float(np.std(pitch_values)) if len(pitch_values) > 0 else 0.0
            max_pitch = float(np.max(pitch_values)) if len(pitch_values) > 0 else 0.0
            min_pitch = (
                float(np.min(pitch_values)) if len(pitch_values) > 0 else 0.0
            )
            pitch_range = max_pitch - min_pitch

            # 2. Energy (RMS)
            rms = librosa.feature.rms(y=audio_data)[0]
            avg_energy = float(np.mean(rms))
            max_energy = float(np.max(rms))
            energy_std = float(np.std(rms))

            # 3. Speech rate (onset detection)
            onset_env = librosa.onset.onset_strength(y=audio_data, sr=sr)
            onsets = librosa.onset.onset_detect(
                onset_envelope=onset_env, sr=sr, backtrack=False
            )
            duration_sec = len(audio_data) / sr
            speech_rate = (
                len(onsets) / duration_sec if duration_sec > 0 else 0
            )

            # 4. Spectral features
            spectral_centroid = float(
                np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr))
            )
            zcr = float(
                np.mean(librosa.feature.zero_crossing_rate(y=audio_data))
            )

            # --- Emotion Inference from Audio ---
            # Simple heuristic-based classification
            is_high_energy = avg_energy > 0.05
            is_high_pitch = avg_pitch > 200  # Hz

            if is_high_energy and is_high_pitch:
                audio_emotion = self.AUDIO_EMOTION_THRESHOLDS[
                    "high_energy_high_pitch"
                ]
            elif is_high_energy and not is_high_pitch:
                audio_emotion = self.AUDIO_EMOTION_THRESHOLDS[
                    "high_energy_low_pitch"
                ]
            elif not is_high_energy and is_high_pitch:
                audio_emotion = self.AUDIO_EMOTION_THRESHOLDS[
                    "low_energy_high_pitch"
                ]
            else:
                audio_emotion = self.AUDIO_EMOTION_THRESHOLDS[
                    "low_energy_low_pitch"
                ]

            return {
                # Raw features
                "avg_pitch": round(avg_pitch, 2),
                "pitch_std": round(pitch_std, 2),
                "pitch_range": round(pitch_range, 2),
                "avg_energy": round(avg_energy, 4),
                "max_energy": round(max_energy, 4),
                "energy_std": round(energy_std, 4),
                "speech_rate": round(speech_rate, 2),
                "spectral_centroid": round(spectral_centroid, 2),
                "zero_crossing_rate": round(zcr, 4),
                "duration_sec": round(duration_sec, 2),
                # Inferred emotion
                "audio_emotion": audio_emotion["label"],
                "audio_emoji": audio_emotion["emoji"],
                "audio_color": audio_emotion["color"],
            }

        except Exception as e:
            logger.error(f"Audio emotion analysis failed: {e}")
            return {
                "avg_pitch": 0.0,
                "pitch_std": 0.0,
                "pitch_range": 0.0,
                "avg_energy": 0.0,
                "max_energy": 0.0,
                "energy_std": 0.0,
                "speech_rate": 0.0,
                "spectral_centroid": 0.0,
                "zero_crossing_rate": 0.0,
                "duration_sec": 0.0,
                "audio_emotion": "Neutral",
                "audio_emoji": "😐",
                "audio_color": "#9090b0",
            }

    def analyze_combined(
        self, text: str, audio_data: np.ndarray, sr: int = 16000
    ) -> dict:
        """
        Perform combined text + audio emotion analysis.

        Returns a unified emotion result that considers both
        the semantic content and the vocal delivery.
        """
        text_result = self.analyze_text(text)
        audio_result = self.analyze_audio(audio_data, sr)

        # Combine: text sentiment is primary, audio is secondary/modifier
        combined = {
            "text_emotion": text_result,
            "audio_features": audio_result,
            # Primary emotion from text
            "primary_label": text_result["label"],
            "primary_emoji": text_result["emoji"],
            "primary_color": text_result["color"],
            # Audio modifier
            "audio_modifier": audio_result["audio_emotion"],
        }

        # If text is neutral but audio shows strong emotion, use audio
        if text_result["stars"] == 3 and audio_result["avg_energy"] > 0.05:
            combined["primary_label"] = audio_result["audio_emotion"]
            combined["primary_emoji"] = audio_result["audio_emoji"]
            combined["primary_color"] = audio_result["audio_color"]

        return combined

    def _neutral_result(self) -> dict:
        """Return a neutral emotion result."""
        neutral = self.EMOTION_MAP[3]
        return {
            "label": neutral["label"],
            "emoji": neutral["emoji"],
            "color": neutral["color"],
            "description": neutral["description"],
            "score": 0.5,
            "stars": 3,
        }

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def unload(self):
        """Free model from memory."""
        if self.text_analyzer is not None:
            del self.text_analyzer
            self.text_analyzer = None
            self._loaded = False
            logger.info("Emotion model unloaded")
