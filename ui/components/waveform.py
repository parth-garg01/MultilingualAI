"""
LinguaFlow — Waveform Visualizer Component
Animated audio waveform display using Canvas.
"""

import customtkinter as ctk
import numpy as np
import math
import time
from typing import Optional


class WaveformVisualizer(ctk.CTkFrame):
    """
    Real-time audio waveform visualizer.
    Displays audio levels as an animated bar graph.
    """

    def __init__(
        self,
        parent,
        theme,
        width: int = 800,
        height: int = 100,
        bar_count: int = 64,
        **kwargs,
    ):
        super().__init__(
            parent,
            fg_color=theme.BG_SECONDARY,
            corner_radius=theme.CORNER_RADIUS,
            **kwargs,
        )

        self.theme = theme
        self.bar_count = bar_count
        self._canvas_width = width
        self._canvas_height = height
        self._is_active = False
        self._levels = np.zeros(bar_count)
        self._target_levels = np.zeros(bar_count)
        self._idle_phase = 0.0
        self._animation_id = None

        self._build_ui()
        self._start_idle_animation()

    def _build_ui(self):
        t = self.theme

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=t.PADDING_MD, pady=(t.PADDING_SM, 0))

        ctk.CTkLabel(
            header,
            text="🎵 AUDIO WAVEFORM",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS, "bold"),
            text_color=t.TEXT_TERTIARY,
        ).pack(side="left")

        self._status_label = ctk.CTkLabel(
            header,
            text="Idle",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS),
            text_color=t.TEXT_TERTIARY,
        )
        self._status_label.pack(side="right")

        # Canvas for waveform
        self.canvas = ctk.CTkCanvas(
            self,
            width=self._canvas_width,
            height=self._canvas_height,
            bg=t.WAVEFORM_BG,
            highlightthickness=0,
        )
        self.canvas.pack(
            fill="both",
            expand=True,
            padx=t.PADDING_MD,
            pady=t.PADDING_SM,
        )

    def _start_idle_animation(self):
        """Animate a gentle sine wave when idle."""
        self._animate_idle()

    def _animate_idle(self):
        """Render idle sine wave animation."""
        if self._is_active:
            return

        self._idle_phase += 0.05
        t = self.theme

        self.canvas.delete("all")
        w = self.canvas.winfo_width() or self._canvas_width
        h = self.canvas.winfo_height() or self._canvas_height

        bar_width = max(2, (w - self.bar_count * 2) / self.bar_count)
        gap = 2

        for i in range(self.bar_count):
            # Gentle sine wave
            wave = math.sin(self._idle_phase + i * 0.15) * 0.3 + 0.35
            wave += math.sin(self._idle_phase * 0.7 + i * 0.1) * 0.1
            bar_h = max(3, wave * h * 0.4)

            x = i * (bar_width + gap) + gap
            y_top = (h - bar_h) / 2
            y_bottom = (h + bar_h) / 2

            # Gradient effect: use idle color
            self.canvas.create_rectangle(
                x, y_top, x + bar_width, y_bottom,
                fill=t.WAVEFORM_IDLE,
                outline="",
            )

        self._animation_id = self.after(33, self._animate_idle)  # ~30fps

    def update_waveform(self, audio_chunk: np.ndarray):
        """
        Update waveform with new audio data.

        Args:
            audio_chunk: NumPy array of audio samples.
        """
        if not self._is_active:
            return

        # Compute RMS levels for each bar
        chunk_size = max(1, len(audio_chunk) // self.bar_count)
        for i in range(self.bar_count):
            start = i * chunk_size
            end = min(start + chunk_size, len(audio_chunk))
            if start < len(audio_chunk):
                segment = audio_chunk[start:end]
                rms = np.sqrt(np.mean(segment**2)) if len(segment) > 0 else 0
                self._target_levels[i] = min(1.0, rms * 8)  # Scale up
            else:
                self._target_levels[i] = 0

    def _animate_active(self):
        """Render active waveform with smooth interpolation."""
        if not self._is_active:
            return

        t = self.theme
        self.canvas.delete("all")

        w = self.canvas.winfo_width() or self._canvas_width
        h = self.canvas.winfo_height() or self._canvas_height

        bar_width = max(2, (w - self.bar_count * 2) / self.bar_count)
        gap = 2

        # Smooth interpolation toward target levels
        alpha = 0.3  # Smoothing factor
        self._levels = self._levels * (1 - alpha) + self._target_levels * alpha

        for i in range(self.bar_count):
            level = self._levels[i]
            bar_h = max(3, level * h * 0.85)

            x = i * (bar_width + gap) + gap
            y_top = (h - bar_h) / 2
            y_bottom = (h + bar_h) / 2

            # Color based on intensity
            if level > 0.7:
                color = t.WAVEFORM_PEAK
            elif level > 0.1:
                color = t.WAVEFORM_ACTIVE
            else:
                color = t.WAVEFORM_IDLE

            self.canvas.create_rectangle(
                x, y_top, x + bar_width, y_bottom,
                fill=color,
                outline="",
            )

        self._animation_id = self.after(33, self._animate_active)

    def set_active(self, active: bool):
        """Switch between idle and active visualization modes."""
        self._is_active = active

        if self._animation_id:
            self.after_cancel(self._animation_id)

        if active:
            self._status_label.configure(
                text="● Recording",
                text_color=self.theme.RECORDING_ACTIVE,
            )
            self._levels = np.zeros(self.bar_count)
            self._target_levels = np.zeros(self.bar_count)
            self._animate_active()
        else:
            self._status_label.configure(
                text="Idle",
                text_color=self.theme.TEXT_TERTIARY,
            )
            self._levels = np.zeros(self.bar_count)
            self._target_levels = np.zeros(self.bar_count)
            self._start_idle_animation()

    def set_processing(self):
        """Show processing state."""
        self._status_label.configure(
            text="⏳ Processing...",
            text_color=self.theme.WARNING,
        )

    def set_complete(self):
        """Show completion state."""
        self._status_label.configure(
            text="✅ Complete",
            text_color=self.theme.SUCCESS,
        )
        self.after(3000, lambda: self._status_label.configure(
            text="Idle", text_color=self.theme.TEXT_TERTIARY
        ))

    def destroy(self):
        """Clean up animation before destroying."""
        if self._animation_id:
            self.after_cancel(self._animation_id)
        super().destroy()
