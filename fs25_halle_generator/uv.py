"""UV-Mapping-Strategien.

Pro Element-Typ wird die passende Projektion gewählt:
  WALL          → U entlang Wandlänge, V Höhe (texture-konsistent über Wände)
  GABLE_SLOPE   → U entlang First (Y), V entlang Schräge Eave→First
  SHED_SLOPE    → U entlang Trauf, V entlang Schräge (high_side bestimmt Richtung)
  FLAT_ROOF     → planar XY (für Flachdach)
  FLOOR         → planar XY
  CYLINDER      → angulär um Achse (U), axial (V) — für Tank/Rinne
  PLANAR        → world-planar pro Face (Fallback / cube-projection-like)

Verwendung:
    from . import uv
    uv.apply(obj, strategy='WALL', scale=1.0, side='FRONT')
"""

import math


def _ensure_uv_layer(obj):
    mesh = obj.data
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    return mesh, mesh.uv_layers.active.data


# ----------------------------------------------------------------------------
def _apply_planar(obj, scale):
    """World-planar projection — chooses XY/YZ/XZ per face based on dominant normal."""
    mesh, uv = _ensure_uv_layer(obj)
    for poly in mesh.polygons:
        n = poly.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for li in poly.loop_indices:
            v = mesh.vertices[mesh.loops[li].vertex_index].co
            if az >= ax and az >= ay:
                uv[li].uv = (v.x * scale, v.y * scale)
            elif ax >= ay:
                uv[li].uv = (v.y * scale, v.z * scale)
            else:
                uv[li].uv = (v.x * scale, v.z * scale)


# ----------------------------------------------------------------------------
def _apply_wall(obj, scale, side):
    """Wall-local UV: U entlang Wandlänge, V Höhe.
    Texture liest von außen betrachtet konsistent von links nach rechts."""
    mesh, uv = _ensure_uv_layer(obj)
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            v = mesh.vertices[mesh.loops[li].vertex_index].co
            if side == 'FRONT':
                u_val, v_val = v.x, v.z
            elif side == 'BACK':
                # Mirror so texture isn't backwards when seen from outside
                u_val, v_val = -v.x, v.z
            elif side == 'LEFT':
                u_val, v_val = v.y, v.z
            elif side == 'RIGHT':
                u_val, v_val = -v.y, v.z
            else:
                u_val, v_val = v.x, v.z
            uv[li].uv = (u_val * scale, v_val * scale)


# ----------------------------------------------------------------------------
def _apply_gable_slope(obj, scale, sign, eave_x, eave_z, pitch_rad):
    """Gable-Dachschräge: V folgt der Schräge (Eave → First),
    U läuft entlang des Firsts (Y-Achse)."""
    mesh, uv = _ensure_uv_layer(obj)
    nx = -sign * math.cos(pitch_rad)
    nz = math.sin(pitch_rad)
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            v = mesh.vertices[mesh.loops[li].vertex_index].co
            v_dist = (v.x - eave_x) * nx + (v.z - eave_z) * nz
            uv[li].uv = (v.y * scale, v_dist * scale)


# ----------------------------------------------------------------------------
def _apply_shed_slope(obj, scale, props, half_w, half_d):
    """Pultdach: Slope-Richtung hängt von shed_high_side ab."""
    mesh, uv = _ensure_uv_layer(obj)
    pitch = math.radians(props.roof_pitch_deg)
    H = props.wall_height
    eo = props.roof_overhang_eaves
    high_side = props.shed_high_side
    low_z = H - eo * math.tan(pitch)

    if high_side in ('LEFT', 'RIGHT'):
        low_x = -half_w - eo if high_side == 'RIGHT' else +half_w + eo
        sgn = +1 if high_side == 'RIGHT' else -1
        nx, nz = sgn * math.cos(pitch), math.sin(pitch)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                v = mesh.vertices[mesh.loops[li].vertex_index].co
                v_dist = (v.x - low_x) * nx + (v.z - low_z) * nz
                uv[li].uv = (v.y * scale, v_dist * scale)
    else:
        low_y = -half_d - eo if high_side == 'BACK' else +half_d + eo
        sgn = +1 if high_side == 'BACK' else -1
        ny, nz = sgn * math.cos(pitch), math.sin(pitch)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                v = mesh.vertices[mesh.loops[li].vertex_index].co
                v_dist = (v.y - low_y) * ny + (v.z - low_z) * nz
                uv[li].uv = (v.x * scale, v_dist * scale)


# ----------------------------------------------------------------------------
def _apply_flat_xy(obj, scale):
    """Floor / Flachdach: einfache XY-Projektion."""
    mesh, uv = _ensure_uv_layer(obj)
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            v = mesh.vertices[mesh.loops[li].vertex_index].co
            uv[li].uv = (v.x * scale, v.y * scale)


# ----------------------------------------------------------------------------
def _apply_cylinder(obj, scale, axis='Y'):
    """Cylindrical projection — U geht 0..1 einmal rum, V axial in Welt-Einheiten."""
    mesh, uv = _ensure_uv_layer(obj)
    if not mesh.vertices:
        return
    cx = sum(v.co.x for v in mesh.vertices) / len(mesh.vertices)
    cy = sum(v.co.y for v in mesh.vertices) / len(mesh.vertices)
    cz = sum(v.co.z for v in mesh.vertices) / len(mesh.vertices)
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            v = mesh.vertices[mesh.loops[li].vertex_index].co
            if axis == 'Y':
                angle = math.atan2(v.x - cx, v.z - cz)
                axial = v.y - cy
            elif axis == 'X':
                angle = math.atan2(v.y - cy, v.z - cz)
                axial = v.x - cx
            else:  # Z
                angle = math.atan2(v.y - cy, v.x - cx)
                axial = v.z - cz
            u = (angle / (2 * math.pi)) + 0.5
            uv[li].uv = (u, axial * scale)


# ============================================================================
#  PUBLIC API
# ============================================================================

def apply(obj, strategy='PLANAR', scale=1.0, **params):
    """Dispatch to the right UV strategy.

    Strategies:
        'PLANAR'      — world-planar per face (default fallback)
        'WALL'        — needs side='FRONT'/'BACK'/'LEFT'/'RIGHT'
        'GABLE_SLOPE' — needs sign=-1/+1, eave_x, eave_z, pitch_rad
        'SHED_SLOPE'  — needs props, half_w, half_d
        'FLAT_XY'     — for floors and flat roofs
        'CYLINDER'    — needs axis='X'/'Y'/'Z'
    """
    if strategy == 'WALL':
        _apply_wall(obj, scale, side=params['side'])
    elif strategy == 'GABLE_SLOPE':
        _apply_gable_slope(obj, scale,
                           sign=params['sign'],
                           eave_x=params['eave_x'],
                           eave_z=params['eave_z'],
                           pitch_rad=params['pitch_rad'])
    elif strategy == 'SHED_SLOPE':
        _apply_shed_slope(obj, scale,
                          props=params['props'],
                          half_w=params['half_w'],
                          half_d=params['half_d'])
    elif strategy == 'FLAT_XY':
        _apply_flat_xy(obj, scale)
    elif strategy == 'CYLINDER':
        _apply_cylinder(obj, scale, axis=params.get('axis', 'Y'))
    else:
        _apply_planar(obj, scale)
