"""Verify the addon can be enabled in Blender 5.1 from its installed location."""
import bpy

# Try to enable the addon
try:
    bpy.ops.preferences.addon_enable(module="fs25_halle_generator")
    print("ENABLED: fs25_halle_generator")
except Exception as e:
    print(f"FAIL on enable: {e}")
    raise

# Verify it's registered
import addon_utils
mod_names = {m.__name__ for m in addon_utils.modules()}
if "fs25_halle_generator" in mod_names:
    print("VISIBLE in addon list")
else:
    print(f"NOT VISIBLE (modules: {sorted(mod_names)[:10]}...)")

# Verify the panel and operators are registered
ok = True
if not hasattr(bpy.types.Scene, "halle_settings"):
    print("FAIL: Scene.halle_settings not registered")
    ok = False
else:
    print("OK: Scene.halle_settings registered")

if hasattr(bpy.types, "HALLE_OT_generate"):
    print("OK: HALLE_OT_generate registered")
else:
    print("FAIL: HALLE_OT_generate missing")
    ok = False

if hasattr(bpy.types, "HALLE_PT_main"):
    print("OK: HALLE_PT_main registered")
else:
    print("FAIL: HALLE_PT_main missing")
    ok = False

# Try to actually generate a hall
if ok:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.preferences.addon_enable(module="fs25_halle_generator")
    p = bpy.context.scene.halle_settings
    p.collection_name = "Halle_VerifyTest"
    p.detail_workbench = True
    p.detail_diesel_tank = True
    bpy.ops.halle.generate()
    col = bpy.data.collections.get("Halle_VerifyTest")
    if col and len(col.objects) > 5:
        print(f"OK: Generation works ({len(col.objects)} objects created)")
    else:
        print(f"FAIL: Generation produced no objects")

print(f"\nBlender: {bpy.app.version_string}")
print("RESULT:", "ALL OK" if ok else "FAILED")
