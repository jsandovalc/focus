"""JRPG Theme Stylesheet Generator.

This module provides QSS stylesheets for the JRPG-themed UI.
Following Qt/PySide6 best practices for stylesheet management.
"""

from styles.colors import JRPG_COLORS, JRPG_GRADIENTS, JRPG_SIZES, JRPG_PATTERNS


def get_timer_card_style() -> str:
    """Get stylesheet for the main timer card (Battle Arena style) with background pattern."""
    return f"""
    QWidget#timer_card {{
        background-color: {JRPG_COLORS['panel_bg']};
        background-image:
            repeating-linear-gradient(
                0deg,
                rgba(255, 255, 255, 0.02) 0px,
                transparent 2px,
                transparent 4px
            ),
            repeating-linear-gradient(
                90deg,
                rgba(255, 255, 255, 0.02) 0px,
                transparent 2px,
                transparent 4px
            );
        border: {JRPG_SIZES['border_width']}px solid {JRPG_COLORS['panel_border']};
        border-radius: {JRPG_SIZES['border_radius']}px;
    }}
    """


def get_timer_state_indicator_style(state: str = "idle") -> str:
    """Get stylesheet for state indicator based on current state.

    Args:
        state: One of 'idle', 'focusing', 'resting', 'paused', 'overtime'
    """
    state_colors = {
        "idle": JRPG_COLORS['text_disabled'],
        "focusing": JRPG_COLORS['focus_glow'],
        "resting": JRPG_COLORS['rest_normal'],
        "paused": JRPG_COLORS['pause_border'],
        "overtime": JRPG_COLORS['warning'],
    }

    color = state_colors.get(state, JRPG_COLORS['text_disabled'])

    return f"""
    QLabel {{
        font-size: 14px;
        font-weight: 600;
        color: {color};
        background: transparent;
        border: none;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}
    """


def get_timer_display_style() -> str:
    """Get stylesheet for the main timer display - SNES style with shadow."""
    return f"""
    QLabel {{
        font-size: 80px;
        font-weight: 700;
        color: {JRPG_COLORS['text_primary']};
        background: transparent;
        border: none;
        font-family: monospace;
        padding: 10px;
    }}
    """


def get_jrpg_progress_bar_style(bar_type: str = "xp") -> str:
    """Get stylesheet for JRPG-styled progress bars - SNES style with segmentation.

    Args:
        bar_type: One of 'xp', 'hp', 'mp', 'stamina'
    """
    bar_gradients = {
        "xp": JRPG_GRADIENTS['xp_bar'],
        "hp": JRPG_GRADIENTS['hp_bar'],
        "mp": JRPG_GRADIENTS['mp_bar'],
        "stamina": JRPG_GRADIENTS['xp_bar'],  # Same as XP for now
    }

    gradient = bar_gradients.get(bar_type, JRPG_GRADIENTS['xp_bar'])

    # Enhanced with inner shadow for depth
    return f"""
    QProgressBar {{
        border: 4px solid {JRPG_COLORS['panel_border']};
        border-radius: 3px;
        background-color: #1a2850;
        text-align: center;
        height: {JRPG_SIZES['progress_bar_height']}px;
        color: {JRPG_COLORS['text_primary']};
        font-weight: bold;
        font-size: 11px;
    }}

    QProgressBar::chunk {{
        background: {gradient};
        border-radius: 1px;
        margin: 1px;
    }}
    """


def get_focus_button_style() -> str:
    """Get stylesheet for Focus button (Enter Battle) - SNES style."""
    return f"""
    QPushButton {{
        background-color: {JRPG_COLORS['focus_normal']};
        color: {JRPG_COLORS['text_primary']};
        font-size: 16px;
        font-weight: bold;
        border: 3px solid {JRPG_COLORS['panel_border']};
        border-radius: {JRPG_SIZES['button_border_radius']}px;
        padding: 12px 28px;
        min-width: 160px;
        min-height: 45px;
        letter-spacing: 1px;
    }}

    QPushButton:hover {{
        background-color: {JRPG_COLORS['focus_hover']};
        border-color: {JRPG_COLORS['focus_glow']};
    }}

    QPushButton:pressed {{
        background-color: {JRPG_COLORS['focus_pressed']};
        border-color: {JRPG_COLORS['panel_border']};
    }}

    QPushButton:disabled {{
        background-color: {JRPG_COLORS['text_disabled']};
        color: {JRPG_COLORS['panel_bg']};
        border-color: {JRPG_COLORS['panel_border']};
    }}
    """


def get_rest_button_style() -> str:
    """Get stylesheet for Rest button (Visit Inn) - SNES style."""
    return f"""
    QPushButton {{
        background-color: {JRPG_COLORS['rest_normal']};
        color: {JRPG_COLORS['text_primary']};
        font-size: 16px;
        font-weight: bold;
        border: 3px solid {JRPG_COLORS['panel_border']};
        border-radius: {JRPG_SIZES['button_border_radius']}px;
        padding: 12px 28px;
        min-width: 160px;
        min-height: 45px;
        letter-spacing: 1px;
    }}

    QPushButton:hover {{
        background-color: {JRPG_COLORS['rest_hover']};
        border-color: {JRPG_COLORS['rest_glow']};
    }}

    QPushButton:pressed {{
        background-color: {JRPG_COLORS['rest_pressed']};
        border-color: {JRPG_COLORS['panel_border']};
    }}

    QPushButton:disabled {{
        background-color: {JRPG_COLORS['text_disabled']};
        color: {JRPG_COLORS['panel_bg']};
        border-color: {JRPG_COLORS['panel_border']};
    }}
    """


def get_pause_button_style() -> str:
    """Get stylesheet for Pause button - SNES style."""
    return f"""
    QPushButton {{
        background-color: {JRPG_COLORS['pause_bg']};
        color: {JRPG_COLORS['pause_text']};
        font-size: 14px;
        font-weight: bold;
        border: 3px solid {JRPG_COLORS['pause_border']};
        border-radius: {JRPG_SIZES['button_border_radius']}px;
        padding: 10px 20px;
        min-width: 110px;
        min-height: 40px;
    }}

    QPushButton:hover {{
        background-color: {JRPG_COLORS['pause_hover']};
    }}

    QPushButton:pressed {{
        background-color: {JRPG_COLORS['pause_pressed']};
        color: {JRPG_COLORS['text_primary']};
    }}
    """


def get_cancel_button_style() -> str:
    """Get stylesheet for Cancel button - SNES style."""
    return f"""
    QPushButton {{
        background-color: {JRPG_COLORS['cancel_bg']};
        color: {JRPG_COLORS['cancel_text']};
        font-size: 14px;
        font-weight: bold;
        border: 3px solid {JRPG_COLORS['cancel_border']};
        border-radius: {JRPG_SIZES['button_border_radius']}px;
        padding: 10px 20px;
        min-width: 110px;
        min-height: 40px;
    }}

    QPushButton:hover {{
        background-color: {JRPG_COLORS['cancel_hover']};
    }}

    QPushButton:pressed {{
        background-color: {JRPG_COLORS['cancel_pressed']};
        color: {JRPG_COLORS['text_primary']};
    }}
    """


def get_skill_selector_style() -> str:
    """Get stylesheet for skill selection dropdown - SNES style."""
    return f"""
    QComboBox {{
        font-size: 14px;
        padding: 10px 14px;
        border: 3px solid {JRPG_COLORS['panel_border']};
        border-radius: {JRPG_SIZES['button_border_radius']}px;
        background-color: {JRPG_COLORS['panel_inner']};
        color: {JRPG_COLORS['text_primary']};
        min-height: 32px;
        font-weight: 600;
    }}

    QComboBox:hover {{
        border-color: {JRPG_COLORS['gold']};
        background-color: {JRPG_COLORS['panel_accent']};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 6px solid {JRPG_COLORS['text_primary']};
        margin-right: 6px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {JRPG_COLORS['panel_bg']};
        color: {JRPG_COLORS['text_primary']};
        selection-background-color: {JRPG_COLORS['gold']};
        selection-color: {JRPG_COLORS['panel_border']};
        border: 3px solid {JRPG_COLORS['panel_border']};
        font-weight: 600;
    }}
    """


def get_session_stats_style() -> str:
    """Get stylesheet for session statistics panel - SNES style."""
    return f"""
    QWidget#stats_panel {{
        background-color: {JRPG_COLORS['panel_inner']};
        border: 3px solid {JRPG_COLORS['panel_border']};
        border-radius: {JRPG_SIZES['button_border_radius']}px;
    }}
    """


def get_stat_label_style(label_type: str = "title") -> str:
    """Get stylesheet for stat labels with improved typography.

    Args:
        label_type: One of 'title', 'value', 'description'
    """
    if label_type == "title":
        return f"""
        QLabel {{
            font-size: 11px;
            color: {JRPG_COLORS['text_secondary']};
            font-weight: 700;
            background: transparent;
            border: none;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        """
    elif label_type == "value":
        return f"""
        QLabel {{
            font-size: 20px;
            font-weight: 700;
            color: {JRPG_COLORS['text_header']};
            background: transparent;
            border: none;
            font-family: monospace;
        }}
        """
    else:  # description
        return f"""
        QLabel {{
            font-size: 12px;
            color: {JRPG_COLORS['text_secondary']};
            background: transparent;
            border: none;
        }}
        """


def get_divider_style() -> str:
    """Get stylesheet for horizontal dividers."""
    return f"""
    QWidget {{
        background-color: {JRPG_COLORS['panel_border']};
        border: none;
    }}
    """


def get_quick_access_button_style(is_selected: bool = False) -> str:
    """Get stylesheet for quick access skill buttons - SNES style.

    Args:
        is_selected: Whether this is the currently selected skill
    """
    if is_selected:
        return f"""
        QPushButton {{
            background-color: {JRPG_COLORS['gold']};
            color: {JRPG_COLORS['panel_border']};
            font-size: 12px;
            font-weight: bold;
            border: 3px solid {JRPG_COLORS['panel_border']};
            border-radius: 4px;
            padding: 8px 12px;
        }}

        QPushButton:hover {{
            background-color: {JRPG_COLORS['bronze']};
        }}

        QPushButton:pressed {{
            background-color: #b8860b;
        }}
        """
    else:
        return f"""
        QPushButton {{
            background-color: {JRPG_COLORS['panel_inner']};
            color: {JRPG_COLORS['text_primary']};
            font-size: 12px;
            font-weight: 600;
            border: 2px solid {JRPG_COLORS['panel_border']};
            border-radius: 4px;
            padding: 8px 12px;
        }}

        QPushButton:hover {{
            background-color: {JRPG_COLORS['panel_accent']};
            border-color: {JRPG_COLORS['silver']};
        }}

        QPushButton:pressed {{
            background-color: {JRPG_COLORS['panel_bg']};
        }}
        """


def get_section_header_style() -> str:
    """Get stylesheet for section headers with JRPG glow effect."""
    return f"""
    QLabel {{
        font-size: 14px;
        font-weight: 700;
        color: {JRPG_COLORS['gold']};
        background: transparent;
        border: none;
        letter-spacing: 1px;
        padding: 4px 0px;
        text-transform: uppercase;
    }}
    """


def get_corner_decoration_style() -> str:
    """Get stylesheet for decorative corner elements - SNES style."""
    return f"""
    QLabel {{
        font-size: 20px;
        color: {JRPG_COLORS['gold']};
        background: transparent;
        border: none;
        padding: 0px;
        margin: 0px;
    }}
    """


def get_stat_icon_style() -> str:
    """Get stylesheet for stat icons in the session statistics."""
    return f"""
    QLabel {{
        font-size: 16px;
        background: transparent;
        border: none;
        padding: 0px 4px;
    }}
    """
