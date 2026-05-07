"""Alle Geometrie-Funktionen: Primitiven, Wände, Dächer, Tore, Fenster, Sockel, Stützen, Rinnen.

Inkl. 3D-Trapez-Profil als optionale Geometrie-Variante (echte Riffeln statt Texture).
"""

import bpy
import bmesh
from math import radians, tan, cos, sin, pi
from mathutils import Vector


# ============================================================================
#  PRIMITIVES
# ============================================================================

def box(x1, x2, y1, y2, z1, z2):
    """Axis-aligned box. Returns (verts, faces)."""
    if x1 > x2: x1, x2 = x2, x1
    if y1 > y2: y1, y2 = y2, y1
    if z1 > z2: z1, z2 = z2, z1
    v = [
        (x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1),
        (x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2),
    ]
    f = [
        (0, 3, 2, 1), (4, 5, 6, 7),
        (0, 1, 5, 4), (2, 3, 7, 6),
        (1, 2, 6, 5), (3, 0, 4, 7),
    ]
    return v, f


def cylinder(cx, cy, z1, z2, radius, segments=16, axis='Z'):
    """Cylinder along given axis.
    For axis='Z': (cx, cy) = (X, Y), z1/z2 = Z range.
    For axis='X': (cx, cy) = (Y, Z), z1/z2 = X range.
    For axis='Y': (cx, cy) = (X, Z), z1/z2 = Y range.
    """
    verts = []
    bot, top = [], []
    for i in range(segments):
        ang = 2 * pi * i / segments
        a, b = radius * cos(ang), radius * sin(ang)
        if axis == 'Z':
            verts.append((cx + a, cy + b, z1))
            verts.append((cx + a, cy + b, z2))
        elif axis == 'X':
            verts.append((z1, cx + a, cy + b))
            verts.append((z2, cx + a, cy + b))
        else:  # Y
            verts.append((cx + a, z1, cy + b))
            verts.append((cx + a, z2, cy + b))
        bot.append(2 * i)
        top.append(2 * i + 1)
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((bot[i], top[i], top[j], bot[j]))
    faces.append(tuple(bot))
    faces.append(tuple(reversed(top)))
    return verts, faces


def merge(items):
    """Combine list of (verts, faces) into one (verts, faces)."""
    av, af = [], []
    o = 0
    for v, f in items:
        av.extend(v)
        for face in f:
            af.append(tuple(i + o for i in face))
        o += len(v)
    return av, af


def ensure_collection(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def make_object(name, verts, faces, collection, mat=None,
                recalc_normals=True, flat_shade=True, merge_dist=0.0001):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.validate(verbose=False)
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        mesh.materials.append(mat)
    collection.objects.link(obj)

    if len(mesh.polygons) > 0:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        if merge_dist > 0:
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge_dist)
        if recalc_normals:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()

    if flat_shade:
        for poly in mesh.polygons:
            poly.use_smooth = False
    return obj


def set_origin(obj, world_pos):
    """Move origin to world_pos without moving the geometry visually."""
    delta = obj.matrix_world.translation - Vector(world_pos)
    mesh = obj.data
    for v in mesh.vertices:
        v.co += delta
    obj.matrix_world.translation = Vector(world_pos)
    mesh.update()


# ============================================================================
#  2D RECT DECOMPOSITION
# ============================================================================

def decompose_with_cutouts(rect, cutouts):
    """Rectangle minus N axis-aligned cutouts. Returns list of solid sub-rectangles."""
    rx1, rx2, rz1, rz2 = rect
    if rx2 <= rx1 or rz2 <= rz1:
        return []
    clipped = []
    for cx1, cx2, cz1, cz2 in cutouts:
        x1 = max(cx1, rx1); x2 = min(cx2, rx2)
        z1 = max(cz1, rz1); z2 = min(cz2, rz2)
        if x2 > x1 and z2 > z1:
            clipped.append((x1, x2, z1, z2))
    if not clipped:
        return [rect]
    xs = {rx1, rx2}; zs = {rz1, rz2}
    for x1, x2, z1, z2 in clipped:
        xs.add(x1); xs.add(x2); zs.add(z1); zs.add(z2)
    xs = sorted(xs); zs = sorted(zs)

    out = []
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            x1, x2 = xs[i], xs[i+1]
            z1, z2 = zs[j], zs[j+1]
            if x2 - x1 < 1e-6 or z2 - z1 < 1e-6:
                continue
            cxc, czc = (x1+x2)/2, (z1+z2)/2
            inside = any(cox1 - 1e-6 <= cxc <= cox2 + 1e-6 and
                         coz1 - 1e-6 <= czc <= coz2 + 1e-6
                         for cox1, cox2, coz1, coz2 in clipped)
            if not inside:
                out.append((x1, x2, z1, z2))
    return out


# ============================================================================
#  WALL TOP FUNCTION
# ============================================================================

def wall_top_function(side, props, half_w, half_d):
    """Top edge control points (lx, lz) for a wall."""
    H = props.wall_height
    pitch = radians(props.roof_pitch_deg)
    is_yw = side in ('FRONT', 'BACK')
    half_l = half_w if is_yw else half_d

    if props.roof_type == 'FLAT':
        return [(-half_l, H), (+half_l, H)]
    if props.roof_type == 'GABLE':
        if is_yw:
            ridge_z = H + half_w * tan(pitch)
            return [(-half_l, H), (0.0, ridge_z), (+half_l, H)]
        return [(-half_l, H), (+half_l, H)]
    # SHED
    high_side = props.shed_high_side
    slope_along_x = high_side in ('LEFT', 'RIGHT')
    delta = (2 * half_w if slope_along_x else 2 * half_d) * tan(pitch)
    wall_along_slope = (slope_along_x and is_yw) or (not slope_along_x and not is_yw)
    if wall_along_slope:
        local_pos_high = ((slope_along_x and high_side == 'RIGHT') or
                          (not slope_along_x and high_side == 'BACK'))
        return [(-half_l, H), (+half_l, H + delta)] if local_pos_high \
               else [(-half_l, H + delta), (+half_l, H)]
    if side == high_side:
        return [(-half_l, H + delta), (+half_l, H + delta)]
    return [(-half_l, H), (+half_l, H)]


# ============================================================================
#  WALL → WORLD COORDINATE MAPPING
# ============================================================================

def local_to_world_box(side, lx1, lx2, z1, z2, T, half_w, half_d):
    if side == 'FRONT': return (lx1, lx2, -half_d, -half_d + T, z1, z2)
    if side == 'BACK':  return (lx1, lx2, half_d - T, half_d, z1, z2)
    if side == 'LEFT':  return (-half_w, -half_w + T, lx1, lx2, z1, z2)
    return (half_w - T, half_w, lx1, lx2, z1, z2)  # RIGHT


def local_to_world_pts(side, lx, lz, T, half_w, half_d):
    if side == 'FRONT': return (lx, -half_d, lz),  (lx, -half_d + T, lz)
    if side == 'BACK':  return (lx, half_d, lz),   (lx, half_d - T, lz)
    if side == 'LEFT':  return (-half_w, lx, lz),  (-half_w + T, lx, lz)
    return (half_w, lx, lz), (half_w - T, lx, lz)  # RIGHT


def local_to_world_3d(side, lx, lz, half_w, half_d, depth_offset=0.0):
    """Map a local (lx, lz) wall point to a single 3D world point.
    `depth_offset` extends outward from the wall surface."""
    if side == 'FRONT': return (lx, -half_d - depth_offset, lz)
    if side == 'BACK':  return (lx, +half_d + depth_offset, lz)
    if side == 'LEFT':  return (-half_w - depth_offset, lx, lz)
    return (+half_w + depth_offset, lx, lz)  # RIGHT


# ============================================================================
#  WALL BUILDING (flat geometry with cutouts)
# ============================================================================

def _build_upper_polygon(top_min_z, top_fn, half_l):
    poly = [(-half_l, top_min_z), (+half_l, top_min_z)]
    for lx, lz in reversed(top_fn):
        if poly:
            lpx, lpz = poly[-1]
            if abs(lpx - lx) < 1e-5 and abs(lpz - lz) < 1e-5:
                continue
        poly.append((lx, lz))
    if len(poly) >= 3 and abs(poly[0][0] - poly[-1][0]) < 1e-5 and abs(poly[0][1] - poly[-1][1]) < 1e-5:
        poly.pop()
    return poly


def build_wall(side, props, half_w, half_d, doors_list, windows_list):
    """Build a wall with door + window cutouts. Returns (verts, faces)."""
    is_yw = side in ('FRONT', 'BACK')
    half_l = half_w if is_yw else half_d
    T = props.wall_thickness
    top_fn = wall_top_function(side, props, half_w, half_d)
    top_min_z = min(lz for _, lz in top_fn)

    cutouts = []
    for cx, dw, dh in doors_list:
        cutouts.append((cx - dw / 2, cx + dw / 2, 0.0, dh))
    cutouts.extend(windows_list)

    base_rect = (-half_l, +half_l, 0.0, top_min_z)
    rects = decompose_with_cutouts(base_rect, cutouts)

    items = []
    for lx1, lx2, z1, z2 in rects:
        items.append(box(*local_to_world_box(side, lx1, lx2, z1, z2, T, half_w, half_d)))

    upper_poly = _build_upper_polygon(top_min_z, top_fn, half_l)
    if len(upper_poly) >= 3:
        for i in range(1, len(upper_poly) - 1):
            tri = [upper_poly[0], upper_poly[i], upper_poly[i + 1]]
            v_outer, v_inner = [], []
            for lx, lz in tri:
                wo, wi = local_to_world_pts(side, lx, lz, T, half_w, half_d)
                v_outer.append(wo); v_inner.append(wi)
            v = v_outer + v_inner
            f = [
                (0, 1, 2), (3, 5, 4),
                (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0),
            ]
            items.append((v, f))
    return merge(items) if items else ([], [])


# ============================================================================
#  3D TRAPEZBLECH PROFILE (skin overlay on wall exterior)
# ============================================================================

# One-period trapez profile: list of (frac_along_x, depth_offset)
# Standard "T35"-like: 30%/30%/30%/30% (rise/crest/fall/trough), with smoothing
TRAPEZ_PROFILE = [
    (0.00, 0.0),
    (0.15, 0.0),
    (0.35, 1.0),  # 1.0 = full amplitude (will be scaled)
    (0.65, 1.0),
    (0.85, 0.0),
]


def build_trapez_skin(side, lx1, lx2, z1, z2, half_w, half_d, amplitude, period):
    """Generate a corrugated trapez skin over a wall rectangle.
    Returns (verts, faces) for a one-sided corrugated surface offset outward."""
    width = lx2 - lx1
    if width < period * 0.5:
        return [], []

    n_periods = max(1, round(width / period))
    actual_period = width / n_periods

    # Build x positions and depths
    pts = []
    for i in range(n_periods):
        for frac, depth_factor in TRAPEZ_PROFILE:
            lx = lx1 + (i + frac) * actual_period
            pts.append((lx, depth_factor * amplitude))
    pts.append((lx2, 0.0))  # final trough at right edge

    # 2 verts per X position (top + bottom of rect)
    verts = []
    for lx, depth in pts:
        verts.append(local_to_world_3d(side, lx, z1, half_w, half_d, depth_offset=depth))
        verts.append(local_to_world_3d(side, lx, z2, half_w, half_d, depth_offset=depth))

    faces = []
    for i in range(len(pts) - 1):
        b1, t1 = 2 * i, 2 * i + 1
        b2, t2 = 2 * (i + 1), 2 * (i + 1) + 1
        faces.append((b1, t1, t2, b2))
    return verts, faces


def build_wall_with_trapez_skin(side, props, half_w, half_d, doors_list, windows_list):
    """Build wall + add trapez corrugation skin on top of solid rectangles.
    Returns (wall_verts_faces, skin_verts_faces) — two separate meshes.
    """
    # Standard flat wall
    wall_vf = build_wall(side, props, half_w, half_d, doors_list, windows_list)

    # Compute solid rectangles (same as inside build_wall) to know where to put skin
    is_yw = side in ('FRONT', 'BACK')
    half_l = half_w if is_yw else half_d
    top_fn = wall_top_function(side, props, half_w, half_d)
    top_min_z = min(lz for _, lz in top_fn)

    cutouts = []
    for cx, dw, dh in doors_list:
        cutouts.append((cx - dw / 2, cx + dw / 2, 0.0, dh))
    cutouts.extend(windows_list)
    base_rect = (-half_l, +half_l, 0.0, top_min_z)
    rects = decompose_with_cutouts(base_rect, cutouts)

    skin_items = []
    for lx1, lx2, z1, z2 in rects:
        v, f = build_trapez_skin(side, lx1, lx2, z1, z2, half_w, half_d,
                                 props.profile_amplitude, props.profile_period)
        if v:
            skin_items.append((v, f))
    skin_vf = merge(skin_items) if skin_items else ([], [])
    return wall_vf, skin_vf


# ============================================================================
#  ROOF
# ============================================================================

def build_gable_slope(sign, props, half_w, half_d, ridge_z):
    pitch = radians(props.roof_pitch_deg)
    H = props.wall_height
    rt = props.roof_thickness
    eo = props.roof_overhang_eaves
    go = props.roof_overhang_gable

    eave_x = sign * (half_w + eo)
    eave_z = H - eo * tan(pitch)
    y_min = -half_d - go; y_max = +half_d + go
    nx = sign * sin(pitch); nz = cos(pitch)

    t_em = (eave_x, y_min, eave_z); t_eM = (eave_x, y_max, eave_z)
    t_rm = (0.0, y_min, ridge_z);    t_rM = (0.0, y_max, ridge_z)

    def off(p): return (p[0] - nx * rt, p[1], p[2] - nz * rt)
    b_em, b_eM, b_rm, b_rM = off(t_em), off(t_eM), off(t_rm), off(t_rM)
    v = [t_em, t_eM, t_rM, t_rm, b_em, b_eM, b_rM, b_rm]
    f = [(0, 1, 2, 3), (4, 7, 6, 5),
         (0, 3, 7, 4), (1, 5, 6, 2),
         (0, 4, 5, 1), (3, 2, 6, 7)]
    return v, f


def build_shed_roof(props, half_w, half_d):
    pitch = radians(props.roof_pitch_deg)
    H = props.wall_height
    rt = props.roof_thickness
    eo = props.roof_overhang_eaves
    go = props.roof_overhang_gable
    high_side = props.shed_high_side

    if high_side in ('LEFT', 'RIGHT'):
        delta = 2 * half_w * tan(pitch)
        if high_side == 'RIGHT':
            low_x, high_x, nx = -half_w - eo, +half_w + eo, -sin(pitch)
        else:
            low_x, high_x, nx = +half_w + eo, -half_w - eo, +sin(pitch)
        ny = 0.0
        low_z = H - eo * tan(pitch); high_z = H + delta + eo * tan(pitch)
        y_min, y_max = -half_d - go, +half_d + go
        t_lm = (low_x, y_min, low_z);    t_lM = (low_x, y_max, low_z)
        t_hm = (high_x, y_min, high_z);  t_hM = (high_x, y_max, high_z)
    else:
        delta = 2 * half_d * tan(pitch)
        if high_side == 'BACK':
            low_y, high_y, ny = -half_d - eo, +half_d + eo, -sin(pitch)
        else:
            low_y, high_y, ny = +half_d + eo, -half_d - eo, +sin(pitch)
        nx = 0.0
        low_z = H - eo * tan(pitch); high_z = H + delta + eo * tan(pitch)
        x_min, x_max = -half_w - go, +half_w + go
        t_lm = (x_min, low_y, low_z);   t_lM = (x_max, low_y, low_z)
        t_hm = (x_min, high_y, high_z); t_hM = (x_max, high_y, high_z)
    nz = cos(pitch)

    def off(p): return (p[0] - nx * rt, p[1] - ny * rt, p[2] - nz * rt)
    v = [t_lm, t_lM, t_hM, t_hm, off(t_lm), off(t_lM), off(t_hM), off(t_hm)]
    f = [(0, 1, 2, 3), (4, 7, 6, 5),
         (0, 3, 7, 4), (1, 5, 6, 2),
         (0, 4, 5, 1), (3, 2, 6, 7)]
    return v, f


def build_flat_roof(props, half_w, half_d):
    H = props.wall_height
    rt = props.roof_thickness
    over = max(props.roof_overhang_eaves, props.roof_overhang_gable)
    return box(-half_w - over, +half_w + over,
               -half_d - over, +half_d + over, H, H + rt)


def build_ridge_cap(props, half_w, half_d, ridge_z):
    cap_w = 0.40
    cap_h = 0.08
    over = props.roof_overhang_gable
    return box(-cap_w / 2, +cap_w / 2,
               -half_d - over, +half_d + over,
               ridge_z - 0.01, ridge_z + cap_h)


def build_gutters(props, half_w, half_d):
    if props.roof_type == 'FLAT':
        return []
    H = props.wall_height
    pitch = radians(props.roof_pitch_deg)
    eo = props.roof_overhang_eaves
    go = props.roof_overhang_gable
    gs = props.gutter_size
    eave_z = H - eo * tan(pitch) if pitch > 0 else H
    items = []
    y_min, y_max = -half_d - go - gs * 0.2, +half_d + go + gs * 0.2
    x_min, x_max = -half_w - go - gs * 0.2, +half_w + go + gs * 0.2

    if props.roof_type == 'GABLE':
        for sign in (-1, +1):
            gx = sign * (half_w + eo + gs * 0.4)
            v, f = cylinder(gx, eave_z, y_min, y_max, gs * 0.5, segments=10, axis='Y')
            items.append((v, f))
    elif props.roof_type == 'SHED':
        hs = props.shed_high_side
        if hs == 'RIGHT':
            v, f = cylinder(-half_w - eo - gs * 0.4, eave_z, y_min, y_max, gs * 0.5, 10, axis='Y'); items.append((v, f))
        elif hs == 'LEFT':
            v, f = cylinder(+half_w + eo + gs * 0.4, eave_z, y_min, y_max, gs * 0.5, 10, axis='Y'); items.append((v, f))
        elif hs == 'BACK':
            v, f = cylinder(-half_d - eo - gs * 0.4, eave_z, x_min, x_max, gs * 0.5, 10, axis='X'); items.append((v, f))
        elif hs == 'FRONT':
            v, f = cylinder(+half_d + eo + gs * 0.4, eave_z, x_min, x_max, gs * 0.5, 10, axis='X'); items.append((v, f))
    return items


# ============================================================================
#  DOORS
# ============================================================================

def door_x_positions(count, length, dw):
    if count <= 0: return []
    if count == 1: return [0.0]
    margin = max(0.5, dw * 0.3)
    total = count * dw
    avail = length - 2 * margin - total
    if avail < 0:
        margin = max(0.1, (length - total) / (count + 1))
        avail = max(0.0, length - 2 * margin - total)
    gap = avail / (count - 1)
    cursor = -length / 2 + margin + dw / 2
    out = []
    for _ in range(count):
        out.append(cursor); cursor += dw + gap
    return out


def build_door_panel_box(side, cx, dw, z1, z2, half_w, half_d, T, depth=0.06):
    if side in ('FRONT', 'BACK'):
        y_c = -half_d + T / 2 if side == 'FRONT' else +half_d - T / 2
        return box(cx - dw/2, cx + dw/2,
                   y_c - depth/2, y_c + depth/2, z1, z2)
    x_c = -half_w + T / 2 if side == 'LEFT' else +half_w - T / 2
    return box(x_c - depth/2, x_c + depth/2,
               cx - dw/2, cx + dw/2, z1, z2)


def door_panel_origin(side, cx, dw, z, half_w, half_d, T):
    if side == 'FRONT': return Vector((cx, -half_d + T/2, z))
    if side == 'BACK':  return Vector((cx, +half_d - T/2, z))
    if side == 'LEFT':  return Vector((-half_w + T/2, cx, z))
    return Vector((+half_w - T/2, cx, z))


# ============================================================================
#  WINDOWS
# ============================================================================

def window_cutout_for_side(side, props, half_w, half_d):
    enabled = {
        'FRONT': props.window_front, 'BACK': props.window_back,
        'LEFT': props.window_left, 'RIGHT': props.window_right,
    }[side]
    if not enabled:
        return []
    is_yw = side in ('FRONT', 'BACK')
    half_l = half_w if is_yw else half_d
    margin = props.window_margin
    z1 = props.window_z
    z2 = z1 + props.window_height
    if z2 >= props.wall_height: return []
    if 2 * margin >= 2 * half_l - 0.2: return []
    return [(-half_l + margin, +half_l - margin, z1, z2)]


def build_window_glass(side, lx1, lx2, z1, z2, half_w, half_d, T, glass_depth=0.02):
    if side in ('FRONT', 'BACK'):
        y_c = -half_d + T/2 if side == 'FRONT' else +half_d - T/2
        return box(lx1, lx2, y_c - glass_depth/2, y_c + glass_depth/2, z1, z2)
    x_c = -half_w + T/2 if side == 'LEFT' else +half_w - T/2
    return box(x_c - glass_depth/2, x_c + glass_depth/2, lx1, lx2, z1, z2)


# ============================================================================
#  PLINTH (Sockel)
# ============================================================================

def build_plinth(props, half_w, half_d):
    H = props.plinth_height
    if H <= 0: return []
    T = props.wall_thickness + props.plinth_offset
    po = props.plinth_offset
    items = [
        box(-half_w - po, +half_w + po, -half_d - po, -half_d + T - po, 0, H),
        box(-half_w - po, +half_w + po, +half_d - T + po, +half_d + po, 0, H),
        box(-half_w - po, -half_w + T - po, -half_d + T - po, +half_d - T + po, 0, H),
        box(+half_w - T + po, +half_w + po, -half_d + T - po, +half_d - T + po, 0, H),
    ]
    return items


# ============================================================================
#  COLUMNS
# ============================================================================

def build_columns(props, half_w, half_d):
    if not props.create_columns: return []
    cs = props.column_size
    cn = props.column_count
    H = props.wall_height
    margin = props.wall_thickness + cs

    if cn == 1:
        ys = [0.0]
    else:
        avail = 2 * half_d - 2 * margin
        if avail <= 0: return []
        spacing = avail / (cn - 1)
        ys = [-half_d + margin + i * spacing for i in range(cn)]

    return [box(-cs/2, +cs/2, py - cs/2, py + cs/2, 0.0, H) for py in ys]
