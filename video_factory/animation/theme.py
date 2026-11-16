"""Identidad visual de los vídeos: los mismos colores que el tema oscuro de PLD (tokens.css)."""

BG = "#101318"
SURFACE = "#171c23"
SURFACE_2 = "#1d242d"
CODE_BG = "#0e1013"
BORDER = "#2b3440"
TEXT = "#e8edf4"
STRONG = "#f7f9fc"
MUTED = "#a8b2c0"
PRIMARY = "#f2b443"
ON_PRIMARY = "#1b1405"
ACCENT = "#3ccb72"
DANGER = "#f87171"
CODE_TEXT = "#e8e6e1"

# Resaltado de sintaxis: tipo de token de Pygments → color.
SYNTAX = {
    "Keyword": "#f4a66a",
    "Name.Builtin": "#7cc4f5",
    "Name.Function": "#7cc4f5",
    "Name.Class": "#f1d98f",
    "Name.Decorator": "#f1d98f",
    "Literal.String": "#9fd6b0",
    "Literal.Number": "#f1d98f",
    "Comment": "#7d8896",
    "Operator": "#a8b2c0",
    "Punctuation": "#a8b2c0",
}

FRAME_WIDTH = 14.222
FRAME_HEIGHT = 8.0
LEFT_EDGE = -6.35
RIGHT_EDGE = 6.35
BODY_TOP = 2.15
BODY_BOTTOM = -3.45

# Cambia si cambia el aspecto de los vídeos: obliga a volver a renderizar los clips en caché.
THEME_VERSION = 1


def syntax_color(token_type) -> str:
    """Color del token, buscando también en sus tipos padre (String.Double → String…)."""
    name = str(token_type).removeprefix("Token.")
    while name:
        if name in SYNTAX:
            return SYNTAX[name]
        name = name.rpartition(".")[0]
    return CODE_TEXT
