"""
LinguaFlow — Language Selector Component
Styled dropdown for selecting source/target languages with a swap button.
"""

import customtkinter as ctk
from typing import Callable, Optional


class LanguageSelector(ctk.CTkFrame):
    """
    Language selection panel with source/target dropdowns and swap button.
    """

    def __init__(
        self,
        parent,
        theme,
        languages: list,
        default_source: str = "English",
        default_target: str = "Hindi",
        on_change: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(
            parent,
            fg_color=theme.BG_SECONDARY,
            corner_radius=theme.CORNER_RADIUS,
            **kwargs,
        )

        self.theme = theme
        self.languages = languages
        self.on_change = on_change

        self._build_ui(default_source, default_target)

    def _build_ui(self, default_source: str, default_target: str):
        t = self.theme

        # ── Container ──
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=t.PADDING_MD, pady=t.PADDING_SM)

        # ── Source Language ──
        source_frame = ctk.CTkFrame(container, fg_color="transparent")
        source_frame.pack(side="left", expand=True, fill="x")

        ctk.CTkLabel(
            source_frame,
            text="FROM",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS, "bold"),
            text_color=t.TEXT_TERTIARY,
        ).pack(anchor="w", padx=4)

        self.source_var = ctk.StringVar(value=default_source)
        self.source_dropdown = ctk.CTkComboBox(
            source_frame,
            values=self.languages,
            variable=self.source_var,
            command=self._on_source_change,
            width=200,
            height=34,
            font=(t.FONT_FAMILY, t.FONT_SIZE_MD),
            dropdown_font=(t.FONT_FAMILY, t.FONT_SIZE_MD),
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
        self.source_dropdown.pack(anchor="w", pady=(4, 0))

        # ── Swap Button ──
        swap_frame = ctk.CTkFrame(container, fg_color="transparent", width=80)
        swap_frame.pack(side="left", padx=t.PADDING_MD)
        swap_frame.pack_propagate(False)

        self.swap_btn = ctk.CTkButton(
            swap_frame,
            text="⟷",
            width=50,
            height=34,
            font=(t.FONT_FAMILY, t.FONT_SIZE_XL, "bold"),
            fg_color=t.BG_SURFACE,
            hover_color=t.BG_HOVER,
            text_color=t.SECONDARY,
            corner_radius=t.CORNER_RADIUS_SM,
            border_width=1,
            border_color=t.BORDER,
            command=self._swap_languages,
        )
        self.swap_btn.pack(expand=True)

        # ── Target Language ──
        target_frame = ctk.CTkFrame(container, fg_color="transparent")
        target_frame.pack(side="left", expand=True, fill="x")

        ctk.CTkLabel(
            target_frame,
            text="TO",
            font=(t.FONT_FAMILY, t.FONT_SIZE_XS, "bold"),
            text_color=t.TEXT_TERTIARY,
        ).pack(anchor="w", padx=4)

        self.target_var = ctk.StringVar(value=default_target)
        self.target_dropdown = ctk.CTkComboBox(
            target_frame,
            values=self.languages,
            variable=self.target_var,
            command=self._on_target_change,
            width=200,
            height=34,
            font=(t.FONT_FAMILY, t.FONT_SIZE_MD),
            dropdown_font=(t.FONT_FAMILY, t.FONT_SIZE_MD),
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
        self.target_dropdown.pack(anchor="w", pady=(4, 0))

    def _on_source_change(self, value: str):
        if self.on_change:
            self.on_change(self.source_var.get(), self.target_var.get())

    def _on_target_change(self, value: str):
        if self.on_change:
            self.on_change(self.source_var.get(), self.target_var.get())

    def _swap_languages(self):
        src = self.source_var.get()
        tgt = self.target_var.get()
        self.source_var.set(tgt)
        self.target_var.set(src)
        if self.on_change:
            self.on_change(tgt, src)

    @property
    def source_language(self) -> str:
        return self.source_var.get()

    @property
    def target_language(self) -> str:
        return self.target_var.get()
