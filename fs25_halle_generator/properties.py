"""HALLE_PG_settings — alle PropertyGroup-Eigenschaften."""

from bpy.props import (
    FloatProperty, IntProperty, BoolProperty, EnumProperty, StringProperty,
)
from bpy.types import PropertyGroup

from . import presets


class HALLE_PG_settings(PropertyGroup):
    # --- Identifikation ---
    base_name: StringProperty(name="Basisname", default="Maschinenhalle")
    collection_name: StringProperty(name="Collection", default="Halle")

    # --- UI-Sektionen (collapsible) ---
    show_dimensions: BoolProperty(default=True)
    show_roof:       BoolProperty(default=True)
    show_floor:      BoolProperty(default=False)
    show_doors:      BoolProperty(default=True)
    show_windows:    BoolProperty(default=False)
    show_columns:    BoolProperty(default=False)
    show_details:    BoolProperty(default=False)
    show_style:      BoolProperty(default=True)
    show_export:     BoolProperty(default=False)

    # --- Hauptmaße ---
    width:          FloatProperty(name="Breite (X)",   default=20.0, min=4.0, max=80.0, soft_max=50.0, unit='LENGTH')
    depth:          FloatProperty(name="Tiefe (Y)",    default=15.0, min=4.0, max=60.0, soft_max=40.0, unit='LENGTH')
    wall_height:    FloatProperty(name="Wandhöhe",    default=5.0, min=2.5, max=12.0, unit='LENGTH')
    wall_thickness: FloatProperty(name="Wandstärke",  default=0.25, min=0.05, max=0.6, unit='LENGTH')

    # --- Dach ---
    roof_type: EnumProperty(name="Dachtyp", items=[
        ('GABLE', "Satteldach", "First entlang Y"),
        ('FLAT',  "Flachdach",  "Horizontales Dach"),
        ('SHED',  "Pultdach",   "Einseitig geneigt (Schleppdach)"),
    ], default='GABLE')
    shed_high_side: EnumProperty(name="Hoch-Seite", items=[
        ('FRONT', "Vorne (-Y)", ""),
        ('BACK',  "Hinten (+Y)", ""),
        ('LEFT',  "Links (-X)", ""),
        ('RIGHT', "Rechts (+X)", ""),
    ], default='BACK')
    roof_pitch_deg:      FloatProperty(name="Dachneigung (°)", default=22.0, min=0.0, max=45.0)
    roof_overhang_eaves: FloatProperty(name="Traufüberstand", default=0.5, min=0.0, max=2.0, unit='LENGTH')
    roof_overhang_gable: FloatProperty(name="Giebelüberstand", default=0.4, min=0.0, max=2.0, unit='LENGTH')
    roof_thickness:      FloatProperty(name="Dachdicke", default=0.15, min=0.05, max=0.4, unit='LENGTH')
    create_ridge_cap:    BoolProperty(name="Firstziegel", default=True)
    create_gutters:      BoolProperty(name="Dachrinnen", default=True)
    gutter_size:         FloatProperty(name="Rinnen-Durchmesser", default=0.12, min=0.05, max=0.30, unit='LENGTH')

    # --- Boden ---
    create_floor:    BoolProperty(name="Bodenplatte", default=True)
    floor_thickness: FloatProperty(name="Bodendicke", default=0.2, min=0.05, max=0.5, unit='LENGTH')
    floor_extend:    FloatProperty(name="Boden-Überstand", default=0.3, min=0.0, max=2.0, unit='LENGTH')

    # --- Sockel ---
    create_plinth: BoolProperty(name="Betonsockel", default=True)
    plinth_height: FloatProperty(name="Sockelhöhe", default=0.4, min=0.0, max=1.5, unit='LENGTH')
    plinth_offset: FloatProperty(name="Sockel-Überstand", default=0.05, min=0.0, max=0.3, unit='LENGTH')

    # --- Tore ---
    door_front_count: IntProperty(name="Vorne (-Y)",   default=2, min=0, max=8)
    door_back_count:  IntProperty(name="Hinten (+Y)",  default=0, min=0, max=8)
    door_left_count:  IntProperty(name="Links (-X)",   default=0, min=0, max=8)
    door_right_count: IntProperty(name="Rechts (+X)",  default=0, min=0, max=8)
    door_width:       FloatProperty(name="Torbreite",  default=4.5, min=2.0, max=8.0, unit='LENGTH')
    door_height:      FloatProperty(name="Torhöhe",   default=4.5, min=2.0, max=8.0, unit='LENGTH')
    door_sectional:   BoolProperty(name="Sektionaltor", default=True,
                                   description="Tor als horizontale Lamellen mit eigenen Origins")
    door_panel_count: IntProperty(name="Lamellen", default=5, min=2, max=8)
    door_panel_gap:   FloatProperty(name="Lamellen-Spalt", default=0.015, min=0.0, max=0.05, unit='LENGTH')

    # --- Fenster ---
    window_front: BoolProperty(name="Vorne", default=True)
    window_back:  BoolProperty(name="Hinten", default=True)
    window_left:  BoolProperty(name="Links",  default=True)
    window_right: BoolProperty(name="Rechts", default=True)
    window_z:      FloatProperty(name="Höhe Unterkante", default=3.5, min=0.5, max=10.0, unit='LENGTH')
    window_height: FloatProperty(name="Lichtbandhöhe", default=1.0, min=0.3, max=3.0, unit='LENGTH')
    window_margin: FloatProperty(name="Rand-Abstand", default=0.8, min=0.0, max=3.0, unit='LENGTH')

    # --- Stützen ---
    create_columns: BoolProperty(name="Innenstützen", default=False)
    column_count:   IntProperty(name="Anzahl", default=3, min=1, max=10)
    column_size:    FloatProperty(name="Querschnitt", default=0.3, min=0.15, max=0.6, unit='LENGTH')

    # --- Innendetails ---
    detail_workbench:        BoolProperty(name="Werkbank", default=False)
    detail_tool_wall:        BoolProperty(name="Werkzeugwand", default=False)
    detail_diesel_tank:      BoolProperty(name="Hofdiesel-Tank", default=False)
    detail_compressor:       BoolProperty(name="Druckluft-Kompressor", default=False)
    detail_fire_extinguisher:BoolProperty(name="Feuerlöscher", default=False)

    # --- Stil-Presets ---
    wall_same_for_all: BoolProperty(
        name="Wandstil global", default=True,
        description="Wenn aktiv: alle 4 Wände im selben Stil. Sonst pro Seite einstellbar.")
    wall_style: EnumProperty(name="Wandstil",
        items=presets.items(presets.WALL_PRESETS), default='TRAPEZ_RUST')
    wall_style_front: EnumProperty(name="Vorne",
        items=presets.items(presets.WALL_PRESETS), default='TRAPEZ_RUST')
    wall_style_back: EnumProperty(name="Hinten",
        items=presets.items(presets.WALL_PRESETS), default='TRAPEZ_RUST')
    wall_style_left: EnumProperty(name="Links",
        items=presets.items(presets.WALL_PRESETS), default='TRAPEZ_RUST')
    wall_style_right: EnumProperty(name="Rechts",
        items=presets.items(presets.WALL_PRESETS), default='TRAPEZ_RUST')

    roof_style: EnumProperty(name="Dachstil",
        items=presets.items(presets.ROOF_PRESETS), default='TRAPEZ_ANTHRACITE')
    door_style: EnumProperty(name="Tor-Stil",
        items=presets.items(presets.DOOR_PRESETS), default='TRAPEZ_WHITE')
    plinth_style: EnumProperty(name="Sockel-Stil",
        items=presets.items(presets.PLINTH_PRESETS), default='CONCRETE')

    # --- 3D-Profil-Geometrie (echte Trapezblech-Riffeln) ---
    wall_3d_profile: BoolProperty(
        name="3D-Trapez-Profil",
        description="Echte Trapezblech-Riffeln als Geometrie statt Texture. "
                    "Höherer Polycount, sieht aber ohne Texturen schon richtig aus. "
                    "Wird nur bei TRAPEZ_*-Stilen angewendet.",
        default=False)
    profile_amplitude: FloatProperty(
        name="Profilhöhe", default=0.025, min=0.005, max=0.10, unit='LENGTH',
        description="Wie weit die Riffeln aus der Wand stehen")
    profile_period: FloatProperty(
        name="Profil-Periode", default=0.33, min=0.10, max=1.0, unit='LENGTH',
        description="Abstand zwischen zwei Riffeln (typisch 33cm bei T35-Profil)")

    # --- Material / UV ---
    create_materials: BoolProperty(name="Materialien anlegen", default=True)
    create_uvs:       BoolProperty(name="UV-Mapping anlegen", default=True)
    uv_scale:         FloatProperty(name="UV-Skala (1/m)", default=1.0, min=0.1, max=10.0,
                                    description="UV-Texeldichte: 1.0 = 1m pro UV-Einheit")
    uv_strategy: EnumProperty(
        name="UV-Strategie",
        items=[
            ('SMART', "Smart (pro Element passend)",
             "Wand-lokal für Wände, Slope-aligned für Dachschrägen, Cylinder für Tank/Rinne"),
            ('PLANAR', "Planar (world-XYZ)",
             "Einfache Cube-Projektion pro Face — funktioniert immer, aber Texturen können unterschiedlich orientiert sein"),
        ],
        default='SMART',
        description="Wie UVs berechnet werden")
    use_procedural_shaders: BoolProperty(
        name="Procedural Shader",
        description="Nutzt Blender-Shader-Nodes für Trapez/Wood/Brick/Riffel-Patterns. "
                    "Schöne Vorschau ohne externe Texturen, vor I3D-Export ggf. Texturen ergänzen.",
        default=True)
    texture_pack_path: StringProperty(
        name="Texture-Pack-Ordner",
        subtype='DIR_PATH',
        default="",
        description="Optionaler Ordner mit PBR-Texturen. Pro Stil-Key wird automatisch nach "
                    "<key_lowercase>_basecolor.png/_normal.png/_roughness.png/_metallic.png "
                    "gesucht. Leer = nur Procedural Shader.")
    uv_debug_tile_meters: FloatProperty(
        name="UV-Grid Kachelgröße",
        description="Wie viele Meter Wand eine UV-Grid-Kachel überdeckt im Debug-Modus. "
                    "Groesser = weniger Kacheln = besser lesbare Buchstaben",
        default=4.0, min=0.25, max=20.0, soft_min=1.0, soft_max=10.0,
        unit='LENGTH')

    # --- FS25 ---
    fs25_origin_floor: BoolProperty(name="Origin Boden-Mitte", default=True)
    create_collision:  BoolProperty(name="Collision-Box", default=False)

    # --- Helper functions ---
    def get_wall_style_for_side(self, side):
        """Returns the wall_style key for a given side."""
        if self.wall_same_for_all:
            return self.wall_style
        return {
            'FRONT': self.wall_style_front,
            'BACK':  self.wall_style_back,
            'LEFT':  self.wall_style_left,
            'RIGHT': self.wall_style_right,
        }[side]
