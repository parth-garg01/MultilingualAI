"""
LinguaFlow — Text-to-Speech Engine
Uses Microsoft Edge TTS for natural-sounding voice synthesis.
Free, no API key required, supports English, Hindi, and Tamil.
"""

import asyncio
import logging
import tempfile
import threading
from pathlib import Path
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class TTSEngine:
    """
    Text-to-Speech engine powered by Edge TTS.
    Generates natural-sounding audio in English, Hindi, and Tamil.
    """

    # Voice mapping: language code → (male_voice, female_voice)
    VOICE_MAP = {
        "en": {
            "male": "en-US-GuyNeural",
            "female": "en-US-JennyNeural",
        },
        "hi": {
            "male": "hi-IN-MadhurNeural",
            "female": "hi-IN-SwaraNeural",
        },
        "ta": {
            "male": "ta-IN-ValluvarNeural",
            "female": "ta-IN-PallaviNeural",
        },
    }

    # Emotion-to-prosody mapping
    EMOTION_PROSODY = {
        "Very Positive": {"rate": "+10%", "pitch": "+5Hz"},
        "Positive": {"rate": "+5%", "pitch": "+2Hz"},
        "Neutral": {"rate": "+0%", "pitch": "+0Hz"},
        "Negative": {"rate": "-5%", "pitch": "-3Hz"},
        "Very Negative": {"rate": "-10%", "pitch": "-5Hz"},
    }

    def __init__(self, output_dir: Optional[Path] = None, voice_gender: str = "male"):
        """
        Initialize TTS Engine.

        Args:
            output_dir: Directory for output audio files.
            voice_gender: Default voice gender ('male' or 'female').
        """
        self.output_dir = output_dir or Path(tempfile.gettempdir()) / "linguaflow_tts"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.voice_gender = voice_gender
        self._file_counter = 0

        logger.info(f"TTS Engine initialized (output_dir={self.output_dir})")

    def get_voice(self, language: str, gender: Optional[str] = None) -> str:
        """Get the voice name for a language and gender."""
        gender = gender or self.voice_gender
        voices = self.VOICE_MAP.get(language, self.VOICE_MAP["en"])
        return voices.get(gender, voices["male"])

    def synthesize(
        self,
        text: str,
        language: str,
        output_path: Optional[str] = None,
        emotion: Optional[str] = None,
        gender: Optional[str] = None,
        callback: Optional[Callable] = None,
    ) -> str:
        """
        Synthesize speech from text.

        Args:
            text: Text to convert to speech.
            language: Target language code ('en', 'hi', 'ta').
            output_path: Optional output file path. Auto-generated if None.
            emotion: Optional emotion label for prosody adjustment.
            gender: Voice gender override.
            callback: Optional progress callback.

        Returns:
            Path to the generated audio file (MP3).
        """
        if not text or not text.strip():
            raise ValueError("Cannot synthesize empty text.")

        if output_path is None:
            self._file_counter += 1
            output_path = str(
                self.output_dir / f"tts_output_{self._file_counter}.mp3"
            )

        voice = self.get_voice(language, gender)

        # Get prosody adjustments based on emotion
        prosody = self.EMOTION_PROSODY.get(emotion, self.EMOTION_PROSODY["Neutral"])

        if callback:
            callback(f"Generating speech in {language}...")

        try:
            # Run async synthesis in a synchronous context
            self._run_synthesis(text, voice, output_path, prosody)

            if callback:
                callback("Speech generated!")
            logger.info(
                f"TTS generated: {language} ({voice}) → {output_path}"
            )
            return output_path

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            if callback:
                callback(f"TTS error: {e}")
            raise

    def _run_synthesis(
        self, text: str, voice: str, output_path: str, prosody: dict
    ):
        """Run the async edge-tts synthesis in a sync context."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # We're inside an async context — run in a new thread
            result = {"error": None}

            def _thread_target():
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    new_loop.run_until_complete(
                        self._synthesize_async(text, voice, output_path, prosody)
                    )
                    new_loop.close()
                except Exception as e:
                    result["error"] = e

            thread = threading.Thread(target=_thread_target)
            thread.start()
            thread.join(timeout=30)

            if result["error"]:
                raise result["error"]
        else:
            # No running loop — create one
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                new_loop.run_until_complete(
                    self._synthesize_async(text, voice, output_path, prosody)
                )
            finally:
                new_loop.close()

    async def _synthesize_async(
        self, text: str, voice: str, output_path: str, prosody: dict
    ):
        """Async edge-tts synthesis."""
        import edge_tts

        communicate = edge_tts.Communicate(
            text,
            voice,
            rate=prosody.get("rate", "+0%"),
            pitch=prosody.get("pitch", "+0Hz"),
        )
        await communicate.save(output_path)

    def synthesize_async_in_thread(
        self,
        text: str,
        language: str,
        callback: Optional[Callable] = None,
        done_callback: Optional[Callable] = None,
    ):
        """
        Synthesize speech in a background thread.

        Args:
            text: Text to synthesize.
            language: Language code.
            callback: Progress callback.
            done_callback: Called with (audio_path, error) when complete.
        """

        def _worker():
            try:
                path = self.synthesize(text, language, callback=callback)
                if done_callback:
                    done_callback(path, None)
            except Exception as e:
                if done_callback:
                    done_callback(None, e)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

    @staticmethod
    def get_available_voices() -> dict:
        """List all available voices (requires internet on first call)."""
        import asyncio

        async def _list():
            import edge_tts
            voices = await edge_tts.list_voices()
            return voices

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_list())
        finally:
            loop.close()

    def cleanup(self):
        """Remove temporary TTS files."""
        import shutil
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir, ignore_errors=True)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info("TTS temp files cleaned up")
