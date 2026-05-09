"""Blender Operators für das Halle-Addon."""

import bpy
from bpy.types import Operator

from . import generator


UV_DEBUG_IMAGE_NAME = "Halle_UV_Debug_Grid"


class HALLE_OT_generate(Operator):
    bl_idname = "halle.generate"
    bl_label = "Halle generieren"
    bl_description = "Maschinenhalle mit aktuellen Einstellungen erzeugen / aktualisieren"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.halle_settings
        try:
            objects = generator.generate_hall(props, context)
        except Exception as e:
            self.report({'ERROR'}, f"Fehler: {e}")
            raise
        self.report({'INFO'},
                    f"Halle erzeugt: {len(objects)} Objekte in '{props.collection_name}'")
        return {'FINISHED'}


class HALLE_OT_clear(Operator):
    bl_idname = "halle.clear"
    bl_label = "Collection leeren"
    bl_description = "Alle Objekte in der Halle-Collection löschen"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.halle_settings
        col = bpy.data.collections.get(props.collection_name)
        if col is None:
            self.report({'INFO'}, f"Collection '{props.collection_name}' existiert nicht.")
            return {'CANCELLED'}
        n = len(col.objects)
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        self.report({'INFO'}, f"{n} Objekte gelöscht.")
        return {'FINISHED'}


def _get_or_create_uv_grid():
    """Get or create the Blender-generated UV_GRID image used for debugging."""
    img = bpy.data.images.get(UV_DEBUG_IMAGE_NAME)
    if img is None:
        img = bpy.data.images.new(UV_DEBUG_IMAGE_NAME, 1024, 1024,
                                  alpha=False, float_buffer=False)
        img.generated_type = 'UV_GRID'
        img.generated_width = 1024
        img.generated_height = 1024
    return img


def _swap_basecolor_to_uv_grid(mat, img):
    """Replace the basecolor input of a material with the UV grid image.
    Removes existing nodes feeding base color (procedural patterns,
    image textures), keeping just BSDF + Output."""
    if not mat.use_nodes:
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    output = nt.nodes.new("ShaderNodeOutputMaterial")
    output.location = (400, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (100, 0)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.location = (-300, 0)
    tex.image = img

    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(bsdf.outputs[0], output.inputs[0])

    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = 0.5
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0


class HALLE_OT_uv_debug(Operator):
    bl_idname = "halle.uv_debug"
    bl_label = "UV-Grid auf alle Halle-Materialien"
    bl_description = ("Ersetzt alle Halle_*-Materialien temporär mit einem "
                      "Blender-eigenen UV-Test-Grid (1024x1024 mit Buchstaben "
                      "und Farb-Quadranten). Perfekt zum Pruefen ob die UVs "
                      "richtig gemappt sind. 'Halle generieren' macht's wieder rueckgaengig.")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        img = _get_or_create_uv_grid()
        count = 0
        for mat in bpy.data.materials:
            if not mat.name.startswith("Halle_"):
                continue
            if mat.name == "Halle_Glass":
                continue  # leave glass transparent
            _swap_basecolor_to_uv_grid(mat, img)
            count += 1
        self.report({'INFO'},
                    f"UV-Grid auf {count} Materialien angewendet "
                    f"— Viewport in 'Material Preview' schalten zum Sehen.")
        return {'FINISHED'}
