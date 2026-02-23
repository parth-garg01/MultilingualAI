"""
LinguaFlow — Main Desktop Application
Premium dark-themed CustomTkinter application for real-time
multilingual translation with emotional intelligence.
"""

import customtkinter as ctk
import threading
import logging
import sys
import numpy as np
from typing import Optional

from config import (
    APP_NAME, APP_VERSION, APP_TAGLINE,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT,
    LANGUAGES, LANG_BY_CODE, ASR_MODEL_SIZE,
)
from ui.themes.colors import DarkTheme, LightTheme
from ui.components.language_selector import LanguageSelector
from ui.components.waveform import WaveformVisualizer
from ui.components.transcript_panel import TranscriptPanel
from ui.components.emotion_badge import EmotionBadge
from ui.components.control_bar import ControlBar
from core.pipeline import LinguaFlowPipeline

logger = logging.getLogger(__name__)


class LinguaFlowApp(ctk.CTk):
    """
    Main LinguaFlow desktop application window.
    """

    def __init__(self):
        super().__init__()

        # ── State ──
        self.theme = DarkTheme
        self._is_dark = True
        self._pipeline: Optional[LinguaFlowPipeline] = None
        self._recorded_audio: Optional[np.ndarray] = None
        self._last_audio_path: Optional[str] = None
        self._init_thread: Optional[threading.Thread] = None
        self._input_devices: list = []  # Available microphones
        self._device_id_map: dict = {}  # Display name → device ID

        # ── Window Configuration ──
        self.title(f"{APP_NAME} — {APP_TAGLINE}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Set window background
        self.configure(fg_color=self.theme.BG_DARKEST)

        # Build UI
        self._build_ui()

        # Start model loading in background
        self.after(500, self._initialize_pipeline)

    def _build_ui(self):
        """Build the complete application UI."""
        t = self.theme

        # ══════════════════════════════════════════════
        # HEADER
        # ══════════════════════════════════════════════
        header = ctk.CTkFrame(self, fg_color=t.BG_PRIMARY, height=50)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="both", expand=True, padx=t.PADDING_MD, pady=4)

        # Logo & Title
        brand = ctk.CTkFrame(header_inner, fg_color="transparent")
        brand.pack(side="left")

        ctk.CTkLabel(
            brand,
            text="🌐",
            font=(t.FONT_FAMILY, 24),
        ).pack(side="left", padx=(0, 8))

        title_frame = ctk.CTkFrame(brand, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text=APP_NAME,
            font=(t.FONT_FAMILY, t.FONT_SIZE_XL, "bold"),
            text_color=t.TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text=APP_TAGLINE,
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS),
            text_color=t.TEXT_TERTIARY,
        ).pack(anchor="w")

        # Right side controls
        right_controls = ctk.CTkFrame(header_inner, fg_color="transparent")
        right_controls.pack(side="right")

        # Theme toggle
        self.theme_btn = ctk.CTkButton(
            right_controls,
            text="🌙",
            width=36,
            height=36,
            font=(t.FONT_FAMILY, 16),
            fg_color=t.BG_SURFACE,
            hover_color=t.BG_HOVER,
            text_color=t.TEXT_SECONDARY,
            corner_radius=t.CORNER_RADIUS_SM,
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side="left", padx=4)

        # Version badge
        ctk.CTkLabel(
            right_controls,
            text=f"v{APP_VERSION}",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS),
            text_color=t.TEXT_TERTIARY,
            fg_color=t.BG_SURFACE,
            corner_radius=4,
            padx=8,
            pady=2,
        ).pack(side="left", padx=(8, 0))

        # Separator
        ctk.CTkFrame(
            self, fg_color=t.BORDER, height=1
        ).pack(fill="x")

        # ══════════════════════════════════════════════
        # MAIN CONTENT AREA
        # ══════════════════════════════════════════════
        main = ctk.CTkFrame(self, fg_color=t.BG_DARKEST)
        main.pack(fill="both", expand=True, padx=t.PADDING_MD, pady=t.PADDING_SM)

        # ── Language Selector ──
        self.lang_selector = LanguageSelector(
            main,
            theme=t,
            languages=list(LANGUAGES.keys()),
            default_source="English",
            default_target="Hindi",
            on_change=self._on_language_change,
        )
        self.lang_selector.pack(fill="x", pady=(0, 4))

        # ── Microphone Selector ──
        mic_frame = ctk.CTkFrame(
            main,
            fg_color=t.BG_SECONDARY,
            corner_radius=t.CORNER_RADIUS_SM,
        )
        mic_frame.pack(fill="x", pady=(0, 4))

        mic_inner = ctk.CTkFrame(mic_frame, fg_color="transparent")
        mic_inner.pack(fill="x", padx=t.PADDING_MD, pady=4)

        ctk.CTkLabel(
            mic_inner,
            text="🎙️ MICROPHONE",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS, "bold"),
            text_color=t.TEXT_TERTIARY,
        ).pack(side="left", padx=(0, t.PADDING_SM))

        self.mic_var = ctk.StringVar(value="Loading devices...")
        self.mic_dropdown = ctk.CTkComboBox(
            mic_inner,
            values=["Loading devices..."],
            variable=self.mic_var,
            command=self._on_mic_change,
            width=400,
            height=32,
            font=(t.FONT_FAMILY, t.FONT_SIZE_SM),
            dropdown_font=(t.FONT_FAMILY, t.FONT_SIZE_SM),
            fg_color=t.BG_ELEVATED,
            border_color=t.BORDER,
            button_color=t.PRIMARY,
            button_hover_color=t.PRIMARY_LIGHT,
            dropdown_fg_color=t.BG_SURFACE,
            dropdown_hover_color=t.BG_HOVER,
            text_color=t.TEXT_PRIMARY,
            dropdown_text_color=t.TEXT_PRIMARY,
            corner_radius=t.CORNER_RADIUS_SM,
            state="readonly",
        )
        self.mic_dropdown.pack(side="left", padx=t.PADDING_SM)

        # Audio level indicator
        self.level_label = ctk.CTkLabel(
            mic_inner,
            text="Level: --",
            font=(t.FONT_FAMILY_MONO, t.FONT_SIZE_XS),
            text_color=t.TEXT_TERTIARY,
        )
        self.level_label.pack(side="right", padx=(t.PADDING_SM, 0))

        self.level_bar = ctk.CTkProgressBar(
            mic_inner,
            width=120,
            height=8,
            fg_color=t.BG_SURFACE,
            progress_color=t.SUCCESS,
            corner_radius=4,
        )
        self.level_bar.pack(side="right")
        self.level_bar.set(0)

        # ── Transcript Panels (takes remaining space but limited) ──
        self.transcript = TranscriptPanel(main, theme=t)
        self.transcript.pack(fill="both", expand=True, pady=(0, 4))

        # ── Bottom Section: Waveform | Emotion | Controls (all in one compact row) ──
        bottom = ctk.CTkFrame(main, fg_color="transparent", height=140)
        bottom.pack(fill="x", pady=(0, 4))
        bottom.pack_propagate(False)
        bottom.grid_columnconfigure(0, weight=5)  # waveform (widest)
        bottom.grid_columnconfigure(1, weight=2)  # emotion
        bottom.grid_columnconfigure(2, weight=3)  # controls
        bottom.grid_rowconfigure(0, weight=1)

        # Waveform (left)
        self.waveform = WaveformVisualizer(
            bottom,
            theme=t,
            bar_count=48,
            height=110,
        )
        self.waveform.grid(
            row=0, column=0,
            sticky="nsew",
            padx=(0, 4),
        )

        # Emotion Badge (center)
        self.emotion_badge = EmotionBadge(bottom, theme=t)
        self.emotion_badge.grid(
            row=0, column=1,
            sticky="nsew",
            padx=4,
        )

        # Controls (right) — vertical stack of buttons
        controls_panel = ctk.CTkFrame(
            bottom,
            fg_color=t.BG_SECONDARY,
            corner_radius=t.CORNER_RADIUS_SM,
        )
        controls_panel.grid(row=0, column=2, sticky="nsew", padx=(4, 0))

        self.controls = ControlBar(
            controls_panel,
            theme=t,
            on_speak=self._on_speak,
            on_stop=self._on_stop,
            on_play=self._on_play,
            on_clear=self._on_clear,
            compact=True,
        )
        self.controls.pack(fill="both", expand=True, padx=4, pady=4)

        # ══════════════════════════════════════════════
        # STATUS BAR
        # ══════════════════════════════════════════════
        ctk.CTkFrame(
            self, fg_color=t.BORDER, height=1
        ).pack(fill="x")

        status_bar = ctk.CTkFrame(self, fg_color=t.BG_PRIMARY, height=32)
        status_bar.pack(fill="x")
        status_bar.pack_propagate(False)

        status_inner = ctk.CTkFrame(status_bar, fg_color="transparent")
        status_inner.pack(fill="both", expand=True, padx=t.PADDING_MD)

        self.status_label = ctk.CTkLabel(
            status_inner,
            text="⏳ Loading models...",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS),
            text_color=t.TEXT_TERTIARY,
        )
        self.status_label.pack(side="left")

        self.latency_label = ctk.CTkLabel(
            status_inner,
            text="Latency: --",
            font=(t.FONT_FAMILY_MONO, t.FONT_SIZE_XS),
            text_color=t.TEXT_TERTIARY,
        )
        self.latency_label.pack(side="right")

        self.model_status = ctk.CTkLabel(
            status_inner,
            text="Models: Loading...",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS),
            text_color=t.WARNING,
        )
        self.model_status.pack(side="right", padx=t.PADDING_LG)

    # ================================================================
    # Pipeline Management
    # ================================================================

    def _initialize_pipeline(self):
        """Initialize the AI pipeline in a background thread."""

        def _init():
            try:
                self._pipeline = LinguaFlowPipeline(
                    asr_model_size=ASR_MODEL_SIZE
                )

                src = LANGUAGES[self.lang_selector.source_language]["code"]
                tgt = LANGUAGES[self.lang_selector.target_language]["code"]

                self._pipeline.initialize(
                    source_lang=src,
                    target_lang=tgt,
                    callback=self._update_status_safe,
                )

                self.after(0, self._on_pipeline_ready)

            except Exception as e:
                logger.error(f"Pipeline init failed: {e}")
                self.after(
                    0,
                    lambda: self._update_status(f"❌ Error: {e}"),
                )

        self._init_thread = threading.Thread(target=_init, daemon=True)
        self._init_thread.start()

    def _on_pipeline_ready(self):
        """Called when pipeline finishes loading."""
        t = self.theme
        self.status_label.configure(
            text="✅ Ready — Click SPEAK to begin",
            text_color=t.SUCCESS,
        )
        self.model_status.configure(
            text="Models: Loaded",
            text_color=t.SUCCESS,
        )
        # Populate microphone list
        self._populate_mic_list()

    def _update_status_safe(self, message: str):
        """Thread-safe status update."""
        self.after(0, lambda: self._update_status(message))

    def _update_status(self, message: str):
        """Update status bar message."""
        self.status_label.configure(text=message)

    # ================================================================
    # Event Handlers
    # ================================================================

    def _on_language_change(self, source: str, target: str):
        """Handle language selection change."""
        logger.info(f"Language changed: {source} → {target}")

        if self._pipeline and self._pipeline.is_initialized:
            src_code = LANGUAGES[source]["code"]
            tgt_code = LANGUAGES[target]["code"]

            def _load():
                try:
                    self._pipeline.ensure_pair_loaded(
                        src_code, tgt_code, self._update_status_safe
                    )
                    self.after(
                        0,
                        lambda: self._update_status(
                            f"✅ Ready — {source} → {target}"
                        ),
                    )
                except Exception as e:
                    self.after(
                        0,
                        lambda: self._update_status(f"❌ Error: {e}"),
                    )

            threading.Thread(target=_load, daemon=True).start()

    def _on_speak(self):
        """Handle speak button press — start recording."""
        if not self._pipeline or not self._pipeline.is_initialized:
            self._update_status("⚠️ Models still loading, please wait...")
            self.controls.set_idle()
            return

        self.transcript.set_source_loading()
        self.transcript.set_target_loading()
        self.waveform.set_active(True)
        self.controls.disable_play()

        self._update_status("🎤 Recording... Speak now!")

        try:
            self._pipeline.start_recording(
                callback=self._on_audio_chunk
            )
        except Exception as e:
            self._update_status(f"❌ Microphone error: {e}")
            self.controls.set_idle()
            self.waveform.set_active(False)

    def _on_audio_chunk(self, chunk: np.ndarray):
        """Handle incoming audio chunk for waveform visualization."""
        self.after(0, lambda c=chunk.copy(): self._update_audio_visuals(c))

    def _update_audio_visuals(self, chunk: np.ndarray):
        """Update waveform and level indicator with audio data."""
        self.waveform.update_waveform(chunk)

        # Update level indicator
        rms = float(np.sqrt(np.mean(chunk ** 2)))
        peak = float(np.max(np.abs(chunk)))
        level = min(1.0, peak * 5)  # Scale for visibility
        self.level_bar.set(level)

        t = self.theme
        if peak > 0.1:
            self.level_label.configure(text=f"Level: {peak:.2f}", text_color=t.SUCCESS)
            self.level_bar.configure(progress_color=t.SUCCESS)
        elif peak > 0.01:
            self.level_label.configure(text=f"Level: {peak:.2f}", text_color=t.WARNING)
            self.level_bar.configure(progress_color=t.WARNING)
        else:
            self.level_label.configure(text=f"Level: {peak:.3f}", text_color=t.ERROR)
            self.level_bar.configure(progress_color=t.ERROR)

    def _on_stop(self):
        """Handle stop button press — process recorded audio."""
        if not self._pipeline:
            return

        self._recorded_audio = self._pipeline.stop_recording()
        self.waveform.set_active(False)
        self.waveform.set_processing()

        if self._recorded_audio is None or len(self._recorded_audio) < 1600:
            self._update_status("⚠️ Recording too short, try again")
            self.controls.set_idle()
            self.transcript.clear()
            return

        # Check audio level
        peak = float(np.max(np.abs(self._recorded_audio)))
        if peak < 0.005:
            self._update_status(
                "⚠️ No audio detected! Check your microphone selection above."
            )
            self.controls.set_idle()
            self.transcript.clear()
            self.level_bar.set(0)
            self.level_label.configure(
                text="No audio!",
                text_color=self.theme.ERROR,
            )
            return

        self.controls.set_processing()
        self._update_status("⏳ Processing audio...")

        src_code = LANGUAGES[self.lang_selector.source_language]["code"]
        tgt_code = LANGUAGES[self.lang_selector.target_language]["code"]

        # Process in background
        self._pipeline.process_async(
            self._recorded_audio,
            src_code,
            tgt_code,
            callback=self._on_pipeline_event,
        )

    def _on_pipeline_event(self, event_type: str, data):
        """Handle pipeline callback events (thread-safe dispatch)."""
        self.after(0, lambda: self._handle_event(event_type, data))

    def _handle_event(self, event_type: str, data):
        """Handle pipeline events on the main thread."""
        t = self.theme
        src_name = self.lang_selector.source_language
        tgt_name = self.lang_selector.target_language

        if event_type == "status":
            self._update_status(data)

        elif event_type == "asr":
            self.transcript.set_source_text(
                data["text"],
                language=src_name,
                confidence=data.get("confidence", 0),
            )

        elif event_type == "emotion":
            self.emotion_badge.update_emotion(data)

        elif event_type == "idioms":
            self.controls.show_idioms(data)

        elif event_type == "translation":
            self.transcript.set_target_text(
                data,
                language=tgt_name,
            )

        elif event_type == "tts":
            self._last_audio_path = data

        elif event_type == "complete":
            latency = data.get("latency_ms", 0)
            self.latency_label.configure(
                text=f"Latency: {latency}ms",
                text_color=t.SUCCESS if latency < 1500 else t.WARNING,
            )
            self.controls.set_complete()
            self.waveform.set_complete()

        elif event_type == "error":
            self._update_status(f"❌ Error: {data}")
            self.controls.set_idle()
            self.waveform.set_active(False)

    def _on_play(self):
        """Play the translated audio."""
        if self._last_audio_path and self._pipeline:
            self._update_status("🔊 Playing translation...")
            self._pipeline.play_audio(
                self._last_audio_path,
                callback=lambda: self.after(
                    0,
                    lambda: self._update_status("✅ Playback complete"),
                ),
            )

    def _on_clear(self):
        """Clear all panels and reset state."""
        self.transcript.clear()
        self.emotion_badge.reset()
        self.controls.disable_play()
        self.controls.hide_idioms()
        self._recorded_audio = None
        self._last_audio_path = None
        self.latency_label.configure(
            text="Latency: --",
            text_color=self.theme.TEXT_TERTIARY,
        )
        self._update_status("✅ Ready — Click SPEAK to begin")

    # ================================================================
    # Microphone Management
    # ================================================================

    def _populate_mic_list(self):
        """Populate the microphone dropdown with available devices."""
        if not self._pipeline:
            return

        self._input_devices = LinguaFlowPipeline.list_input_devices()
        self._device_id_map = {}
        display_names = []

        for dev in self._input_devices:
            suffix = " ⭐" if dev["is_default"] else ""
            name = f"{dev['name']}{suffix}"
            display_names.append(name)
            self._device_id_map[name] = dev["id"]

        if display_names:
            self.mic_dropdown.configure(values=display_names)
            # Select default device
            for name in display_names:
                if "⭐" in name:
                    self.mic_var.set(name)
                    break
            else:
                self.mic_var.set(display_names[0])

            logger.info(
                f"Found {len(display_names)} input devices"
            )
        else:
            self.mic_dropdown.configure(values=["No devices found"])
            self.mic_var.set("No devices found")

    def _on_mic_change(self, selected: str):
        """Handle microphone selection change."""
        if selected in self._device_id_map and self._pipeline:
            device_id = self._device_id_map[selected]
            self._pipeline.set_input_device(device_id)
            clean_name = selected.replace(" ⭐", "")
            self._update_status(f"🎙️ Microphone: {clean_name}")
            logger.info(f"Microphone changed to [{device_id}] {clean_name}")

    def _toggle_theme(self):
        """Toggle between dark and light theme."""
        # Note: Full theme switching would require rebuilding all widgets
        # For now, toggle CTk appearance mode
        self._is_dark = not self._is_dark
        if self._is_dark:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="🌙")
        else:
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="☀️")

    # ================================================================
    # Cleanup
    # ================================================================

    def on_closing(self):
        """Handle window close event."""
        if self._pipeline:
            self._pipeline.cleanup()
        self.destroy()
        sys.exit(0)
