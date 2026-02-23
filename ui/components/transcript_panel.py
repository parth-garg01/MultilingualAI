"""
LinguaFlow — Transcript Panel Component
Displays original and translated text with typing animation.
"""

import customtkinter as ctk
from typing import Optional


class TranscriptPanel(ctk.CTkFrame):
    """
    Dual-panel transcript display showing original text
    and its translation side by side.
    """

    def __init__(self, parent, theme, **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs,
        )

        self.theme = theme
        self._typing_animations = {}

        self._build_ui()

    def _build_ui(self):
        t = self.theme

        # Grid layout: two equal columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Source Panel ──
        self.source_panel = self._create_panel(
            column=0,
            title="📝 ORIGINAL TEXT",
            placeholder="Speak something to see the transcription...",
            accent_color=t.PRIMARY,
        )

        # ── Target Panel ──
        self.target_panel = self._create_panel(
            column=1,
            title="🌐 TRANSLATED TEXT",
            placeholder="Translation will appear here...",
            accent_color=t.SECONDARY,
        )

    def _create_panel(
        self,
        column: int,
        title: str,
        placeholder: str,
        accent_color: str,
    ) -> dict:
        """Create a single transcript panel."""
        t = self.theme
        padx = (0, t.PADDING_SM) if column == 0 else (t.PADDING_SM, 0)

        frame = ctk.CTkFrame(
            self,
            fg_color=t.BG_SECONDARY,
            corner_radius=t.CORNER_RADIUS,
            border_width=1,
            border_color=t.BORDER,
        )
        frame.grid(
            row=0, column=column,
            sticky="nsew",
            padx=padx,
        )
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # ── Header ──
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=t.PADDING_MD, pady=(t.PADDING_SM, 0))

        # Accent bar
        accent = ctk.CTkFrame(
            header,
            fg_color=accent_color,
            width=3,
            height=16,
            corner_radius=2,
        )
        accent.pack(side="left", padx=(0, 8))

        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS, "bold"),
            text_color=t.TEXT_TERTIARY,
        )
        title_label.pack(side="left")

        # Language badge
        lang_badge = ctk.CTkLabel(
            header,
            text="",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS),
            text_color=accent_color,
            fg_color=t.BG_SURFACE,
            corner_radius=4,
            padx=8,
            pady=2,
        )
        lang_badge.pack(side="right")

        # ── Text Area ──
        textbox = ctk.CTkTextbox(
            frame,
            font=(t.FONT_FAMILY, t.FONT_SIZE_LG),
            text_color=t.TEXT_PRIMARY,
            fg_color=t.BG_SURFACE,
            corner_radius=t.CORNER_RADIUS_SM,
            border_width=0,
            wrap="word",
            state="disabled",
            activate_scrollbars=True,
        )
        textbox.grid(
            row=1, column=0,
            sticky="nsew",
            padx=t.PADDING_MD,
            pady=t.PADDING_SM,
        )

        # Show placeholder
        textbox.configure(state="normal")
        textbox.insert("1.0", placeholder)
        textbox.configure(text_color=t.TEXT_TERTIARY, state="disabled")

        # ── Info Bar ──
        info_bar = ctk.CTkFrame(frame, fg_color="transparent", height=24)
        info_bar.grid(
            row=2, column=0,
            sticky="ew",
            padx=t.PADDING_MD,
            pady=(0, t.PADDING_SM),
        )

        char_count = ctk.CTkLabel(
            info_bar,
            text="0 characters",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS),
            text_color=t.TEXT_TERTIARY,
        )
        char_count.pack(side="left")

        confidence_label = ctk.CTkLabel(
            info_bar,
            text="",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS),
            text_color=t.TEXT_TERTIARY,
        )
        confidence_label.pack(side="right")

        return {
            "frame": frame,
            "textbox": textbox,
            "lang_badge": lang_badge,
            "char_count": char_count,
            "confidence_label": confidence_label,
            "placeholder": placeholder,
        }

    def set_source_text(
        self,
        text: str,
        language: str = "",
        confidence: float = 0.0,
        animate: bool = True,
    ):
        """Set the source (original) transcript text."""
        self._set_panel_text(
            self.source_panel,
            text,
            language,
            confidence,
            animate,
            "source",
        )

    def set_target_text(
        self,
        text: str,
        language: str = "",
        animate: bool = True,
    ):
        """Set the target (translated) transcript text."""
        self._set_panel_text(
            self.target_panel,
            text,
            language,
            0,
            animate,
            "target",
        )

    def _set_panel_text(
        self,
        panel: dict,
        text: str,
        language: str,
        confidence: float,
        animate: bool,
        panel_id: str,
    ):
        """Set text in a panel with optional typing animation."""
        t = self.theme

        # Cancel any existing animation
        if panel_id in self._typing_animations:
            anim_id = self._typing_animations.pop(panel_id)
            self.after_cancel(anim_id)

        # Update language badge
        if language:
            panel["lang_badge"].configure(text=f" {language} ")

        # Update confidence
        if confidence > 0:
            panel["confidence_label"].configure(
                text=f"Confidence: {confidence:.0%}"
            )

        textbox = panel["textbox"]

        if animate and text:
            # Typing animation
            textbox.configure(state="normal", text_color=t.TEXT_PRIMARY)
            textbox.delete("1.0", "end")
            self._animate_typing(textbox, text, 0, panel, panel_id)
        else:
            textbox.configure(state="normal", text_color=t.TEXT_PRIMARY)
            textbox.delete("1.0", "end")
            if text:
                textbox.insert("1.0", text)
                panel["char_count"].configure(text=f"{len(text)} characters")
            else:
                textbox.insert("1.0", panel["placeholder"])
                textbox.configure(text_color=t.TEXT_TERTIARY)
                panel["char_count"].configure(text="0 characters")
            textbox.configure(state="disabled")

    def _animate_typing(
        self,
        textbox: ctk.CTkTextbox,
        text: str,
        index: int,
        panel: dict,
        panel_id: str,
    ):
        """Animate text appearing character by character."""
        if index < len(text):
            textbox.insert("end", text[index])
            textbox.see("end")
            panel["char_count"].configure(text=f"{index + 1} characters")

            # Variable speed: faster for spaces, slower for punctuation
            char = text[index]
            delay = 15  # Base delay in ms
            if char in ".!?":
                delay = 80
            elif char in ",;:":
                delay = 40
            elif char == " ":
                delay = 10

            anim_id = self.after(
                delay,
                self._animate_typing,
                textbox, text, index + 1, panel, panel_id,
            )
            self._typing_animations[panel_id] = anim_id
        else:
            textbox.configure(state="disabled")
            if panel_id in self._typing_animations:
                del self._typing_animations[panel_id]

    def clear(self):
        """Clear both panels."""
        t = self.theme
        for panel in [self.source_panel, self.target_panel]:
            tb = panel["textbox"]
            tb.configure(state="normal", text_color=t.TEXT_TERTIARY)
            tb.delete("1.0", "end")
            tb.insert("1.0", panel["placeholder"])
            tb.configure(state="disabled")
            panel["char_count"].configure(text="0 characters")
            panel["confidence_label"].configure(text="")
            panel["lang_badge"].configure(text="")

    def set_source_loading(self):
        """Show loading state on source panel."""
        self._set_loading(self.source_panel, "Transcribing...")

    def set_target_loading(self):
        """Show loading state on target panel."""
        self._set_loading(self.target_panel, "Translating...")

    def _set_loading(self, panel: dict, message: str):
        t = self.theme
        tb = panel["textbox"]
        tb.configure(state="normal", text_color=t.TEXT_TERTIARY)
        tb.delete("1.0", "end")
        tb.insert("1.0", f"⏳ {message}")
        tb.configure(state="disabled")
