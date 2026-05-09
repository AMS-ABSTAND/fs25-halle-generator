"""Material-Erzeugung mit Procedural Shader Nodes oder Bild-Texturen.

Wenn ein Texture-Pack-Pfad gesetzt ist, werden für jedes Material Bilder
mit der Namenskonvention `<style_key_lowercase>_basecolor.png` etc. geladen.
Sonst (oder wenn die Bilder fehlen) Procedural-Fallback mit Wave/Noise/Brick-
Nodes.

Erkannte Suffixe (case-insensitive):
    Base color:  _basecolor, _albedo, _diffuse, _color, _diff, _col
    Normal:      _normal, _nrm, _norm, _n
    Roughness:   _roughness, _rough, _r
    Metallic:    _metallic, _metal, _m
    AO:          _ao, _ambientocclusion
"""

import os
import bpy

from . import presets


def _color_scale(color, factor):
    """Scale color, clamped to [0, 1]."""
    return tuple(min(max(c * factor, 0.0), 1.0) for c in color) + (1.0,)


def _make_base_material(name, color, roughness, metallic,
                        alpha=1.0, transmission=0.0):
    """Create a fresh Principled BSDF material. Wipes existing nodes if material reused."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True

    nt = mat.node_tree
    nt.nodes.clear()

    output = nt.nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    nt.links.new(bsdf.outputs[0], output.inputs[0])

    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    if alpha < 1.0 and "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = 'BLEND'
    for tname in ("Transmission Weight", "Transmission"):
        if tname in bsdf.inputs:
            bsdf.inputs[tname].default_value = transmission
            break

    return mat, bsdf, nt


def _add_tex_coord(nt, x=-1000, y=0):
    """Add a Texture Coordinate node. Returns the node."""
    n = nt.nodes.new("ShaderNodeTexCoord")
    n.location = (x, y)
    return n


def _add_mapping(nt, x=-800, y=0, scale=(1, 1, 1), rotation=(0, 0, 0)):
    n = nt.nodes.new("ShaderNodeMapping")
    n.location = (x, y)
    n.inputs['Scale'].default_value = scale
    n.inputs['Rotation'].default_value = rotation
    return n


def _add_color_ramp(nt, x=0, y=0, color1=(0,0,0,1), color2=(1,1,1,1),
                    pos1=0.0, pos2=1.0):
    n = nt.nodes.new("ShaderNodeValToRGB")
    n.location = (x, y)
    r = n.color_ramp
    r.elements[0].position = pos1
    r.elements[0].color = color1
    r.elements[1].position = pos2
    r.elements[1].color = color2
    return n


# ============================================================================
#  PATTERN APPLIERS
# ============================================================================

def _apply_trapez(mat, bsdf, nt, color, period=0.33, horizontal=False):
    """Vertical (or horizontal) trapezblech stripes."""
    tc = _add_tex_coord(nt, -1000, 0)
    rot = (0, 0, 1.5708) if horizontal else (0, 0, 0)
    mp = _add_mapping(nt, -800, 0, scale=(1.0/period, 1.0/period, 1.0), rotation=rot)
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])

    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.location = (-500, 0)
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    wave.wave_profile = 'SAW'  # smoother than SQR
    wave.inputs['Scale'].default_value = 1.0
    wave.inputs['Distortion'].default_value = 0.0
    wave.inputs['Detail'].default_value = 0.0
    wave.inputs['Detail Scale'].default_value = 1.0
    nt.links.new(mp.outputs['Vector'], wave.inputs['Vector'])

    ramp = _add_color_ramp(nt, -200, 0,
        color1=_color_scale(color, 0.55),
        color2=_color_scale(color, 1.05),
        pos1=0.30, pos2=0.70)
    nt.links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])


def _apply_wood(mat, bsdf, nt, color):
    """Wood grain via stretched noise."""
    tc = _add_tex_coord(nt, -1200, 0)
    # Stretch UVs along V to make grain elongated vertically (planks running vertical)
    mp = _add_mapping(nt, -1000, 0, scale=(0.15, 4.0, 1.0))
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-700, 0)
    noise.inputs['Scale'].default_value = 5.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.6
    if 'Distortion' in noise.inputs:
        noise.inputs['Distortion'].default_value = 1.5
    nt.links.new(mp.outputs['Vector'], noise.inputs['Vector'])

    ramp = _add_color_ramp(nt, -400, 0,
        color1=_color_scale(color, 0.55),
        color2=_color_scale(color, 1.20),
        pos1=0.35, pos2=0.70)
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    # Add a wave for plank seams
    plank_tc = _add_tex_coord(nt, -1200, -300)
    plank_mp = _add_mapping(nt, -1000, -300, scale=(5.0, 0.1, 1.0))  # planks ~20cm wide
    nt.links.new(plank_tc.outputs['UV'], plank_mp.inputs['Vector'])

    plank_wave = nt.nodes.new("ShaderNodeTexWave")
    plank_wave.location = (-700, -300)
    plank_wave.wave_type = 'BANDS'
    plank_wave.bands_direction = 'X'
    plank_wave.wave_profile = 'SAW'  # 'SQR' wurde in Blender 4.x entfernt
    plank_wave.inputs['Distortion'].default_value = 0.0
    nt.links.new(plank_mp.outputs['Vector'], plank_wave.inputs['Vector'])

    plank_ramp = _add_color_ramp(nt, -400, -300,
        color1=(0.05, 0.04, 0.02, 1),
        color2=(1.0, 1.0, 1.0, 1),
        pos1=0.0, pos2=0.05)
    nt.links.new(plank_wave.outputs['Fac'], plank_ramp.inputs['Fac'])

    # Multiply plank seams onto wood color
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.location = (-100, 0)
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = 0.7
    nt.links.new(ramp.outputs['Color'], mix.inputs['Color1'])
    nt.links.new(plank_ramp.outputs['Color'], mix.inputs['Color2'])
    nt.links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])


def _apply_concrete(mat, bsdf, nt, color):
    """Sichtbeton: subtle noise variation."""
    tc = _add_tex_coord(nt, -800, 0)
    mp = _add_mapping(nt, -600, 0, scale=(0.5, 0.5, 1.0))
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 8.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.7
    nt.links.new(mp.outputs['Vector'], noise.inputs['Vector'])

    ramp = _add_color_ramp(nt, -150, 0,
        color1=_color_scale(color, 0.85),
        color2=_color_scale(color, 1.10),
        pos1=0.30, pos2=0.70)
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])


def _apply_clinker(mat, bsdf, nt, color):
    """Klinker / brick pattern via Brick Texture node."""
    tc = _add_tex_coord(nt, -700, 0)

    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.location = (-400, 0)
    brick.offset = 0.5
    brick.offset_frequency = 2
    brick.squash = 1.0
    brick.squash_frequency = 2
    c1 = (color[0], color[1], color[2], 1.0)
    c2 = _color_scale(color, 0.7)
    brick.inputs['Color1'].default_value = c1
    brick.inputs['Color2'].default_value = c2
    brick.inputs['Mortar'].default_value = (0.55, 0.55, 0.55, 1.0)
    brick.inputs['Scale'].default_value = 5.0
    brick.inputs['Mortar Size'].default_value = 0.025
    brick.inputs['Mortar Smooth'].default_value = 0.1
    brick.inputs['Bias'].default_value = 0.0
    brick.inputs['Brick Width'].default_value = 0.5
    brick.inputs['Row Height'].default_value = 0.25
    nt.links.new(tc.outputs['UV'], brick.inputs['Vector'])
    nt.links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])


def _apply_riffel(mat, bsdf, nt, color):
    """Riffelblech: diamond pattern via Voronoi (45° rotated)."""
    tc = _add_tex_coord(nt, -1000, 0)
    mp = _add_mapping(nt, -800, 0, scale=(20, 20, 1), rotation=(0, 0, 0.7854))
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])

    voro = nt.nodes.new("ShaderNodeTexVoronoi")
    voro.location = (-500, 0)
    voro.feature = 'F1'
    voro.distance = 'CHEBYCHEV'
    voro.inputs['Scale'].default_value = 1.0
    voro.inputs['Randomness'].default_value = 0.0  # regular grid
    nt.links.new(mp.outputs['Vector'], voro.inputs['Vector'])

    ramp = _add_color_ramp(nt, -200, 0,
        color1=_color_scale(color, 0.65),
        color2=_color_scale(color, 1.05),
        pos1=0.30, pos2=0.55)
    nt.links.new(voro.outputs['Distance'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])


def _apply_stehfalz(mat, bsdf, nt, color):
    """Stehfalz: wide vertical seams (every ~50-60cm)."""
    tc = _add_tex_coord(nt, -1000, 0)
    mp = _add_mapping(nt, -800, 0, scale=(2.0, 1.0, 1.0))
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])

    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.location = (-500, 0)
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    wave.wave_profile = 'SAW'  # 'SQR' wurde in Blender 4.x entfernt
    wave.inputs['Scale'].default_value = 1.0
    wave.inputs['Distortion'].default_value = 0.0
    nt.links.new(mp.outputs['Vector'], wave.inputs['Vector'])

    ramp = _add_color_ramp(nt, -200, 0,
        color1=_color_scale(color, 0.55),
        color2=_color_scale(color, 1.05),
        pos1=0.0, pos2=0.06)  # only thin seam darkens
    nt.links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])


def _apply_tiles(mat, bsdf, nt, color):
    """Roof tiles: brick texture with narrow tile shape."""
    tc = _add_tex_coord(nt, -700, 0)

    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.location = (-400, 0)
    brick.offset = 0.5
    brick.offset_frequency = 2
    c1 = (color[0], color[1], color[2], 1.0)
    c2 = _color_scale(color, 0.75)
    brick.inputs['Color1'].default_value = c1
    brick.inputs['Color2'].default_value = c2
    brick.inputs['Mortar'].default_value = (0.15, 0.10, 0.08, 1.0)
    brick.inputs['Scale'].default_value = 8.0
    brick.inputs['Mortar Size'].default_value = 0.015
    brick.inputs['Brick Width'].default_value = 0.4
    brick.inputs['Row Height'].default_value = 0.35
    nt.links.new(tc.outputs['UV'], brick.inputs['Vector'])
    nt.links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])


def _apply_paint(mat, bsdf, nt, color):
    """Painted surface: very subtle noise."""
    # Just keep the flat color, no nodes added (BSDF already has the color)
    pass


PATTERN_DISPATCH = {
    presets.PATTERN_FLAT:     None,
    presets.PATTERN_TRAPEZ:   lambda m, b, n, c: _apply_trapez(m, b, n, c, period=0.33, horizontal=False),
    presets.PATTERN_TRAPEZ_H: lambda m, b, n, c: _apply_trapez(m, b, n, c, period=0.30, horizontal=True),
    presets.PATTERN_WOOD:     _apply_wood,
    presets.PATTERN_CONCRETE: _apply_concrete,
    presets.PATTERN_CLINKER:  _apply_clinker,
    presets.PATTERN_RIFFEL:   _apply_riffel,
    presets.PATTERN_STEHFALZ: _apply_stehfalz,
    presets.PATTERN_TILES:    _apply_tiles,
    presets.PATTERN_PAINT:    _apply_paint,
}


# ============================================================================
#  PUBLIC API
# ============================================================================

def make_material(name, color, roughness=0.7, metallic=0.0,
                  alpha=1.0, transmission=0.0,
                  pattern=presets.PATTERN_FLAT, use_procedural=True):
    """Create or update a named material.
    If `use_procedural` and pattern != FLAT, attaches procedural shader nodes.
    """
    mat, bsdf, nt = _make_base_material(name, color, roughness, metallic,
                                        alpha, transmission)
    if use_procedural and pattern != presets.PATTERN_FLAT:
        applier = PATTERN_DISPATCH.get(pattern)
        if applier:
            applier(mat, bsdf, nt, color)
    return mat


def make_material_from_preset(name, preset_list, key, use_procedural=True):
    """Convenience: create material from a preset list + key."""
    color, roughness, metallic, pattern = presets.lookup(preset_list, key)
    return make_material(name, color, roughness, metallic,
                         pattern=pattern, use_procedural=use_procedural)


# ============================================================================
#  TEXTURE PACK LOADING
# ============================================================================

_BASECOLOR_SUFFIXES = ['_basecolor', '_albedo', '_diffuse', '_color', '_diff', '_col']
_NORMAL_SUFFIXES    = ['_normal', '_nrm', '_norm', '_n']
_ROUGHNESS_SUFFIXES = ['_roughness', '_rough', '_r']
_METALLIC_SUFFIXES  = ['_metallic', '_metal', '_m']
_AO_SUFFIXES        = ['_ao', '_ambientocclusion', '_occlusion']
_IMAGE_EXTS         = ['.png', '.jpg', '.jpeg', '.tga', '.tif', '.tiff', '.exr']


def _find_texture(directory, key, suffixes):
    """Look for `<key>_<suffix>.<ext>` (case-insensitive) in directory."""
    if not directory or not os.path.isdir(directory):
        return None
    key_lower = key.lower()
    try:
        files = os.listdir(directory)
    except OSError:
        return None
    files_lower = {f.lower(): f for f in files}
    for suffix in suffixes:
        for ext in _IMAGE_EXTS:
            candidate = (key_lower + suffix + ext).lower()
            if candidate in files_lower:
                return os.path.join(directory, files_lower[candidate])
    return None


def _load_image(path):
    """Load image into Blender, reuse if already loaded."""
    img = bpy.data.images.load(path, check_existing=True)
    return img


def make_material_with_textures(name, preset_list, key, texture_dir,
                                use_procedural_fallback=True):
    """Build a PBR material from images in `texture_dir`. Files named
    `<key_lowercase>_<map>.<ext>` are auto-detected. Falls back to procedural
    if no basecolor texture is found."""
    color, roughness, metallic, pattern = presets.lookup(preset_list, key)

    bc_path = _find_texture(texture_dir, key, _BASECOLOR_SUFFIXES)
    if bc_path is None:
        # No texture pack for this style → procedural / flat color fallback
        return make_material(name, color, roughness, metallic,
                             pattern=pattern,
                             use_procedural=use_procedural_fallback)

    # Texture-based PBR material
    mat, bsdf, nt = _make_base_material(name, color, roughness, metallic)

    # Base color
    bc_node = nt.nodes.new("ShaderNodeTexImage")
    bc_node.location = (-500, 200)
    bc_node.image = _load_image(bc_path)
    nt.links.new(bc_node.outputs['Color'], bsdf.inputs['Base Color'])

    # Normal map
    n_path = _find_texture(texture_dir, key, _NORMAL_SUFFIXES)
    if n_path:
        n_node = nt.nodes.new("ShaderNodeTexImage")
        n_node.location = (-700, -100)
        n_img = _load_image(n_path)
        n_img.colorspace_settings.name = 'Non-Color'
        n_node.image = n_img
        nrm = nt.nodes.new("ShaderNodeNormalMap")
        nrm.location = (-300, -100)
        nt.links.new(n_node.outputs['Color'], nrm.inputs['Color'])
        nt.links.new(nrm.outputs['Normal'], bsdf.inputs['Normal'])

    # Roughness
    r_path = _find_texture(texture_dir, key, _ROUGHNESS_SUFFIXES)
    if r_path:
        r_node = nt.nodes.new("ShaderNodeTexImage")
        r_node.location = (-500, -350)
        r_img = _load_image(r_path)
        r_img.colorspace_settings.name = 'Non-Color'
        r_node.image = r_img
        nt.links.new(r_node.outputs['Color'], bsdf.inputs['Roughness'])

    # Metallic
    m_path = _find_texture(texture_dir, key, _METALLIC_SUFFIXES)
    if m_path:
        m_node = nt.nodes.new("ShaderNodeTexImage")
        m_node.location = (-500, -550)
        m_img = _load_image(m_path)
        m_img.colorspace_settings.name = 'Non-Color'
        m_node.image = m_img
        nt.links.new(m_node.outputs['Color'], bsdf.inputs['Metallic'])

    return mat


# ============================================================================
#  UV MAPPING (legacy — kept for backward compat; new code uses uv.apply())
# ============================================================================

def set_uvs_planar(obj, scale=1.0):
    """Planar UV projection per face based on dominant normal axis.
    Legacy entry point — equivalent to ``uv.apply(obj, strategy='PLANAR', scale=scale)``."""
    mesh = obj.data
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    uv = mesh.uv_layers.active.data
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
