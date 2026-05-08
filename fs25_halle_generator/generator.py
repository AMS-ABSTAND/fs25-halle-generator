"""Hauptorchestrator: generate_hall() führt die ganze Pipeline aus."""

from math import radians, tan
from . import geometry as geom
from . import materials as mats
from . import details
from . import presets as P


def generate_hall(props, context):
    W, D, H, T = props.width, props.depth, props.wall_height, props.wall_thickness
    half_w, half_d = W / 2, D / 2
    pitch = radians(props.roof_pitch_deg)

    if props.roof_type == 'GABLE':
        ridge_z = H + half_w * tan(pitch)
    elif props.roof_type == 'SHED':
        if props.shed_high_side in ('LEFT', 'RIGHT'):
            ridge_z = H + 2 * half_w * tan(pitch)
        else:
            ridge_z = H + 2 * half_d * tan(pitch)
    else:
        ridge_z = H + props.roof_thickness

    base = props.base_name
    col = geom.ensure_collection(props.collection_name)

    # Clear collection
    import bpy
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    created = []

    # ------------------------------------------------------------------
    #  MATERIALS
    # ------------------------------------------------------------------
    M = {}
    if props.create_materials:
        use_proc = props.use_procedural_shaders

        # Per-side wall materials (4 entries even if same_for_all → same key 4×)
        for side_name in ('FRONT', 'BACK', 'LEFT', 'RIGHT'):
            key = props.get_wall_style_for_side(side_name)
            if f'wall_{key}' not in M:
                M[f'wall_{key}'] = mats.make_material_from_preset(
                    f"Halle_Wall_{key}", P.WALL_PRESETS, key, use_procedural=use_proc)

        # Roof / Door / Plinth — single style each
        M['roof']   = mats.make_material_from_preset(
            f"Halle_Roof_{props.roof_style}", P.ROOF_PRESETS, props.roof_style, use_proc)
        M['door']   = mats.make_material_from_preset(
            f"Halle_Door_{props.door_style}", P.DOOR_PRESETS, props.door_style, use_proc)
        M['plinth'] = mats.make_material_from_preset(
            f"Halle_Plinth_{props.plinth_style}", P.PLINTH_PRESETS, props.plinth_style, use_proc)

        # Auxiliary materials
        M['concrete'] = mats.make_material("Halle_Concrete", (0.55, 0.55, 0.55), 0.85, 0.0,
                                           pattern=P.PATTERN_CONCRETE, use_procedural=use_proc)
        M['steel']  = mats.make_material("Halle_Steel",   (0.20, 0.20, 0.22), 0.30, 0.70)
        M['glass']  = mats.make_material("Halle_Glass",   (0.65, 0.78, 0.85), 0.10, 0.0,
                                         alpha=0.30, transmission=0.85)
        M['wood']   = mats.make_material("Halle_Wood",    (0.50, 0.32, 0.18), 0.85, 0.0,
                                         pattern=P.PATTERN_WOOD, use_procedural=use_proc)
        M['red']    = mats.make_material("Halle_Red",     (0.75, 0.10, 0.08), 0.60, 0.10)
        M['gutter'] = mats.make_material("Halle_Gutter_Zinc", (0.78, 0.78, 0.80), 0.40, 0.50)

    # ------------------------------------------------------------------
    #  HELPER
    # ------------------------------------------------------------------
    def add_obj(name, vf, mat=None, uv_scale=None, skip_uv=False):
        """Create an object from (verts, faces). Auto-creates UV map when
        `props.create_uvs` is enabled, even if `uv_scale` is not passed
        — falls back to `props.uv_scale`. Pass `skip_uv=True` to opt out
        (used for the wireframe collision box where UVs are useless)."""
        if not vf or not vf[0]:
            return None
        obj = geom.make_object(name, vf[0], vf[1], col, mat=mat)
        if props.create_uvs and not skip_uv:
            scale = uv_scale if uv_scale is not None else props.uv_scale
            mats.set_uvs_planar(obj, scale=scale)
        created.append(obj)
        return obj

    # ------------------------------------------------------------------
    #  FLOOR
    # ------------------------------------------------------------------
    if props.create_floor:
        ext, ft = props.floor_extend, props.floor_thickness
        add_obj(f"{base}_Floor",
                geom.box(-half_w - ext, +half_w + ext,
                         -half_d - ext, +half_d + ext, -ft, 0.0),
                mat=M.get('concrete'), uv_scale=props.uv_scale)

    # ------------------------------------------------------------------
    #  PLINTH
    # ------------------------------------------------------------------
    if props.create_plinth and props.plinth_height > 0:
        items = geom.build_plinth(props, half_w, half_d)
        if items:
            add_obj(f"{base}_Plinth", geom.merge(items),
                    mat=M.get('plinth'), uv_scale=props.uv_scale)

    # ------------------------------------------------------------------
    #  DOOR POSITIONS PER SIDE
    # ------------------------------------------------------------------
    door_counts = {
        'FRONT': props.door_front_count, 'BACK': props.door_back_count,
        'LEFT':  props.door_left_count,  'RIGHT': props.door_right_count,
    }
    door_centers = {}
    for side, cnt in door_counts.items():
        wlen = W if side in ('FRONT', 'BACK') else D
        door_centers[side] = geom.door_x_positions(cnt, wlen, props.door_width)

    # ------------------------------------------------------------------
    #  WALLS (with optional 3D-Trapez-Skin)
    # ------------------------------------------------------------------
    for side in ('FRONT', 'BACK', 'LEFT', 'RIGHT'):
        wall_style = props.get_wall_style_for_side(side)
        wall_mat = M.get(f'wall_{wall_style}')

        doors_here = [(cx, props.door_width, props.door_height)
                      for cx in door_centers[side]]
        windows_here = geom.window_cutout_for_side(side, props, half_w, half_d)

        use_3d_profile = (props.wall_3d_profile and
                          P.is_trapez_style(P.WALL_PRESETS, wall_style))

        if use_3d_profile:
            wall_vf, skin_vf = geom.build_wall_with_trapez_skin(
                side, props, half_w, half_d, doors_here, windows_here)
            if wall_vf[0]:
                add_obj(f"{base}_Wall_{side.capitalize()}", wall_vf,
                        mat=wall_mat, uv_scale=props.uv_scale)
            if skin_vf[0]:
                add_obj(f"{base}_Wall_{side.capitalize()}_Skin", skin_vf,
                        mat=wall_mat, uv_scale=props.uv_scale)
        else:
            v, f = geom.build_wall(side, props, half_w, half_d, doors_here, windows_here)
            if v:
                add_obj(f"{base}_Wall_{side.capitalize()}", (v, f),
                        mat=wall_mat, uv_scale=props.uv_scale)

    # ------------------------------------------------------------------
    #  ROOF
    # ------------------------------------------------------------------
    if props.roof_type == 'GABLE':
        for sign, name in ((-1, 'Left'), (+1, 'Right')):
            v, f = geom.build_gable_slope(sign, props, half_w, half_d, ridge_z)
            add_obj(f"{base}_Roof_{name}", (v, f),
                    mat=M.get('roof'), uv_scale=props.uv_scale)
        if props.create_ridge_cap:
            add_obj(f"{base}_RidgeCap",
                    geom.build_ridge_cap(props, half_w, half_d, ridge_z),
                    mat=M.get('roof'), uv_scale=props.uv_scale)
    elif props.roof_type == 'SHED':
        v, f = geom.build_shed_roof(props, half_w, half_d)
        add_obj(f"{base}_Roof", (v, f), mat=M.get('roof'), uv_scale=props.uv_scale)
    elif props.roof_type == 'FLAT':
        v, f = geom.build_flat_roof(props, half_w, half_d)
        add_obj(f"{base}_Roof", (v, f), mat=M.get('roof'), uv_scale=props.uv_scale)

    # ------------------------------------------------------------------
    #  GUTTERS
    # ------------------------------------------------------------------
    if props.create_gutters and props.roof_type != 'FLAT':
        items = geom.build_gutters(props, half_w, half_d)
        if items:
            add_obj(f"{base}_Gutters", geom.merge(items), mat=M.get('gutter'))

    # ------------------------------------------------------------------
    #  DOOR PANELS (sectional or single)
    # ------------------------------------------------------------------
    door_idx = 1
    for side in ('FRONT', 'BACK', 'LEFT', 'RIGHT'):
        for cx in door_centers[side]:
            if props.door_sectional:
                pn = props.door_panel_count
                gap = props.door_panel_gap
                panel_h = (props.door_height - (pn - 1) * gap) / pn
                for k in range(pn):
                    z1 = k * (panel_h + gap)
                    z2 = z1 + panel_h
                    v, f = geom.build_door_panel_box(side, cx, props.door_width,
                                                    z1, z2, half_w, half_d, T)
                    obj = add_obj(f"{base}_Door_{door_idx:02d}_Panel{k+1}",
                                  (v, f), mat=M.get('door'), uv_scale=props.uv_scale)
                    if obj:
                        origin = geom.door_panel_origin(side, cx, props.door_width, z1,
                                                       half_w, half_d, T)
                        geom.set_origin(obj, origin)
            else:
                v, f = geom.build_door_panel_box(side, cx, props.door_width,
                                                0.05, props.door_height - 0.02,
                                                half_w, half_d, T)
                obj = add_obj(f"{base}_Door_{door_idx:02d}", (v, f),
                              mat=M.get('door'), uv_scale=props.uv_scale)
                if obj:
                    origin = geom.door_panel_origin(side, cx, props.door_width, 0.0,
                                                   half_w, half_d, T)
                    geom.set_origin(obj, origin)
            door_idx += 1

    # ------------------------------------------------------------------
    #  WINDOWS (Glass)
    # ------------------------------------------------------------------
    win_idx = 1
    for side in ('FRONT', 'BACK', 'LEFT', 'RIGHT'):
        cuts = geom.window_cutout_for_side(side, props, half_w, half_d)
        for lx1, lx2, z1, z2 in cuts:
            v, f = geom.build_window_glass(side, lx1, lx2, z1, z2, half_w, half_d, T)
            add_obj(f"{base}_Window_{side.capitalize()}_{win_idx:02d}", (v, f),
                    mat=M.get('glass'), uv_scale=props.uv_scale)
            win_idx += 1

    # ------------------------------------------------------------------
    #  COLUMNS
    # ------------------------------------------------------------------
    column_items = geom.build_columns(props, half_w, half_d)
    if column_items:
        add_obj(f"{base}_Columns", geom.merge(column_items),
                mat=M.get('steel'), uv_scale=props.uv_scale)

    # ------------------------------------------------------------------
    #  INTERIOR DETAILS
    # ------------------------------------------------------------------
    if props.detail_workbench:
        add_obj(f"{base}_Detail_Workbench",
                geom.merge(details.build_workbench(props, half_w, half_d)),
                mat=M.get('wood'), uv_scale=props.uv_scale)
    if props.detail_tool_wall:
        add_obj(f"{base}_Detail_ToolWall",
                geom.merge(details.build_tool_wall(props, half_w, half_d)),
                mat=M.get('wood'), uv_scale=props.uv_scale)
    if props.detail_diesel_tank:
        add_obj(f"{base}_Detail_DieselTank",
                geom.merge(details.build_diesel_tank(props, half_w, half_d)),
                mat=M.get('steel'), uv_scale=props.uv_scale)
    if props.detail_compressor:
        add_obj(f"{base}_Detail_Compressor",
                geom.merge(details.build_compressor(props, half_w, half_d)),
                mat=M.get('steel'), uv_scale=props.uv_scale)
    if props.detail_fire_extinguisher:
        add_obj(f"{base}_Detail_FireExtinguisher",
                geom.merge(details.build_fire_extinguisher(props, half_w, half_d)),
                mat=M.get('red'), uv_scale=props.uv_scale)

    # ------------------------------------------------------------------
    #  COLLISION
    # ------------------------------------------------------------------
    if props.create_collision:
        v, f = geom.box(-half_w, +half_w, -half_d, +half_d, 0.0, ridge_z)
        obj = add_obj(f"{base}_Collision", (v, f), skip_uv=True)
        if obj:
            obj.display_type = 'WIRE'
            obj.hide_render = True

    return created
