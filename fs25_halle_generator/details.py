"""Innendetails: Werkbank, Werkzeugwand, Hofdiesel-Tank, Druckluft-Kompressor, Feuerlöscher.

Alle Details werden als (verts, faces)-Listen zurückgegeben — der Generator
fügt sie zu Mesh-Objekten zusammen.
"""

from . import geometry as geom


def build_workbench(props, half_w, half_d):
    """Werkbank gegen die Rückwand, hinten links."""
    T = props.wall_thickness
    bench_w, bench_d, bench_h = 2.5, 0.7, 0.85
    x1 = -half_w + T + 0.3
    x2 = x1 + bench_w
    y2 = +half_d - T - 0.05
    y1 = y2 - bench_d
    items = []
    items.append(geom.box(x1, x2, y1, y2, 0.0, bench_h))           # Bench top
    items.append(geom.box(x2 - 0.28, x2 - 0.10,
                          y1 + 0.1, y1 + 0.28,
                          bench_h, bench_h + 0.22))                # Vise
    items.append(geom.box(x1, x2, y2 - 0.15, y2,
                          bench_h + 0.4, bench_h + 1.4))           # Tool storage
    return items


def build_tool_wall(props, half_w, half_d):
    """Werkzeugwand: dünne Platte an Linkswand."""
    T = props.wall_thickness
    panel_w = 0.04
    return [geom.box(-half_w + T, -half_w + T + panel_w,
                     +half_d - T - 3.5, +half_d - T - 0.3,
                     1.4, 2.6)]


def build_diesel_tank(props, half_w, half_d):
    """Hofdiesel-Tank: liegender Tank auf 4 Standfüßen."""
    T = props.wall_thickness
    tank_d, tank_l = 1.4, 2.2
    leg_h, leg_w = 0.30, 0.10
    cx = +half_w - T - tank_d / 2 - 0.2
    cy = -half_d + T + 0.5 + tank_l / 2
    z_c = leg_h + tank_d / 2
    items = []
    v, f = geom.cylinder(cx, z_c, cy - tank_l/2, cy + tank_l/2,
                         tank_d / 2, segments=20, axis='Y')
    items.append((v, f))
    for sx in (-1, +1):
        for sy in (-1, +1):
            lx = cx + sx * (tank_d/2 - 0.15) - leg_w/2
            ly = cy + sy * (tank_l/2 - 0.20) - leg_w/2
            items.append(geom.box(lx, lx + leg_w, ly, ly + leg_w, 0.0, leg_h))
    items.append(geom.box(cx - 0.15, cx + 0.15,
                          cy - 0.15, cy + 0.15,
                          leg_h + tank_d, leg_h + tank_d + 0.45))
    return items


def build_compressor(props, half_w, half_d):
    """Druckluft-Kompressor: liegender Tank + Motor obendrauf."""
    T = props.wall_thickness
    comp_w, comp_d, comp_h = 0.5, 1.0, 0.5
    x2 = +half_w - T - 0.2
    x1 = x2 - comp_w
    y2 = +half_d - T - 0.2
    y1 = y2 - comp_d
    y_c = (y1 + y2) / 2
    z_c = comp_h / 2
    items = []
    v, f = geom.cylinder(y_c, z_c, x1, x2, comp_h / 2, segments=16, axis='X')
    items.append((v, f))
    items.append(geom.box(x1 + 0.05, x1 + 0.45,
                          y_c - 0.25, y_c + 0.25,
                          comp_h, comp_h + 0.45))
    return items


def build_fire_extinguisher(props, half_w, half_d):
    """Feuerlöscher an der Wand neben dem Tor."""
    T = props.wall_thickness
    cx = -half_w + T + 0.3
    cy = -half_d + T + 0.4
    items = []
    v, f = geom.cylinder(cx, cy, 0.5, 1.1, 0.08, segments=12, axis='Z')
    items.append((v, f))
    items.append(geom.box(cx - 0.05, cx + 0.05,
                          cy - 0.10, cy - 0.05,
                          0.7, 0.95))
    return items
