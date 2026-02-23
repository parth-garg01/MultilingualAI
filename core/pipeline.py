"""
LinguaFlow — Main Processing Pipeline
Orchestrates the entire flow: Audio → ASR → Emotion → Idiom Mapping → Translation → TTS
"""

import logging
import time
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from typing import Optional, Callable

from core.asr.engine import ASREngine
from core.translator.engine import TranslationEngine
from core.tts.engine import TTSEngine
from core.emotion.analyzer import EmotionAnalyzer
from core.idiom_mapper.mapper import IdiomMapper

logger = logging.getLogger(__name__)


class LinguaFlowPipeline:
    """
    The main LinguaFlow processing pipeline.
    Orchestrates all AI components in sequence:
    Audio → ASR → Emotion Analysis → Idiom Detection → Translation → TTS

    The pipeline is designed to be UI-agnostic and can be used
    from a desktop app, API server, or CLI.
    """

    def __init__(
        self,
        asr_model_size: str = "small",
        device: Optional[str] = None,
    ):
        """
        Initialize the LinguaFlow pipeline.

        Args:
            asr_model_size: Whisper model size (tiny, base, small, medium, large).
            device: Compute device ('cuda' or 'cpu'). Auto-detects if None.
        """
        self.asr = ASREngine(model_size=asr_model_size, device=device)
        self.translator = TranslationEngine(device=device)
        self.tts = TTSEngine()
        self.emotion = EmotionAnalyzer()
        self.idiom_mapper = IdiomMapper()

        self._initialized = False
        self._is_recording = False
        self._audio_buffer = []
        self._recording_stream = None

        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self._input_device = None  # None = system default

        logger.info("LinguaFlow Pipeline created")

    # ================================================================
    # Audio Device Management
    # ================================================================

    @staticmethod
    def list_input_devices() -> list:
        """
        List all available audio input devices (microphones).

        Returns:
            List of dicts with 'id', 'name', 'channels', 'is_default'.
        """
        devices = []
        try:
            all_devices = sd.query_devices()
            default_input = sd.default.device[0]

            for i, d in enumerate(all_devices):
                if d["max_input_channels"] > 0:
                    devices.append({
                        "id": i,
                        "name": d["name"],
                        "channels": d["max_input_channels"],
                        "is_default": i == default_input,
                        "sample_rate": d.get("default_samplerate", 16000),
                    })
        except Exception as e:
            logger.error(f"Failed to list input devices: {e}")

        return devices

    @staticmethod
    def list_output_devices() -> list:
        """
        List all available audio output devices (speakers).

        Returns:
            List of dicts with 'id', 'name', 'channels', 'is_default'.
        """
        devices = []
        try:
            all_devices = sd.query_devices()
            default_output = sd.default.device[1]

            for i, d in enumerate(all_devices):
                if d["max_output_channels"] > 0:
                    devices.append({
                        "id": i,
                        "name": d["name"],
                        "channels": d["max_output_channels"],
                        "is_default": i == default_output,
                    })
        except Exception as e:
            logger.error(f"Failed to list output devices: {e}")

        return devices

    def set_input_device(self, device_id: int):
        """
        Set the audio input device.

        Args:
            device_id: Device ID from list_input_devices().
        """
        self._input_device = device_id
        logger.info(f"Input device set to: {device_id}")

    def set_output_device(self, device_id: int):
        """
        Set the audio output device.

        Args:
            device_id: Device ID from list_output_devices().
        """
        sd.default.device = (sd.default.device[0], device_id)
        logger.info(f"Output device set to: {device_id}")

    @property
    def input_device(self):
        return self._input_device

    def initialize(
        self,
        source_lang: str = "en",
        target_lang: str = "hi",
        callback: Optional[Callable] = None,
    ):
        """
        Load all required models for the given language pair.

        Args:
            source_lang: Source language code.
            target_lang: Target language code.
            callback: Progress callback function(message: str).
        """
        start_time = time.time()

        try:
            # Step 1: Load ASR
            if callback:
                callback("Loading speech recognition model...")
            self.asr.load_model(callback)

            # Step 2: Load Translation models
            if callback:
                callback("Loading translation models...")
            self.translator.load_model(source_lang, target_lang, callback)
            # Also load reverse direction
            self.translator.load_model(target_lang, source_lang, callback)

            # Step 3: Load Emotion model
            if callback:
                callback("Loading emotion analysis model...")
            self.emotion.load_model(callback)

            self._initialized = True
            elapsed = time.time() - start_time

            if callback:
                callback(
                    f"All models loaded successfully! ({elapsed:.1f}s)"
                )
            logger.info(
                f"Pipeline initialized in {elapsed:.1f}s "
                f"({source_lang}↔{target_lang})"
            )

        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            if callback:
                callback(f"Initialization error: {e}")
            raise

    def ensure_pair_loaded(
        self,
        source_lang: str,
        target_lang: str,
        callback: Optional[Callable] = None,
    ):
        """Ensure translation models for a language pair are loaded."""
        if not self.translator.is_pair_loaded(source_lang, target_lang):
            self.translator.load_model(source_lang, target_lang, callback)

    # ================================================================
    # Recording
    # ================================================================

    def start_recording(self, callback: Optional[Callable] = None):
        """
        Start recording audio from the microphone.

        Args:
            callback: Called with audio chunks for visualization.
        """
        if self._is_recording:
            logger.warning("Already recording")
            return

        self._audio_buffer = []
        self._is_recording = True

        def audio_callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"Audio status: {status}")
            if self._is_recording:
                self._audio_buffer.append(indata.copy())
                if callback:
                    callback(indata.copy().flatten())

        try:
            stream_kwargs = {
                "samplerate": self.sample_rate,
                "channels": self.channels,
                "dtype": "float32",
                "callback": audio_callback,
                "blocksize": int(self.sample_rate * 0.1),  # 100ms chunks
            }
            if self._input_device is not None:
                stream_kwargs["device"] = self._input_device
                logger.info(f"Using input device: {self._input_device}")
            else:
                logger.info(f"Using default input device: {sd.default.device[0]}")

            self._recording_stream = sd.InputStream(**stream_kwargs)
            self._recording_stream.start()
            logger.info("Recording started")

        except Exception as e:
            self._is_recording = False
            logger.error(f"Failed to start recording: {e}")
            raise

    def stop_recording(self) -> Optional[np.ndarray]:
        """
        Stop recording and return the captured audio.

        Returns:
            NumPy array of recorded audio (float32, mono, 16kHz).
        """
        if not self._is_recording:
            return None

        self._is_recording = False

        if self._recording_stream:
            self._recording_stream.stop()
            self._recording_stream.close()
            self._recording_stream = None

        if not self._audio_buffer:
            logger.warning("No audio captured")
            return None

        # Concatenate all chunks
        audio = np.concatenate(self._audio_buffer, axis=0).flatten()
        self._audio_buffer = []

        logger.info(
            f"Recording stopped: {len(audio)} samples "
            f"({len(audio) / self.sample_rate:.1f}s)"
        )
        return audio

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    # ================================================================
    # Main Processing Pipeline
    # ================================================================

    def process(
        self,
        audio_data: np.ndarray,
        source_lang: str,
        target_lang: str,
        callback: Optional[Callable] = None,
    ) -> dict:
        """
        Run the full translation pipeline on recorded audio.

        Args:
            audio_data: NumPy array of audio (float32, 16kHz).
            source_lang: Source language code ('en', 'hi', 'ta').
            target_lang: Target language code ('en', 'hi', 'ta').
            callback: Progress callback(event_type: str, data: any).
                event_type can be: 'status', 'asr', 'emotion',
                'idioms', 'translation', 'tts', 'complete', 'error'

        Returns:
            dict with all results from each pipeline stage.
        """
        if not self._initialized:
            raise RuntimeError(
                "Pipeline not initialized. Call initialize() first."
            )

        start_time = time.time()
        result = {
            "original_text": "",
            "translated_text": "",
            "detected_language": source_lang,
            "emotion": {},
            "audio_features": {},
            "idioms_found": [],
            "audio_output_path": None,
            "latency_ms": 0,
            "success": False,
        }

        try:
            # ──────────────────────────────────────────────
            # Step 1: Automatic Speech Recognition
            # ──────────────────────────────────────────────
            if callback:
                callback("status", "🎤 Transcribing speech...")

            asr_result = self.asr.transcribe(audio_data, language=source_lang)
            original_text = asr_result["text"]
            result["original_text"] = original_text
            result["detected_language"] = asr_result["language"]

            if callback:
                callback("asr", {
                    "text": original_text,
                    "language": asr_result["language"],
                    "confidence": asr_result["confidence"],
                })

            if not original_text.strip():
                if callback:
                    callback("status", "⚠️ No speech detected")
                    callback("error", "No speech detected in audio")
                return result

            logger.info(f"ASR result: '{original_text}'")

            # ──────────────────────────────────────────────
            # Step 2: Emotion Analysis (parallel text + audio)
            # ──────────────────────────────────────────────
            if callback:
                callback("status", "🎭 Analyzing emotion...")

            emotion_result = self.emotion.analyze_combined(
                original_text, audio_data, self.sample_rate
            )
            result["emotion"] = emotion_result["text_emotion"]
            result["audio_features"] = emotion_result["audio_features"]

            if callback:
                callback("emotion", emotion_result)

            logger.info(
                f"Emotion: {emotion_result['primary_emoji']} "
                f"{emotion_result['primary_label']}"
            )

            # ──────────────────────────────────────────────
            # Step 3: Idiom Detection & Mapping
            # ──────────────────────────────────────────────
            if callback:
                callback("status", "📖 Checking for idioms...")

            processed_text, idioms = self.idiom_mapper.map_idioms(
                original_text, source_lang, target_lang
            )
            result["idioms_found"] = idioms

            if idioms and callback:
                callback("idioms", idioms)
                for idiom in idioms:
                    logger.info(
                        f"Idiom: '{idiom['original']}' → '{idiom['translated']}'"
                    )

            # ──────────────────────────────────────────────
            # Step 4: Translation
            # ──────────────────────────────────────────────
            if callback:
                callback("status", "🌐 Translating...")

            # Ensure models are loaded for this pair
            self.ensure_pair_loaded(source_lang, target_lang)

            translated_text = self.translator.translate(
                processed_text, source_lang, target_lang
            )
            result["translated_text"] = translated_text

            if callback:
                callback("translation", translated_text)

            logger.info(f"Translation: '{translated_text}'")

            # ──────────────────────────────────────────────
            # Step 5: Text-to-Speech
            # ──────────────────────────────────────────────
            if callback:
                callback("status", "🔊 Generating speech...")

            emotion_label = emotion_result.get("primary_label", "Neutral")
            audio_path = self.tts.synthesize(
                translated_text,
                target_lang,
                emotion=emotion_label,
            )
            result["audio_output_path"] = audio_path

            if callback:
                callback("tts", audio_path)

            # ──────────────────────────────────────────────
            # Complete
            # ──────────────────────────────────────────────
            elapsed_ms = (time.time() - start_time) * 1000
            result["latency_ms"] = round(elapsed_ms)
            result["success"] = True

            if callback:
                callback("status", f"✅ Done! ({elapsed_ms:.0f}ms)")
                callback("complete", result)

            logger.info(f"Pipeline complete in {elapsed_ms:.0f}ms")

        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            if callback:
                callback("error", str(e))
                callback("status", f"❌ Error: {e}")
            result["error"] = str(e)

        return result

    def process_async(
        self,
        audio_data: np.ndarray,
        source_lang: str,
        target_lang: str,
        callback: Optional[Callable] = None,
    ) -> threading.Thread:
        """
        Run the pipeline asynchronously in a background thread.

        Returns:
            The thread running the pipeline.
        """

        def _worker():
            self.process(audio_data, source_lang, target_lang, callback)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

    # ================================================================
    # Audio Playback
    # ================================================================

    @staticmethod
    def play_audio(file_path: str, callback: Optional[Callable] = None):
        """
        Play an audio file through the speakers.

        Args:
            file_path: Path to audio file (MP3 or WAV).
            callback: Called when playback finishes.
        """

        def _play():
            try:
                # Try pydub first for MP3 support
                from pydub import AudioSegment
                from pydub.playback import play as pydub_play

                audio = AudioSegment.from_file(file_path)
                pydub_play(audio)

            except ImportError:
                # Fallback to sounddevice (WAV only)
                try:
                    data, sr = sf.read(file_path)
                    sd.play(data, sr)
                    sd.wait()
                except Exception as e:
                    logger.error(f"Playback failed: {e}")

            if callback:
                callback()

        thread = threading.Thread(target=_play, daemon=True)
        thread.start()
        return thread

    # ================================================================
    # Utility
    # ================================================================

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def save_audio(self, audio_data: np.ndarray, path: str):
        """Save audio data to a WAV file."""
        sf.write(path, audio_data, self.sample_rate)
        logger.info(f"Audio saved to {path}")

    def cleanup(self):
        """Clean up resources."""
        if self._is_recording:
            self.stop_recording()
        self.tts.cleanup()
        logger.info("Pipeline cleaned up")

    def get_status(self) -> dict:
        """Get current pipeline status."""
        return {
            "initialized": self._initialized,
            "recording": self._is_recording,
            "asr_loaded": self.asr.is_loaded,
            "emotion_loaded": self.emotion.is_loaded,
            "translation_pairs": self.translator.get_loaded_pairs(),
            "idiom_count": self.idiom_mapper.get_idiom_count(),
        }
