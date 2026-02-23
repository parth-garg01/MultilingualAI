"""
LinguaFlow — Control Bar Component
Speak button, playback controls, and idiom display.
"""

import customtkinter as ctk
from typing import Optional, Callable


class ControlBar(ctk.CTkFrame):
    """
    Main control bar with speak button, playback controls,
    and idiom mapping display.
    """

    def __init__(
        self,
        parent,
        theme,
        on_speak: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
        on_play: Optional[Callable] = None,
        on_clear: Optional[Callable] = None,
        compact: bool = False,
        **kwargs,
    ):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs,
        )

        self.theme = theme
        self._on_speak = on_speak
        self._on_stop = on_stop
        self._on_play = on_play
        self._on_clear = on_clear
        self._is_recording = False
        self._pulse_animation_id = None
        self._compact = compact

        self._build_ui()

    def _build_ui(self):
        t = self.theme

        if self._compact:
            self._build_compact_ui()
        else:
            self._build_full_ui()

        # ── Idiom Display (shared) ──
        self.idiom_frame = ctk.CTkFrame(
            self,
            fg_color=t.BG_SECONDARY,
            corner_radius=t.CORNER_RADIUS_SM,
            border_width=1,
            border_color=t.BORDER,
        )
        # Hidden by default
        self.idiom_frame.pack_forget()

        self.idiom_header = ctk.CTkLabel(
            self.idiom_frame,
            text="📖 IDIOM DETECTED",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS, "bold"),
            text_color=t.ACCENT,
        )
        self.idiom_header.pack(anchor="w", padx=t.PADDING_MD, pady=(t.PADDING_SM, 0))

        self.idiom_content = ctk.CTkLabel(
            self.idiom_frame,
            text="",
            font=(t.FONT_FAMILY, t.FONT_SIZE_SM),
            text_color=t.TEXT_SECONDARY,
            wraplength=600,
            justify="left",
        )
        self.idiom_content.pack(
            anchor="w",
            padx=t.PADDING_MD,
            pady=(4, t.PADDING_SM),
        )

    def _build_full_ui(self):
        """Horizontal layout — used when control bar spans full width."""
        t = self.theme

        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", pady=t.PADDING_SM)

        left = ctk.CTkFrame(controls, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        self.clear_btn = ctk.CTkButton(
            left, text="🗑  Clear", width=100, height=38,
            font=(t.FONT_FAMILY, t.FONT_SIZE_SM),
            fg_color=t.BUTTON_SECONDARY_BG, hover_color=t.BUTTON_SECONDARY_HOVER,
            text_color=t.BUTTON_SECONDARY_TEXT, corner_radius=t.CORNER_RADIUS_SM,
            border_width=1, border_color=t.BORDER, command=self._handle_clear,
        )
        self.clear_btn.pack(side="left")

        center = ctk.CTkFrame(controls, fg_color="transparent")
        center.pack(side="left", padx=t.PADDING_LG)

        self.speak_btn = ctk.CTkButton(
            center, text="  🎤  SPEAK  ", width=200, height=56,
            font=(t.FONT_FAMILY, t.FONT_SIZE_LG, "bold"),
            fg_color=t.BUTTON_PRIMARY_BG, hover_color=t.BUTTON_PRIMARY_HOVER,
            text_color=t.BUTTON_PRIMARY_TEXT, corner_radius=28,
            command=self._handle_speak_toggle,
        )
        self.speak_btn.pack()

        right = ctk.CTkFrame(controls, fg_color="transparent")
        right.pack(side="right", fill="x", expand=True)

        self.play_btn = ctk.CTkButton(
            right, text="▶  Play Translation", width=160, height=38,
            font=(t.FONT_FAMILY, t.FONT_SIZE_SM),
            fg_color=t.BUTTON_SECONDARY_BG, hover_color=t.BUTTON_SECONDARY_HOVER,
            text_color=t.SECONDARY, corner_radius=t.CORNER_RADIUS_SM,
            border_width=1, border_color=t.BORDER,
            command=self._handle_play, state="disabled",
        )
        self.play_btn.pack(side="right")

    def _build_compact_ui(self):
        """Compact vertical layout — SPEAK top, Play+Clear below."""
        t = self.theme

        self.speak_btn = ctk.CTkButton(
            self, text="🎤  SPEAK", height=60,
            font=(t.FONT_FAMILY, t.FONT_SIZE_LG, "bold"),
            fg_color=t.BUTTON_PRIMARY_BG, hover_color=t.BUTTON_PRIMARY_HOVER,
            text_color=t.BUTTON_PRIMARY_TEXT, corner_radius=t.CORNER_RADIUS,
            command=self._handle_speak_toggle,
        )
        self.speak_btn.pack(fill="x", pady=(0, 6))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x")

        self.play_btn = ctk.CTkButton(
            row, text="▶ Play", height=34,
            font=(t.FONT_FAMILY, t.FONT_SIZE_SM),
            fg_color=t.BUTTON_SECONDARY_BG, hover_color=t.BUTTON_SECONDARY_HOVER,
            text_color=t.SECONDARY, corner_radius=t.CORNER_RADIUS_SM,
            border_width=1, border_color=t.BORDER,
            command=self._handle_play, state="disabled",
        )
        self.play_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.clear_btn = ctk.CTkButton(
            row, text="🗑 Clear", height=34,
            font=(t.FONT_FAMILY, t.FONT_SIZE_SM),
            fg_color=t.BUTTON_SECONDARY_BG, hover_color=t.BUTTON_SECONDARY_HOVER,
            text_color=t.BUTTON_SECONDARY_TEXT, corner_radius=t.CORNER_RADIUS_SM,
            border_width=1, border_color=t.BORDER, command=self._handle_clear,
        )
        self.clear_btn.pack(side="right", fill="x", expand=True, padx=(4, 0))

    def _handle_speak_toggle(self):
        """Toggle recording on/off."""
        if self._is_recording:
            self.set_idle()
            if self._on_stop:
                self._on_stop()
        else:
            self.set_recording()
            if self._on_speak:
                self._on_speak()

    def _handle_play(self):
        if self._on_play:
            self._on_play()

    def _handle_clear(self):
        if self._on_clear:
            self._on_clear()
        self.hide_idioms()

    def set_recording(self):
        """Switch to recording state."""
        t = self.theme
        self._is_recording = True

        self.speak_btn.configure(
            text="⏹  STOP" if self._compact else "  ⏹  STOP  ",
            fg_color=t.RECORDING_ACTIVE,
            hover_color="#ff7070",
        )
        self._start_pulse()

    def set_idle(self):
        """Switch to idle state."""
        t = self.theme
        self._is_recording = False

        self.speak_btn.configure(
            text="🎤  SPEAK" if self._compact else "  🎤  SPEAK  ",
            fg_color=t.BUTTON_PRIMARY_BG,
            hover_color=t.BUTTON_PRIMARY_HOVER,
        )
        self._stop_pulse()

    def set_processing(self):
        """Switch to processing state."""
        t = self.theme
        self._is_recording = False

        self.speak_btn.configure(
            text="⏳ Processing..." if self._compact else "  ⏳  Processing...  ",
            fg_color=t.BG_ELEVATED,
            hover_color=t.BG_ELEVATED,
            state="disabled",
        )
        self._stop_pulse()

    def set_complete(self):
        """Switch to complete state (with play enabled)."""
        t = self.theme
        self.speak_btn.configure(state="normal")
        self.set_idle()
        self.play_btn.configure(state="normal")

    def enable_play(self):
        """Enable the play button."""
        self.play_btn.configure(state="normal")

    def disable_play(self):
        """Disable the play button."""
        self.play_btn.configure(state="disabled")

    def show_idioms(self, idioms: list):
        """Display detected idiom mappings."""
        if not idioms:
            return

        t = self.theme
        lines = []
        for idiom in idioms:
            lines.append(
                f'"{idiom["original"]}" → "{idiom["translated"]}"\n'
                f'   💡 {idiom.get("meaning", "")}'
            )

        self.idiom_content.configure(text="\n".join(lines))
        self.idiom_frame.pack(
            fill="x",
            pady=(t.PADDING_SM, 0),
        )

    def hide_idioms(self):
        """Hide the idiom display."""
        self.idiom_frame.pack_forget()

    def _start_pulse(self):
        """Start recording pulse animation."""
        self._pulse_step = 0
        self._animate_pulse()

    def _stop_pulse(self):
        """Stop recording pulse animation."""
        if self._pulse_animation_id:
            self.after_cancel(self._pulse_animation_id)
            self._pulse_animation_id = None

    def _animate_pulse(self):
        """Animate the speak button pulsing while recording."""
        if not self._is_recording:
            return

        import math

        self._pulse_step += 1
        # Pulsing opacity effect via alternating colors
        phase = math.sin(self._pulse_step * 0.15)

        if phase > 0:
            color = "#ff5252"
        else:
            color = "#cc3333"

        self.speak_btn.configure(fg_color=color)
        self._pulse_animation_id = self.after(50, self._animate_pulse)

    def destroy(self):
        """Clean up animations."""
        self._stop_pulse()
        super().destroy()
