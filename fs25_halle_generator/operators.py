"""Blender Operators für das Halle-Addon."""

import bpy
from bpy.types import Operator

from . import generator


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
