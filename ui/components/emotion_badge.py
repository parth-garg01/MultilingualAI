"""
LinguaFlow — Emotion Badge Component
Color-coded emotion indicator with emoji and label.
"""

import customtkinter as ctk
from typing import Optional


class EmotionBadge(ctk.CTkFrame):
    """
    Displays the detected emotion with an emoji, label,
    color-coded badge, and audio feature details.
    """

    def __init__(self, parent, theme, **kwargs):
        super().__init__(
            parent,
            fg_color=theme.BG_SECONDARY,
            corner_radius=theme.CORNER_RADIUS,
            **kwargs,
        )

        self.theme = theme
        self._build_ui()

    def _build_ui(self):
        t = self.theme

        # ── Header ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=t.PADDING_MD, pady=(t.PADDING_SM, 0))

        ctk.CTkLabel(
            header,
            text="🎭 EMOTION",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS, "bold"),
            text_color=t.TEXT_TERTIARY,
        ).pack(side="left")

        # ── Main Emotion Display ──
        emotion_frame = ctk.CTkFrame(self, fg_color="transparent")
        emotion_frame.pack(fill="x", padx=t.PADDING_MD, pady=t.PADDING_SM)

        # Emoji (large)
        self.emoji_label = ctk.CTkLabel(
            emotion_frame,
            text="😐",
            font=(t.FONT_FAMILY, 36),
            text_color=t.TEXT_PRIMARY,
        )
        self.emoji_label.pack(side="left", padx=(0, t.PADDING_SM))

        # Text info
        text_frame = ctk.CTkFrame(emotion_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)

        self.label = ctk.CTkLabel(
            text_frame,
            text="Neutral",
            font=(t.FONT_FAMILY, t.FONT_SIZE_MD, "bold"),
            text_color=t.EMOTION_NEUTRAL,
        )
        self.label.pack(anchor="w")

        self.description = ctk.CTkLabel(
            text_frame,
            text="Waiting for input...",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS),
            text_color=t.TEXT_TERTIARY,
        )
        self.description.pack(anchor="w")

        # Confidence bar
        self.confidence_bar = ctk.CTkProgressBar(
            text_frame,
            width=140,
            height=6,
            fg_color=t.BG_SURFACE,
            progress_color=t.EMOTION_NEUTRAL,
            corner_radius=3,
        )
        self.confidence_bar.pack(anchor="w", pady=(4, 0))
        self.confidence_bar.set(0.5)

        # ── Audio Features ──
        features_frame = ctk.CTkFrame(
            self,
            fg_color=t.BG_SURFACE,
            corner_radius=t.CORNER_RADIUS_SM,
        )
        features_frame.pack(
            fill="x",
            padx=t.PADDING_MD,
            pady=(0, t.PADDING_SM),
        )

        features_grid = ctk.CTkFrame(features_frame, fg_color="transparent")
        features_grid.pack(fill="x", padx=t.PADDING_SM, pady=t.PADDING_SM)

        # Feature indicators
        self.pitch_label = self._create_feature(
            features_grid, "🎵 Pitch", "--", 0
        )
        self.energy_label = self._create_feature(
            features_grid, "⚡ Energy", "--", 1
        )
        self.speed_label = self._create_feature(
            features_grid, "🏃 Speed", "--", 2
        )

    def _create_feature(
        self, parent, icon_text: str, value: str, column: int
    ) -> ctk.CTkLabel:
        """Create a single audio feature indicator."""
        t = self.theme

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", expand=True, fill="x", padx=2)

        ctk.CTkLabel(
            frame,
            text=icon_text,
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS),
            text_color=t.TEXT_TERTIARY,
        ).pack(anchor="center")

        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=(t.FONT_FAMILY, t.FONT_SIZE_SM, "bold"),
            text_color=t.TEXT_SECONDARY,
        )
        value_label.pack(anchor="center")

        return value_label

    def update_emotion(self, emotion_data: dict):
        """
        Update the emotion display.

        Args:
            emotion_data: Dict from EmotionAnalyzer with keys:
                - text_emotion: {label, emoji, color, score, description}
                - audio_features: {avg_pitch, avg_energy, speech_rate, ...}
                - primary_label, primary_emoji, primary_color
        """
        t = self.theme

        # Extract data
        text_emotion = emotion_data.get("text_emotion", {})
        audio_features = emotion_data.get("audio_features", {})
        primary_emoji = emotion_data.get("primary_emoji", "😐")
        primary_label = emotion_data.get("primary_label", "Neutral")
        primary_color = emotion_data.get("primary_color", t.EMOTION_NEUTRAL)

        # Update emoji
        self.emoji_label.configure(text=primary_emoji)

        # Update label
        self.label.configure(
            text=primary_label,
            text_color=primary_color,
        )

        # Update description
        desc = text_emotion.get("description", "")
        audio_label = audio_features.get("audio_emotion", "")
        if audio_label and audio_label != primary_label:
            desc += f" (Voice: {audio_label})"
        self.description.configure(text=desc or primary_label)

        # Update confidence bar
        score = text_emotion.get("score", 0.5)
        self.confidence_bar.set(score)
        self.confidence_bar.configure(progress_color=primary_color)

        # Update audio features
        avg_pitch = audio_features.get("avg_pitch", 0)
        avg_energy = audio_features.get("avg_energy", 0)
        speech_rate = audio_features.get("speech_rate", 0)

        # Classify pitch
        if avg_pitch > 250:
            pitch_text = "High"
        elif avg_pitch > 150:
            pitch_text = "Normal"
        elif avg_pitch > 0:
            pitch_text = "Low"
        else:
            pitch_text = "--"

        # Classify energy
        if avg_energy > 0.08:
            energy_text = "High"
        elif avg_energy > 0.03:
            energy_text = "Normal"
        elif avg_energy > 0:
            energy_text = "Low"
        else:
            energy_text = "--"

        # Classify speed
        if speech_rate > 5:
            speed_text = "Fast"
        elif speech_rate > 2:
            speed_text = "Normal"
        elif speech_rate > 0:
            speed_text = "Slow"
        else:
            speed_text = "--"

        self.pitch_label.configure(text=pitch_text)
        self.energy_label.configure(text=energy_text)
        self.speed_label.configure(text=speed_text)

    def reset(self):
        """Reset to default state."""
        t = self.theme
        self.emoji_label.configure(text="😐")
        self.label.configure(text="Neutral", text_color=t.EMOTION_NEUTRAL)
        self.description.configure(text="Waiting for input...")
        self.confidence_bar.set(0.5)
        self.confidence_bar.configure(progress_color=t.EMOTION_NEUTRAL)
        self.pitch_label.configure(text="--")
        self.energy_label.configure(text="--")
        self.speed_label.configure(text="--")
