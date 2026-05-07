"""Render example halls as screenshots for the README."""
import sys
import os
import math
import bpy

ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
if ADDON_DIR not in sys.path:
    sys.path.insert(0, ADDON_DIR)

OUT_DIR = os.path.join(ADDON_DIR, "docs", "img")
os.makedirs(OUT_DIR, exist_ok=True)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup_camera(target=(0, 0, 3.0), distance=28, height=12, angle_deg=35):
    cam_data = bpy.data.cameras.new("RenderCam")
    cam = bpy.data.objects.new("RenderCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    angle = math.radians(angle_deg)
    cam.location = (distance * math.cos(angle),
                    -distance * math.sin(angle),
                    height)
    # Aim at target via track-to constraint
    target_empty = bpy.data.objects.new("CamTarget", None)
    target_empty.location = target
    bpy.context.scene.collection.objects.link(target_empty)
    track = cam.constraints.new('TRACK_TO')
    track.target = target_empty
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    cam_data.lens = 35


def setup_lighting():
    sun_data = bpy.data.lights.new("Sun", 'SUN')
    sun_data.energy = 4.0
    sun_data.angle = math.radians(3)
    sun = bpy.data.objects.new("Sun", sun_data)
    bpy.context.scene.collection.objects.link(sun)
    sun.location = (10, -10, 20)
    sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(40))

    # World background — sky-blue gradient
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs['Color'].default_value = (0.55, 0.70, 0.85, 1.0)
    bg.inputs['Strength'].default_value = 1.5
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(bg.outputs[0], out.inputs[0])


def add_ground():
    bpy.ops.mesh.primitive_plane_add(size=80)
    plane = bpy.context.active_object
    plane.name = "Ground"
    mat = bpy.data.materials.new("Ground_Grass")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.20, 0.32, 0.15, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.95
    plane.data.materials.append(mat)


def render(filepath, resolution=(1280, 720), engine='BLENDER_EEVEE_NEXT'):
    scn = bpy.context.scene
    # Try EEVEE Next first (Blender 4.2+), fall back to EEVEE
    try:
        scn.render.engine = engine
    except TypeError:
        scn.render.engine = 'BLENDER_EEVEE'
    scn.render.resolution_x = resolution[0]
    scn.render.resolution_y = resolution[1]
    scn.render.resolution_percentage = 100
    scn.render.image_settings.file_format = 'PNG'
    scn.render.filepath = filepath
    scn.eevee.taa_render_samples = 32
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {filepath}")


_addon_registered = False


def render_hall(name, configure_fn, cam_target=(0, 0, 3.0), distance=28):
    global _addon_registered
    reset_scene()
    add_ground()
    setup_lighting()
    setup_camera(target=cam_target, distance=distance)

    import fs25_halle_generator
    # read_factory_settings wipes scene properties — re-register PointerProperty
    # but leave classes registered.
    if not _addon_registered:
        fs25_halle_generator.register()
        _addon_registered = True
    else:
        # Only re-create the Scene PointerProperty (classes still registered)
        from bpy.props import PointerProperty
        bpy.types.Scene.halle_settings = PointerProperty(
            type=fs25_halle_generator.properties.HALLE_PG_settings)

    p = bpy.context.scene.halle_settings
    configure_fn(p)
    bpy.ops.halle.generate()

    out = os.path.join(OUT_DIR, f"{name}.png")
    render(out)


# ----------------------------------------------------------------------
def cfg_classic(p):
    p.collection_name = "Halle"
    p.width = 24.0; p.depth = 16.0; p.wall_height = 5.5
    p.roof_type = 'GABLE'; p.roof_pitch_deg = 22
    p.door_front_count = 3
    p.window_front = True; p.window_back = False
    p.window_left = True; p.window_right = True
    p.create_columns = False
    p.detail_workbench = False
    p.detail_diesel_tank = True
    p.wall_style = 'TRAPEZ_GREEN'
    p.roof_style = 'TRAPEZ_RED'
    p.door_style = 'TRAPEZ_WHITE'
    p.plinth_style = 'CONCRETE'


def cfg_wood(p):
    cfg_classic(p)
    p.collection_name = "Halle"
    p.wall_style = 'WOOD_DARK'
    p.roof_style = 'TILES_RED'
    p.plinth_style = 'CLINKER_RED'
    p.door_style = 'WOOD'


def cfg_3d_profile(p):
    cfg_classic(p)
    p.collection_name = "Halle"
    p.wall_style = 'TRAPEZ_ANTHRACITE'
    p.roof_style = 'TRAPEZ_ANTHRACITE'
    p.door_style = 'TRAPEZ_WHITE'
    p.wall_3d_profile = True
    p.profile_amplitude = 0.04
    p.profile_period = 0.33


print("Rendering hero shots...")
render_hall("hero_classic", cfg_classic)
render_hall("variant_wood",  cfg_wood)
render_hall("variant_3d_profile", cfg_3d_profile)
print(f"\nDone. Files in: {OUT_DIR}")
