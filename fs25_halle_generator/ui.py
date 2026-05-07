"""Sidebar-Panel für das Halle-Addon."""

from bpy.types import Panel


def _section(layout, props, prop_name, label, icon='NONE'):
    """Collapsible section header. Returns (box, is_open)."""
    box = layout.box()
    row = box.row(align=True)
    is_open = getattr(props, prop_name)
    tri = 'TRIA_DOWN' if is_open else 'TRIA_RIGHT'
    row.prop(props, prop_name, text="", icon=tri, emboss=False)
    row.label(text=label, icon=icon)
    return box, is_open


class HALLE_PT_main(Panel):
    bl_label = "FS25 Halle"
    bl_idname = "HALLE_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FS25 Halle"

    def draw(self, context):
        layout = self.layout
        p = context.scene.halle_settings

        # Identifikation
        c = layout.column(align=True)
        c.prop(p, "base_name")
        c.prop(p, "collection_name")

        # Hauptmaße
        box, show = _section(layout, p, "show_dimensions", "Hauptmaße", 'ARROW_LEFTRIGHT')
        if show:
            c = box.column(align=True)
            c.prop(p, "width")
            c.prop(p, "depth")
            c.prop(p, "wall_height")
            c.prop(p, "wall_thickness")

        # Dach
        box, show = _section(layout, p, "show_roof", "Dach", 'HOME')
        if show:
            box.prop(p, "roof_type")
            if p.roof_type == 'SHED':
                box.prop(p, "shed_high_side")
            if p.roof_type in ('GABLE', 'SHED'):
                box.prop(p, "roof_pitch_deg")
            c = box.column(align=True)
            c.prop(p, "roof_overhang_eaves")
            c.prop(p, "roof_overhang_gable")
            box.prop(p, "roof_thickness")
            r = box.row(align=True)
            if p.roof_type == 'GABLE':
                r.prop(p, "create_ridge_cap", toggle=True)
            r.prop(p, "create_gutters", toggle=True)
            if p.create_gutters:
                box.prop(p, "gutter_size")

        # Boden / Sockel
        box, show = _section(layout, p, "show_floor", "Boden & Sockel", 'MESH_PLANE')
        if show:
            box.prop(p, "create_floor")
            if p.create_floor:
                c = box.column(align=True)
                c.prop(p, "floor_thickness")
                c.prop(p, "floor_extend")
            box.prop(p, "create_plinth")
            if p.create_plinth:
                c = box.column(align=True)
                c.prop(p, "plinth_height")
                c.prop(p, "plinth_offset")

        # Tore
        box, show = _section(layout, p, "show_doors", "Tore", 'MESH_GRID')
        if show:
            c = box.column(align=True)
            c.prop(p, "door_front_count")
            c.prop(p, "door_back_count")
            c.prop(p, "door_left_count")
            c.prop(p, "door_right_count")
            c = box.column(align=True)
            c.prop(p, "door_width")
            c.prop(p, "door_height")
            box.prop(p, "door_sectional")
            if p.door_sectional:
                c = box.column(align=True)
                c.prop(p, "door_panel_count")
                c.prop(p, "door_panel_gap")

        # Fenster / Lichtbänder
        box, show = _section(layout, p, "show_windows", "Fenster / Lichtband", 'MOD_MIRROR')
        if show:
            r = box.row(align=True)
            r.prop(p, "window_front", toggle=True)
            r.prop(p, "window_back", toggle=True)
            r = box.row(align=True)
            r.prop(p, "window_left", toggle=True)
            r.prop(p, "window_right", toggle=True)
            c = box.column(align=True)
            c.prop(p, "window_z")
            c.prop(p, "window_height")
            c.prop(p, "window_margin")

        # Stützen
        box, show = _section(layout, p, "show_columns", "Innenstützen", 'EMPTY_SINGLE_ARROW')
        if show:
            box.prop(p, "create_columns")
            if p.create_columns:
                c = box.column(align=True)
                c.prop(p, "column_count")
                c.prop(p, "column_size")

        # Innendetails
        box, show = _section(layout, p, "show_details", "Innendetails", 'TOOL_SETTINGS')
        if show:
            c = box.column(align=True)
            c.prop(p, "detail_workbench", toggle=True)
            c.prop(p, "detail_tool_wall", toggle=True)
            c.prop(p, "detail_diesel_tank", toggle=True)
            c.prop(p, "detail_compressor", toggle=True)
            c.prop(p, "detail_fire_extinguisher", toggle=True)

        # Stil & Farbe
        box, show = _section(layout, p, "show_style", "Stil & Farbe", 'COLOR')
        if show:
            box.prop(p, "wall_same_for_all")
            if p.wall_same_for_all:
                box.prop(p, "wall_style")
            else:
                c = box.column(align=True)
                c.prop(p, "wall_style_front")
                c.prop(p, "wall_style_back")
                c.prop(p, "wall_style_left")
                c.prop(p, "wall_style_right")

            box.separator()
            c = box.column(align=True)
            c.prop(p, "roof_style")
            c.prop(p, "door_style")
            if p.create_plinth:
                c.prop(p, "plinth_style")

            box.separator()
            box.prop(p, "wall_3d_profile")
            if p.wall_3d_profile:
                c = box.column(align=True)
                c.prop(p, "profile_amplitude")
                c.prop(p, "profile_period")
                box.label(text="3D-Profil wirkt nur auf TRAPEZ_*-Wände",
                          icon='INFO')

        # FS25 / Material / UV
        box, show = _section(layout, p, "show_export", "FS25 / Material / UV", 'EXPORT')
        if show:
            box.prop(p, "create_materials")
            if p.create_materials:
                box.prop(p, "use_procedural_shaders")
            box.prop(p, "create_uvs")
            if p.create_uvs:
                box.prop(p, "uv_scale")
            box.prop(p, "fs25_origin_floor")
            box.prop(p, "create_collision")

        # Aktionen
        layout.separator()
        layout.operator("halle.generate", icon='MESH_CUBE')
        layout.operator("halle.clear", icon='X')
