"""
LinguaFlow — Automatic Speech Recognition Engine
Uses OpenAI's Whisper model for multilingual speech-to-text.
Runs 100% locally, no API key required.
"""

import logging
import numpy as np
import torch
from pathlib import Path
from typing import Optional, Callable, Union

logger = logging.getLogger(__name__)


class ASREngine:
    """
    Automatic Speech Recognition engine powered by OpenAI Whisper.
    Supports English, Hindi, and Tamil with high accuracy.
    """

    SUPPORTED_LANGUAGES = {"en", "hi", "ta"}

    def __init__(self, model_size: str = "small", device: Optional[str] = None):
        """
        Initialize ASR Engine.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: 'cuda' or 'cpu'. Auto-detects if None.
        """
        self.model_size = model_size
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self._loaded = False

        logger.info(f"ASR Engine initialized (model={model_size}, device={self.device})")

    def load_model(self, callback: Optional[Callable] = None):
        """
        Load the Whisper model into memory.

        Args:
            callback: Optional function to report loading progress.
        """
        try:
            import whisper

            if callback:
                callback(f"Loading Whisper '{self.model_size}' model...")

            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size, device=self.device)
            self._loaded = True

            if callback:
                callback("ASR model loaded successfully!")
            logger.info("Whisper model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            if callback:
                callback(f"Error loading ASR model: {e}")
            raise

    def transcribe(
        self,
        audio_data: Union[np.ndarray, str, Path],
        language: Optional[str] = None,
        task: str = "transcribe",
    ) -> dict:
        """
        Transcribe audio data to text.

        Args:
            audio_data: NumPy array of audio samples (float32, 16kHz)
                        or path to an audio file.
            language: Language code ('en', 'hi', 'ta') or None for auto-detect.
            task: 'transcribe' or 'translate' (translate always outputs English).

        Returns:
            dict with keys: text, language, segments, confidence
        """
        if not self._loaded:
            raise RuntimeError("ASR model not loaded. Call load_model() first.")

        if language and language not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Language '{language}' might not be well-supported.")

        try:
            # Prepare transcription options
            options = {
                "task": task,
                "fp16": self.device == "cuda",
            }
            if language:
                options["language"] = language

            # Handle file path or numpy array
            if isinstance(audio_data, (str, Path)):
                audio_input = str(audio_data)
            elif isinstance(audio_data, np.ndarray):
                # Ensure correct format: float32, mono
                if audio_data.dtype != np.float32:
                    audio_data = audio_data.astype(np.float32)
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.mean(axis=1)  # Convert to mono
                audio_input = audio_data
            else:
                raise ValueError(f"Unsupported audio_data type: {type(audio_data)}")

            result = self.model.transcribe(audio_input, **options)

            # Calculate average confidence from segments
            segments = result.get("segments", [])
            avg_confidence = 0.0
            if segments:
                avg_confidence = sum(
                    seg.get("avg_logprob", -1.0) for seg in segments
                ) / len(segments)
                # Convert log probability to a 0-1 confidence score
                avg_confidence = min(1.0, max(0.0, 1.0 + avg_confidence))

            detected_language = result.get("language", language or "unknown")

            return {
                "text": result["text"].strip(),
                "language": detected_language,
                "segments": segments,
                "confidence": round(avg_confidence, 3),
            }

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    def detect_language(self, audio_data: np.ndarray) -> dict:
        """
        Detect the spoken language from an audio sample.

        Args:
            audio_data: NumPy array of audio samples.

        Returns:
            dict with detected language code and probabilities.
        """
        if not self._loaded:
            raise RuntimeError("ASR model not loaded. Call load_model() first.")

        import whisper

        # Pad/trim to 30 seconds as required by Whisper
        audio = whisper.pad_or_trim(audio_data.astype(np.float32))
        mel = whisper.log_mel_spectrogram(audio).to(self.device)

        _, probs = self.model.detect_language(mel)

        # Get top languages
        top_langs = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "detected": top_langs[0][0],
            "confidence": round(top_langs[0][1], 3),
            "top_languages": {k: round(v, 3) for k, v in top_langs},
        }

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def unload(self):
        """Free the model from memory."""
        if self.model is not None:
            del self.model
            self.model = None
            self._loaded = False
            if self.device == "cuda":
                torch.cuda.empty_cache()
            logger.info("ASR model unloaded")
