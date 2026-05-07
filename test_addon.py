"""Headless smoke test: alle Konfigurationen, alle Stile, 3D-Profil, per-Seite-Walls."""
import sys
import os

ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
if ADDON_DIR not in sys.path:
    sys.path.insert(0, ADDON_DIR)

import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)

# Import the package addon
import fs25_halle_generator
fs25_halle_generator.register()


def configure_full(p):
    """Vollausstattung als Baseline."""
    p.base_name = "Maschinenhalle"
    p.collection_name = "Halle"
    p.width = 24.0
    p.depth = 18.0
    p.wall_height = 5.5
    p.wall_thickness = 0.25
    p.roof_type = 'GABLE'
    p.roof_pitch_deg = 25.0
    p.roof_overhang_eaves = 0.6
    p.roof_overhang_gable = 0.4
    p.roof_thickness = 0.15
    p.create_ridge_cap = True
    p.create_gutters = True
    p.gutter_size = 0.12

    p.create_floor = True
    p.floor_thickness = 0.2
    p.floor_extend = 0.3

    p.create_plinth = True
    p.plinth_height = 0.4
    p.plinth_offset = 0.05

    p.door_front_count = 3
    p.door_back_count = 0
    p.door_left_count = 1
    p.door_right_count = 0
    p.door_width = 4.5
    p.door_height = 4.5
    p.door_sectional = True
    p.door_panel_count = 5
    p.door_panel_gap = 0.015

    p.window_front = True
    p.window_back = True
    p.window_left = True
    p.window_right = True
    p.window_z = 3.5
    p.window_height = 1.0
    p.window_margin = 0.8

    p.create_columns = True
    p.column_count = 3
    p.column_size = 0.30

    p.detail_workbench = True
    p.detail_tool_wall = True
    p.detail_diesel_tank = True
    p.detail_compressor = True
    p.detail_fire_extinguisher = True

    # Default styles (v0.3 baseline)
    p.wall_same_for_all = True
    p.wall_style = 'TRAPEZ_RUST'
    p.roof_style = 'TRAPEZ_ANTHRACITE'
    p.door_style = 'TRAPEZ_WHITE'
    p.plinth_style = 'CONCRETE'
    p.wall_3d_profile = False

    p.create_materials = True
    p.use_procedural_shaders = True
    p.create_uvs = True
    p.uv_scale = 1.0
    p.create_collision = True


def inspect(name, allow_warn=False):
    col = bpy.data.collections.get(name)
    if col is None:
        print(f"  FAIL: Collection '{name}' not found")
        return False, 0, 0
    n_obj = len(col.objects)
    n_v = sum(len(o.data.vertices) for o in col.objects if hasattr(o.data, 'vertices'))
    n_f = sum(len(o.data.polygons) for o in col.objects if hasattr(o.data, 'polygons'))
    print(f"  {name}: {n_obj} objects, {n_v} verts, {n_f} faces")
    issues = 0
    for obj in col.objects:
        if obj.type != 'MESH':
            continue
        m = obj.data
        if m.validate(verbose=False):
            print(f"    WARN: {obj.name} invalid (auto-fixed)")
            issues += 1
        for poly in m.polygons:
            if poly.area < 1e-7:
                print(f"    WARN: {obj.name} zero-area face")
                issues += 1
                break
    return (issues == 0 or allow_warn), n_v, n_f


# ============================================================
def banner(s):
    print("\n" + "=" * 60)
    print(s)
    print("=" * 60)


tests = []

# 1: Default Gable, full features
banner("TEST 1: GABLE roof + all features (default styles)")
p = bpy.context.scene.halle_settings
configure_full(p)
p.collection_name = "Halle_Gable"
bpy.ops.halle.generate()
tests.append(inspect("Halle_Gable"))

# 2: SHED back
banner("TEST 2: SHED Pultdach (high=BACK)")
configure_full(p); p.collection_name = "Halle_Shed_Back"
p.roof_type = 'SHED'; p.shed_high_side = 'BACK'
bpy.ops.halle.generate()
tests.append(inspect("Halle_Shed_Back"))

# 3: FLAT
banner("TEST 3: FLAT roof")
configure_full(p); p.collection_name = "Halle_Flat"
p.roof_type = 'FLAT'
bpy.ops.halle.generate()
tests.append(inspect("Halle_Flat"))

# 4: Doors all sides
banner("TEST 4: Tore auf allen 4 Seiten")
configure_full(p); p.collection_name = "Halle_AllDoors"
p.door_front_count = 2; p.door_back_count = 2
p.door_left_count = 1; p.door_right_count = 1
bpy.ops.halle.generate()
tests.append(inspect("Halle_AllDoors"))

# 5: Holz + Klinker + Riffel + Tonziegel (Stile mixen)
banner("TEST 5: Holz Wand + Klinker Sockel + Riffel Tor + Tonziegel Dach")
configure_full(p); p.collection_name = "Halle_WoodClinker"
p.wall_style = 'WOOD_DARK'
p.plinth_style = 'CLINKER_RED'
p.door_style = 'CHECKER'
p.roof_style = 'TILES_RED'
bpy.ops.halle.generate()
tests.append(inspect("Halle_WoodClinker"))

# 6: Per-Seite Wandstile
banner("TEST 6: Per-Seite Wandstile (Front Holz, Sides Trapez, Back Klinker)")
configure_full(p); p.collection_name = "Halle_MixedWalls"
p.wall_same_for_all = False
p.wall_style_front = 'WOOD_LIGHT'
p.wall_style_back = 'CLINKER_RED'
p.wall_style_left = 'TRAPEZ_GREEN'
p.wall_style_right = 'TRAPEZ_GREEN'
bpy.ops.halle.generate()
tests.append(inspect("Halle_MixedWalls"))

# 7: 3D Trapez profile (echte Riffeln als Geometrie)
banner("TEST 7: 3D-Trapez-Profil aktiviert")
configure_full(p); p.collection_name = "Halle_3DProfile"
p.wall_style = 'TRAPEZ_GREEN'
p.wall_3d_profile = True
p.profile_amplitude = 0.025
p.profile_period = 0.33
bpy.ops.halle.generate()
tests.append(inspect("Halle_3DProfile"))

# 8: 3D Profile + Per-Seite + alle Features
banner("TEST 8: 3D-Profil + Per-Seite mixen (extreme combo)")
configure_full(p); p.collection_name = "Halle_Extreme"
p.wall_same_for_all = False
p.wall_style_front = 'TRAPEZ_RED'
p.wall_style_back = 'TRAPEZ_GREEN'
p.wall_style_left = 'WOOD_DARK'         # 3D-Profil ignoriert Holz, bleibt flat
p.wall_style_right = 'CLINKER_RED'      # 3D-Profil ignoriert Klinker
p.wall_3d_profile = True
bpy.ops.halle.generate()
tests.append(inspect("Halle_Extreme"))

# Material Verifikation
banner("MATERIAL CHECKS (Test 5)")
expected_mats = [
    ("Halle_Wall_WOOD_DARK",      (0.32, 0.20, 0.10)),
    ("Halle_Plinth_CLINKER_RED",  (0.55, 0.20, 0.15)),
    ("Halle_Door_CHECKER",        (0.55, 0.55, 0.58)),
    ("Halle_Roof_TILES_RED",      (0.55, 0.20, 0.12)),
]
mat_ok = True
for name, expected_color in expected_mats:
    mat = bpy.data.materials.get(name)
    if mat is None:
        print(f"  FAIL: '{name}' missing"); mat_ok = False; continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        print(f"  FAIL: '{name}' no BSDF"); mat_ok = False; continue
    actual = tuple(bsdf.inputs["Base Color"].default_value[:3])
    if any(abs(a - e) > 0.01 for a, e in zip(actual, expected_color)):
        # When procedural shaders are on, base color may be replaced by Color Ramp
        # output → check if any node in tree has the expected color
        found = False
        for node in mat.node_tree.nodes:
            for inp in getattr(node, 'inputs', []):
                if hasattr(inp, 'default_value') and hasattr(inp.default_value, '__len__'):
                    if len(inp.default_value) >= 3:
                        c = tuple(inp.default_value[:3])
                        if all(abs(a - e) < 0.01 for a, e in zip(c, expected_color)):
                            found = True; break
            if found: break
        if found:
            print(f"  OK   '{name}' (proc)")
        else:
            print(f"  FAIL: '{name}' color {actual} != {expected_color}")
            mat_ok = False
    else:
        print(f"  OK   '{name}' color {tuple(round(c, 2) for c in actual)}")

# Verify per-side materials exist for Test 6
banner("PER-SIDE WALL MATERIALS (Test 6)")
per_side_mats = ['Halle_Wall_WOOD_LIGHT', 'Halle_Wall_CLINKER_RED',
                 'Halle_Wall_TRAPEZ_GREEN']
for n in per_side_mats:
    if bpy.data.materials.get(n):
        print(f"  OK   '{n}' exists")
    else:
        print(f"  FAIL: '{n}' missing")
        mat_ok = False

# Verify 3D Profile produced extra Skin objects in Test 7
banner("3D PROFILE SKIN OBJECTS (Test 7)")
col_3d = bpy.data.collections.get("Halle_3DProfile")
if col_3d:
    skin_objs = [o for o in col_3d.objects if "_Skin" in o.name]
    if len(skin_objs) > 0:
        total_skin_faces = sum(len(o.data.polygons) for o in skin_objs)
        print(f"  OK   {len(skin_objs)} Skin objects, {total_skin_faces} corrugation faces")
    else:
        print(f"  FAIL: no Skin objects produced")
        mat_ok = False

# Summary
all_ok = all(t[0] for t in tests) and mat_ok
total_v = sum(t[1] for t in tests)
total_f = sum(t[2] for t in tests)
print("\n" + "=" * 60)
print(f"RESULT: {'ALL PASS' if all_ok else 'WARNINGS / FAILURES'}")
print(f"Total geometry across {len(tests)} tests: {total_v} verts, {total_f} faces")
print("=" * 60)

# Save the most interesting one for inspection
out = os.path.join(ADDON_DIR, "test_output.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
print(f"Saved: {out}")
print(f"Blender: {bpy.app.version_string}")
