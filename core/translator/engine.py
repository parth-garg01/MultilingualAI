"""
LinguaFlow — Translation Engine
Uses Helsinki-NLP MarianMT models for high-quality offline translation.
Supports English, Hindi, and Tamil with pivot translation for unsupported pairs.
"""

import logging
import torch
from typing import Optional, Callable, Dict, Tuple

logger = logging.getLogger(__name__)


class TranslationEngine:
    """
    Neural machine translation engine using MarianMT models.
    Handles direct translation for available pairs and pivot
    translation through English for others (e.g., Hindi ↔ Tamil).
    """

    # Direct model mappings for available language pairs
    MODEL_MAP: Dict[Tuple[str, str], str] = {
        ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
        ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
        ("en", "ta"): "Helsinki-NLP/opus-mt-en-mul",
        ("ta", "en"): "Helsinki-NLP/opus-mt-mul-en",
        # hi↔ta will use English as pivot
    }

    # For multilingual models, target language prefix tokens
    LANG_PREFIXES: Dict[Tuple[str, str], str] = {
        ("en", "ta"): ">>tam<< ",
        ("ta", "en"): "",  # mul-en doesn't need prefix
    }

    def __init__(self, device: Optional[str] = None):
        """
        Initialize Translation Engine.

        Args:
            device: 'cuda' or 'cpu'. Auto-detects if None.
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.models: dict = {}
        self.tokenizers: dict = {}
        self._loaded_pairs: set = set()

        logger.info(f"Translation Engine initialized (device={self.device})")

    def load_model(
        self,
        source_lang: str,
        target_lang: str,
        callback: Optional[Callable] = None,
    ):
        """
        Load a translation model for a specific language pair.

        Args:
            source_lang: Source language code (en, hi, ta).
            target_lang: Target language code (en, hi, ta).
            callback: Optional progress callback.
        """
        pair = (source_lang, target_lang)

        if pair in self._loaded_pairs:
            logger.info(f"Model for {pair} already loaded, skipping.")
            return

        # For pairs without direct models, load pivot models
        if pair not in self.MODEL_MAP:
            if source_lang != "en" and target_lang != "en":
                # Load both legs of the pivot
                if callback:
                    callback(
                        f"Loading pivot translation: {source_lang}→en→{target_lang}..."
                    )
                self.load_model(source_lang, "en", callback)
                self.load_model("en", target_lang, callback)
                self._loaded_pairs.add(pair)
                return
            else:
                raise ValueError(
                    f"No translation model available for {source_lang}→{target_lang}"
                )

        model_name = self.MODEL_MAP[pair]

        try:
            from transformers import MarianMTModel, MarianTokenizer

            if callback:
                callback(f"Loading translation model: {source_lang}→{target_lang}...")

            logger.info(f"Loading MarianMT model: {model_name}")

            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)

            if self.device == "cuda":
                model = model.to(self.device)

            self.tokenizers[pair] = tokenizer
            self.models[pair] = model
            self._loaded_pairs.add(pair)

            if callback:
                callback(f"Translation model {source_lang}→{target_lang} loaded!")
            logger.info(f"MarianMT model loaded: {model_name}")

        except Exception as e:
            logger.error(f"Failed to load translation model {model_name}: {e}")
            if callback:
                callback(f"Error loading translation model: {e}")
            raise

    def load_all_models(self, callback: Optional[Callable] = None):
        """Load all available translation models."""
        pairs = [("en", "hi"), ("hi", "en"), ("en", "ta"), ("ta", "en")]
        for src, tgt in pairs:
            self.load_model(src, tgt, callback)
        # Mark pivot pairs as loaded
        self._loaded_pairs.add(("hi", "ta"))
        self._loaded_pairs.add(("ta", "hi"))

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text from source language to target language.

        Args:
            text: Input text to translate.
            source_lang: Source language code.
            target_lang: Target language code.

        Returns:
            Translated text string.
        """
        if source_lang == target_lang:
            return text

        if not text or not text.strip():
            return ""

        pair = (source_lang, target_lang)

        # Check if we need pivot translation
        if pair not in self.models:
            if source_lang != "en" and target_lang != "en":
                # Pivot through English
                logger.info(
                    f"Using pivot translation: {source_lang}→en→{target_lang}"
                )
                intermediate = self.translate(text, source_lang, "en")
                return self.translate(intermediate, "en", target_lang)
            else:
                raise RuntimeError(
                    f"Translation model for {pair} not loaded. "
                    "Call load_model() first."
                )

        try:
            tokenizer = self.tokenizers[pair]
            model = self.models[pair]

            # Add language prefix if needed (for multilingual models)
            prefix = self.LANG_PREFIXES.get(pair, "")
            input_text = prefix + text

            # Tokenize
            inputs = tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )

            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate translation
            with torch.no_grad():
                translated_tokens = model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True,
                )

            # Decode
            result = tokenizer.decode(
                translated_tokens[0], skip_special_tokens=True
            )

            logger.info(
                f"Translated [{source_lang}→{target_lang}]: "
                f"'{text[:50]}...' → '{result[:50]}...'"
            )
            return result.strip()

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

    def translate_batch(
        self, texts: list, source_lang: str, target_lang: str
    ) -> list:
        """Translate a batch of texts."""
        return [self.translate(t, source_lang, target_lang) for t in texts]

    def get_loaded_pairs(self) -> list:
        """Return list of loaded language pairs."""
        return list(self._loaded_pairs)

    def is_pair_loaded(self, source_lang: str, target_lang: str) -> bool:
        """Check if a translation pair is loaded."""
        return (source_lang, target_lang) in self._loaded_pairs

    def unload(self):
        """Free all models from memory."""
        self.models.clear()
        self.tokenizers.clear()
        self._loaded_pairs.clear()
        if self.device == "cuda":
            torch.cuda.empty_cache()
        logger.info("All translation models unloaded")
