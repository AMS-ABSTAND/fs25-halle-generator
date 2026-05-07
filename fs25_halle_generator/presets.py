"""Material-Presets für Wand, Dach, Tor und Sockel.

Jedes Preset definiert: (key, Anzeigename, Farbe, Roughness, Metallic, Pattern).
Pattern = Procedural-Shader-Typ für die Vorschau (siehe materials.py).
"""

# Pattern types (drives procedural shader setup in materials.py)
PATTERN_FLAT     = 'FLAT'        # No procedural pattern
PATTERN_TRAPEZ   = 'TRAPEZ'      # Vertical trapez stripes (Wave)
PATTERN_TRAPEZ_H = 'TRAPEZ_H'    # Horizontal trapez stripes
PATTERN_WOOD     = 'WOOD'        # Wood grain (noise + wave)
PATTERN_CONCRETE = 'CONCRETE'    # Subtle noise variation
PATTERN_CLINKER  = 'CLINKER'     # Brick texture
PATTERN_RIFFEL   = 'RIFFEL'      # Diamond/voronoi
PATTERN_STEHFALZ = 'STEHFALZ'    # Wide vertical seams
PATTERN_TILES    = 'TILES'       # Roof tiles (fine brick rows)
PATTERN_PAINT    = 'PAINT'       # Smooth painted surface


# (key, Anzeigename, (R,G,B), Roughness, Metallic, Pattern)
WALL_PRESETS = [
    ('TRAPEZ_RUST',       "Trapezblech Rost",         (0.55, 0.30, 0.18), 0.55, 0.30, PATTERN_TRAPEZ),
    ('TRAPEZ_GREEN',      "Trapezblech Tannengrün",   (0.18, 0.30, 0.20), 0.55, 0.30, PATTERN_TRAPEZ),
    ('TRAPEZ_ANTHRACITE', "Trapezblech Anthrazit",    (0.18, 0.18, 0.20), 0.50, 0.40, PATTERN_TRAPEZ),
    ('TRAPEZ_RED',        "Trapezblech Feuerrot",     (0.65, 0.20, 0.15), 0.55, 0.30, PATTERN_TRAPEZ),
    ('TRAPEZ_WHITE',      "Trapezblech Weiß",         (0.85, 0.85, 0.85), 0.50, 0.30, PATTERN_TRAPEZ),
    ('TRAPEZ_SILVER',     "Trapezblech Silber",       (0.72, 0.72, 0.74), 0.40, 0.55, PATTERN_TRAPEZ),
    ('SANDWICH_WHITE',    "Sandwichpanel Weiß",       (0.92, 0.92, 0.92), 0.40, 0.05, PATTERN_FLAT),
    ('SANDWICH_GREY',     "Sandwichpanel Grau",       (0.55, 0.55, 0.58), 0.40, 0.05, PATTERN_FLAT),
    ('WOOD_LIGHT',        "Holz Hell (Lärche)",       (0.65, 0.45, 0.25), 0.85, 0.0,  PATTERN_WOOD),
    ('WOOD_DARK',         "Holz Dunkel (geölt)",      (0.32, 0.20, 0.10), 0.85, 0.0,  PATTERN_WOOD),
    ('WOOD_BLACK',        "Holz Schwarz (Yakisugi)",  (0.10, 0.08, 0.06), 0.85, 0.0,  PATTERN_WOOD),
    ('WOOD_WEATHERED',    "Holz Verwittert (grau)",   (0.45, 0.40, 0.35), 0.92, 0.0,  PATTERN_WOOD),
    ('CONCRETE',          "Sichtbeton",               (0.55, 0.55, 0.55), 0.85, 0.0,  PATTERN_CONCRETE),
    ('CLINKER_RED',       "Klinker Rot",              (0.55, 0.20, 0.15), 0.85, 0.0,  PATTERN_CLINKER),
    ('CLINKER_DARK',      "Klinker Dunkel",           (0.30, 0.18, 0.15), 0.85, 0.0,  PATTERN_CLINKER),
    ('CHECKER_PLATE',     "Riffelblech (Aluminium)",  (0.55, 0.55, 0.58), 0.30, 0.85, PATTERN_RIFFEL),
]

ROOF_PRESETS = [
    ('TRAPEZ_ANTHRACITE', "Trapezblech Anthrazit",    (0.18, 0.18, 0.20), 0.50, 0.40, PATTERN_TRAPEZ),
    ('TRAPEZ_RED',        "Trapezblech Rot (Klassik)",(0.65, 0.20, 0.15), 0.55, 0.30, PATTERN_TRAPEZ),
    ('TRAPEZ_GREEN',      "Trapezblech Grün",         (0.18, 0.30, 0.20), 0.55, 0.30, PATTERN_TRAPEZ),
    ('TRAPEZ_BROWN',      "Trapezblech Braun",        (0.30, 0.18, 0.10), 0.60, 0.20, PATTERN_TRAPEZ),
    ('STEHFALZ_ZINC',     "Stehfalz Zink",            (0.65, 0.65, 0.68), 0.30, 0.70, PATTERN_STEHFALZ),
    ('STEHFALZ_KUPFER',   "Stehfalz Kupfer (patin.)", (0.30, 0.55, 0.45), 0.40, 0.60, PATTERN_STEHFALZ),
    ('TILES_RED',         "Tonziegel Rot",            (0.55, 0.20, 0.12), 0.85, 0.0,  PATTERN_TILES),
    ('TILES_DARK',        "Tonziegel Engobe Schwarz", (0.20, 0.15, 0.12), 0.85, 0.0,  PATTERN_TILES),
    ('CHECKER_PLATE',     "Riffelblech",              (0.55, 0.55, 0.58), 0.30, 0.85, PATTERN_RIFFEL),
]

DOOR_PRESETS = [
    ('TRAPEZ_WHITE',      "Trapez Weiß",        (0.92, 0.92, 0.92), 0.40, 0.20, PATTERN_TRAPEZ_H),
    ('TRAPEZ_GREEN',      "Trapez Grün",        (0.18, 0.30, 0.20), 0.45, 0.25, PATTERN_TRAPEZ_H),
    ('TRAPEZ_RED',        "Trapez Rot",         (0.65, 0.20, 0.15), 0.45, 0.25, PATTERN_TRAPEZ_H),
    ('TRAPEZ_GREY',       "Trapez Grau",        (0.50, 0.50, 0.52), 0.40, 0.25, PATTERN_TRAPEZ_H),
    ('TRAPEZ_ANTHRACITE', "Trapez Anthrazit",   (0.18, 0.18, 0.20), 0.40, 0.30, PATTERN_TRAPEZ_H),
    ('SANDWICH_WHITE',    "Sandwich Weiß",      (0.95, 0.95, 0.95), 0.30, 0.05, PATTERN_FLAT),
    ('WOOD',              "Holz",               (0.50, 0.32, 0.18), 0.85, 0.0,  PATTERN_WOOD),
    ('CHECKER',           "Riffelblech",        (0.55, 0.55, 0.58), 0.30, 0.85, PATTERN_RIFFEL),
]

PLINTH_PRESETS = [
    ('CONCRETE',     "Beton hellgrau",  (0.55, 0.55, 0.55), 0.90, 0.0,  PATTERN_CONCRETE),
    ('CONCRETE_DK',  "Beton dunkel",    (0.35, 0.35, 0.37), 0.90, 0.0,  PATTERN_CONCRETE),
    ('CLINKER_RED',  "Klinker Rot",     (0.55, 0.20, 0.15), 0.85, 0.0,  PATTERN_CLINKER),
    ('CLINKER_DK',   "Klinker Dunkel",  (0.30, 0.18, 0.15), 0.85, 0.0,  PATTERN_CLINKER),
    ('PAINTED_WHITE',"Gestrichen Weiß", (0.88, 0.88, 0.88), 0.70, 0.0,  PATTERN_PAINT),
    ('PAINTED_GREEN',"Gestrichen Grün", (0.20, 0.35, 0.22), 0.70, 0.0,  PATTERN_PAINT),
    ('CHECKER',      "Riffelblech",     (0.55, 0.55, 0.58), 0.30, 0.85, PATTERN_RIFFEL),
]


def items(preset_list):
    """EnumProperty items list."""
    return [(p[0], p[1], '') for p in preset_list]


def lookup(preset_list, key):
    """Returns (color, roughness, metallic, pattern) for the key.
    Falls back to first preset if key not found."""
    for p in preset_list:
        if p[0] == key:
            return p[2], p[3], p[4], p[5]
    p = preset_list[0]
    return p[2], p[3], p[4], p[5]


def is_trapez_style(preset_list, key):
    """True if this preset's key starts with 'TRAPEZ' — i.e. it's eligible
    for 3D trapez profile geometry."""
    return key.startswith('TRAPEZ')
