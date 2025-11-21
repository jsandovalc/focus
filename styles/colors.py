"""JRPG Color Palette and Theme Configuration - SNES Era Inspired."""

# SNES JRPG Color Palette - Inspired by Final Fantasy VI, Chrono Trigger, Dragon Quest
JRPG_COLORS = {
    # Base UI - Bright SNES-style blues and purples
    "panel_bg": "#2d4a9e",  # Rich royal blue (like FF6 menus)
    "panel_border": "#1a2850",  # Dark blue border (thick SNES borders)
    "panel_accent": "#3b5ca8",  # Lighter blue for secondary panels
    "background": "#4a6bb5",  # Medium blue background
    "panel_inner": "#5a7bc5",  # Even lighter blue for inner sections

    # Text - High contrast SNES style
    "text_primary": "#ffffff",  # Pure white for readability
    "text_secondary": "#e0e8ff",  # Light blue-white
    "text_header": "#fbbf24",  # Bright gold/yellow (SNES gold text)
    "text_disabled": "#8899bb",  # Muted blue-gray

    # Accent colors - Vibrant SNES palette
    "gold": "#fbbf24",  # Bright gold
    "silver": "#e5e7eb",  # Bright silver
    "bronze": "#d97706",  # Bright bronze

    # Status colors - Bright and vibrant like SNES
    "hp_red": "#ef4444",  # Bright red HP bar
    "hp_red_dark": "#dc2626",  # Darker red for gradient
    "mp_blue": "#3b82f6",  # Bright blue MP bar
    "mp_blue_dark": "#2563eb",  # Darker blue for gradient
    "xp_green": "#22c55e",  # Bright green XP (like Chrono Trigger)
    "xp_green_dark": "#16a34a",  # Darker green for gradient
    "warning": "#f59e0b",  # Bright amber warning
    "success": "#10b981",  # Bright emerald success

    # Button states - Bright SNES colors
    "focus_normal": "#22c55e",  # Bright green (Go!)
    "focus_hover": "#16a34a",
    "focus_pressed": "#15803d",
    "focus_glow": "#4ade80",

    # Button states - Rest (Bright blue like SNES inn scenes)
    "rest_normal": "#3b82f6",  # Bright blue
    "rest_hover": "#2563eb",
    "rest_pressed": "#1d4ed8",
    "rest_glow": "#60a5fa",

    # Button states - Pause (Bright yellow)
    "pause_bg": "#fef3c7",
    "pause_text": "#92400e",
    "pause_border": "#f59e0b",
    "pause_hover": "#fde68a",
    "pause_pressed": "#f59e0b",

    # Button states - Cancel (Bright red)
    "cancel_bg": "#fee2e2",
    "cancel_text": "#991b1b",
    "cancel_border": "#ef4444",
    "cancel_hover": "#fecaca",
    "cancel_pressed": "#ef4444",

    # Stat/Element colors - Vibrant SNES palette
    "intellect": "#a78bfa",  # Bright purple
    "willpower": "#fbbf24",  # Bright amber
    "dexterity": "#34d399",  # Bright emerald
    "vitality": "#f87171",  # Bright red
    "charisma": "#f472b6",  # Bright pink
    "strength": "#a8a29e",  # Light stone
    "wisdom": "#22d3ee",  # Bright cyan
}

# Gradient definitions for buttons and panels - SNES style
JRPG_GRADIENTS = {
    # Gold button gradient (bright SNES gold)
    "gold_button": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:0.5 #fcd34d, stop:1 #fbbf24)",
    "gold_button_hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fcd34d, stop:0.5 #fde68a, stop:1 #fcd34d)",
    "gold_button_pressed": "#d97706",

    # Panel header gradient (SNES blue gradient)
    "panel_header": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3b5ca8, stop:0.5 #2d4a9e, stop:1 #1e3a8a)",

    # XP bar - Bright green like Chrono Trigger
    "xp_bar": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #22c55e, stop:0.5 #16a34a, stop:1 #22c55e)",
    "xp_bar_shimmer": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4ade80, stop:0.5 #22c55e, stop:1 #4ade80)",

    # MP bar - Bright blue like FF6
    "mp_bar": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:0.5 #2563eb, stop:1 #3b82f6)",

    # HP bar - Bright red like SNES games
    "hp_bar": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:0.5 #dc2626, stop:1 #ef4444)",
}

# Font configurations
JRPG_FONTS = {
    # Using system fonts that give a JRPG feel without requiring external fonts
    "header": "bold",  # Bold system font for headers
    "body": "",  # Default system font for body
    "numbers": "monospace",  # Monospace for stats/numbers
    "title": "bold",  # Bold for titles
}

# Size configurations - SNES style (thicker borders)
JRPG_SIZES = {
    "border_width": 4,  # Thicker SNES-style borders
    "border_radius": 6,  # Less rounded, more SNES-like
    "button_border_radius": 4,
    "progress_bar_height": 14,  # Chunkier progress bars
    "slim_progress_bar_height": 10,
    "icon_size": 16,
}

# Background patterns - Subtle SNES-style textures
JRPG_PATTERNS = {
    # Subtle diagonal lines pattern (common in SNES menus)
    "diagonal_lines": """
        repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(26, 40, 80, 0.3) 10px,
            rgba(26, 40, 80, 0.3) 20px
        )
    """,
    # Subtle noise/grain texture
    "noise": """
        repeating-linear-gradient(
            0deg,
            rgba(255, 255, 255, 0.03) 0px,
            transparent 2px,
            transparent 4px
        ),
        repeating-linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.03) 0px,
            transparent 2px,
            transparent 4px
        )
    """,
}
