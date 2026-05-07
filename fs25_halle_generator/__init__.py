"""FS25 Halle Generator — Blender Addon (Package).

Generiert parametrische Maschinenhallen für Farming Simulator 25.

Module:
    presets    : Material-Presets (Trapezblech, Holz, Klinker, Riffelblech, ...)
    properties : PropertyGroup mit allen einstellbaren Parametern
    materials  : Procedural Shader Nodes pro Pattern + UV-Mapping
    geometry   : Wände, Dächer, Tore, Fenster, Sockel, Stützen, Rinnen
                 + 3D-Trapez-Profil als Geometrie
    details    : Innendetails (Werkbank, Tank, Kompressor, ...)
    generator  : Hauptorchestrator generate_hall()
    operators  : Generate / Clear Buttons
    ui         : Sidebar-Panel
"""

bl_info = {
    "name": "FS25 Halle Generator",
    "author": "AMS-ABSTAND",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar (N) > FS25 Halle",
    "description": "Parametrische Maschinenhallen für Farming Simulator 25 — "
                   "mit Procedural Shaders, Per-Seite-Wandstilen und 3D-Trapez-Profil",
    "category": "Add Mesh",
}


# Reload-Support für Blender-Reload-Skripte (F3 → "Reload Scripts")
if "bpy" in locals():
    import importlib
    for mod_name in ("presets", "properties", "materials", "geometry",
                     "details", "generator", "operators", "ui"):
        if mod_name in locals():
            importlib.reload(locals()[mod_name])

import bpy
from bpy.props import PointerProperty

from . import presets
from . import properties
from . import materials
from . import geometry
from . import details
from . import generator
from . import operators
from . import ui


classes = (
    properties.HALLE_PG_settings,
    operators.HALLE_OT_generate,
    operators.HALLE_OT_clear,
    ui.HALLE_PT_main,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.halle_settings = PointerProperty(type=properties.HALLE_PG_settings)


def unregister():
    if hasattr(bpy.types.Scene, "halle_settings"):
        del bpy.types.Scene.halle_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
