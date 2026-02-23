"""
LinguaFlow — Theme Color System
Premium dark and light themes for the desktop application.
"""


class DarkTheme:
    """Premium dark theme with purple-cyan accents."""

    # ── Background Layers ──
    BG_DARKEST = "#06060f"      # Window background
    BG_PRIMARY = "#0a0a1a"      # Main content background
    BG_SECONDARY = "#10102a"    # Panel backgrounds
    BG_SURFACE = "#161638"      # Cards/elevated surfaces
    BG_ELEVATED = "#1c1c48"     # Hover states, inputs
    BG_HOVER = "#222260"        # Active hover

    # ── Primary Colors ──
    PRIMARY = "#7c6aff"         # Main accent (purple)
    PRIMARY_LIGHT = "#9d8fff"   # Lighter variant
    PRIMARY_DARK = "#5a4adb"    # Darker variant
    PRIMARY_GLOW = "#7c6aff40"  # Glow effect (with alpha)

    # ── Secondary Colors ──
    SECONDARY = "#00d4ff"       # Cyan accent
    SECONDARY_LIGHT = "#4de4ff"
    SECONDARY_DARK = "#00a8cc"
    SECONDARY_GLOW = "#00d4ff30"

    # ── Accent Color ──
    ACCENT = "#ff6b9d"          # Pink accent
    ACCENT_LIGHT = "#ff8eb5"
    ACCENT_DARK = "#d94a7c"

    # ── Semantic Colors ──
    SUCCESS = "#00e676"
    SUCCESS_BG = "#00e67615"
    WARNING = "#ffd740"
    WARNING_BG = "#ffd74015"
    ERROR = "#ff5252"
    ERROR_BG = "#ff525215"
    INFO = "#448aff"
    INFO_BG = "#448aff15"

    # ── Text Colors ──
    TEXT_PRIMARY = "#e8e8f4"
    TEXT_SECONDARY = "#9898c0"
    TEXT_TERTIARY = "#6868a0"
    TEXT_DISABLED = "#484880"
    TEXT_INVERSE = "#0a0a1a"

    # ── Border Colors ──
    BORDER = "#2a2a50"
    BORDER_LIGHT = "#3a3a68"
    BORDER_FOCUS = "#7c6aff"

    # ── Emotion Colors ──
    EMOTION_VERY_NEGATIVE = "#ff4444"
    EMOTION_NEGATIVE = "#ff8844"
    EMOTION_NEUTRAL = "#9898c0"
    EMOTION_POSITIVE = "#44cc88"
    EMOTION_VERY_POSITIVE = "#00e676"
    EMOTION_EXCITED = "#ffaa00"
    EMOTION_ANXIOUS = "#ff8844"
    EMOTION_SAD = "#4488ff"

    # ── Waveform Colors ──
    WAVEFORM_IDLE = "#3a3a68"
    WAVEFORM_ACTIVE = "#7c6aff"
    WAVEFORM_PEAK = "#00d4ff"
    WAVEFORM_BG = "#0a0a1a"

    # ── Button Styles ──
    BUTTON_PRIMARY_BG = "#7c6aff"
    BUTTON_PRIMARY_HOVER = "#9d8fff"
    BUTTON_PRIMARY_TEXT = "#ffffff"
    BUTTON_SECONDARY_BG = "#1c1c48"
    BUTTON_SECONDARY_HOVER = "#2a2a60"
    BUTTON_SECONDARY_TEXT = "#e8e8f4"
    BUTTON_DANGER_BG = "#ff5252"
    BUTTON_DANGER_HOVER = "#ff7070"

    # ── Recording States ──
    RECORDING_IDLE = "#3a3a68"
    RECORDING_ACTIVE = "#ff5252"
    RECORDING_PULSE = "#ff525280"

    # ── Misc ──
    SCROLLBAR = "#2a2a50"
    SCROLLBAR_HOVER = "#3a3a68"
    SHADOW = "#00000060"
    OVERLAY = "#06060fCC"

    # ── Font Configuration ──
    FONT_FAMILY = "Segoe UI"
    FONT_FAMILY_MONO = "Cascadia Code"
    FONT_SIZE_XS = 10
    FONT_SIZE_SM = 11
    FONT_SIZE_MD = 13
    FONT_SIZE_LG = 16
    FONT_SIZE_XL = 20
    FONT_SIZE_2XL = 28
    FONT_SIZE_3XL = 36

    # ── Spacing ──
    PADDING_XS = 4
    PADDING_SM = 8
    PADDING_MD = 16
    PADDING_LG = 24
    PADDING_XL = 32
    CORNER_RADIUS = 12
    CORNER_RADIUS_SM = 8
    CORNER_RADIUS_LG = 16


class LightTheme:
    """Clean light theme with purple-cyan accents."""

    # ── Background Layers ──
    BG_DARKEST = "#e8e8f0"
    BG_PRIMARY = "#f0f0f8"
    BG_SECONDARY = "#f5f5fd"
    BG_SURFACE = "#ffffff"
    BG_ELEVATED = "#ffffff"
    BG_HOVER = "#eeeef8"

    # ── Primary Colors ──
    PRIMARY = "#6c5ce7"
    PRIMARY_LIGHT = "#8b7ff0"
    PRIMARY_DARK = "#5240cc"
    PRIMARY_GLOW = "#6c5ce730"

    # ── Secondary Colors ──
    SECONDARY = "#00b4d8"
    SECONDARY_LIGHT = "#33c7e6"
    SECONDARY_DARK = "#0096b7"
    SECONDARY_GLOW = "#00b4d820"

    # ── Accent Color ──
    ACCENT = "#e84393"
    ACCENT_LIGHT = "#f06baf"
    ACCENT_DARK = "#c02577"

    # ── Semantic Colors ──
    SUCCESS = "#00b894"
    SUCCESS_BG = "#00b89418"
    WARNING = "#fdcb6e"
    WARNING_BG = "#fdcb6e18"
    ERROR = "#e17055"
    ERROR_BG = "#e1705518"
    INFO = "#0984e3"
    INFO_BG = "#0984e318"

    # ── Text Colors ──
    TEXT_PRIMARY = "#2d3436"
    TEXT_SECONDARY = "#636e72"
    TEXT_TERTIARY = "#b2bec3"
    TEXT_DISABLED = "#dfe6e9"
    TEXT_INVERSE = "#ffffff"

    # ── Border Colors ──
    BORDER = "#dfe6e9"
    BORDER_LIGHT = "#edf0f2"
    BORDER_FOCUS = "#6c5ce7"

    # ── Emotion Colors ──
    EMOTION_VERY_NEGATIVE = "#d63031"
    EMOTION_NEGATIVE = "#e17055"
    EMOTION_NEUTRAL = "#636e72"
    EMOTION_POSITIVE = "#00b894"
    EMOTION_VERY_POSITIVE = "#00cec9"
    EMOTION_EXCITED = "#fdcb6e"
    EMOTION_ANXIOUS = "#e17055"
    EMOTION_SAD = "#0984e3"

    # ── Waveform Colors ──
    WAVEFORM_IDLE = "#dfe6e9"
    WAVEFORM_ACTIVE = "#6c5ce7"
    WAVEFORM_PEAK = "#00b4d8"
    WAVEFORM_BG = "#f5f5fd"

    # ── Button Styles ──
    BUTTON_PRIMARY_BG = "#6c5ce7"
    BUTTON_PRIMARY_HOVER = "#8b7ff0"
    BUTTON_PRIMARY_TEXT = "#ffffff"
    BUTTON_SECONDARY_BG = "#f0f0f8"
    BUTTON_SECONDARY_HOVER = "#e8e8f0"
    BUTTON_SECONDARY_TEXT = "#2d3436"
    BUTTON_DANGER_BG = "#e17055"
    BUTTON_DANGER_HOVER = "#f08070"

    # ── Recording States ──
    RECORDING_IDLE = "#dfe6e9"
    RECORDING_ACTIVE = "#d63031"
    RECORDING_PULSE = "#d6303180"

    # ── Misc ──
    SCROLLBAR = "#dfe6e9"
    SCROLLBAR_HOVER = "#b2bec3"
    SHADOW = "#00000020"
    OVERLAY = "#2d3436AA"

    # ── Font Configuration ──
    FONT_FAMILY = "Segoe UI"
    FONT_FAMILY_MONO = "Cascadia Code"
    FONT_SIZE_XS = 10
    FONT_SIZE_SM = 11
    FONT_SIZE_MD = 13
    FONT_SIZE_LG = 16
    FONT_SIZE_XL = 20
    FONT_SIZE_2XL = 28
    FONT_SIZE_3XL = 36

    # ── Spacing ──
    PADDING_XS = 4
    PADDING_SM = 8
    PADDING_MD = 16
    PADDING_LG = 24
    PADDING_XL = 32
    CORNER_RADIUS = 12
    CORNER_RADIUS_SM = 8
    CORNER_RADIUS_LG = 16
