# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-07

### Added

- Modular package structure (9 modules: presets, properties, materials,
  geometry, details, generator, operators, ui, init).
- Per-side wall styles: choose a different material for each of the 4 walls.
- Procedural shader nodes for previewing styles without external textures
  (Trapezblech, Holzmaserung, Klinker mit Mörtel, Riffelblech-Diamant,
  Stehfalz, Tonziegel, Sichtbeton).
- 3D-Trapez-Profil: optional real corrugation geometry as a skin overlay,
  generated only on TRAPEZ_*-styled walls.
- `blender_manifest.toml` for compatibility with Blender 4.2+ extension system.
- `make_zip.py` build script for installable releases.
- 8-configuration smoke test suite (test_addon.py).

### Changed

- Material naming now includes the style key (`Halle_Wall_WOOD_DARK`).
- UI panel reorganized with collapsible sections.

## [0.3.0]

### Added

- Style preset system for walls, roof, doors, plinth.
- 16 wall styles, 9 roof styles, 8 door styles, 7 plinth styles.

## [0.2.0]

### Added

- Pultdach (shed roof) with selectable high side.
- Lichtbänder (windows) on all 4 sides.
- Multi-side door support with per-side counts.
- Sectional doors with per-panel origin for animation.
- Concrete plinth.
- Eaves gutters.
- Ridge cap for gable roofs.
- Interior details: workbench, tool wall, diesel tank, compressor,
  fire extinguisher.
- Planar UV mapping.

## [0.1.0]

### Added

- Initial single-file addon.
- Gable and flat roofs.
- Rectangular walls with door cutouts.
- Floor slab.
- Single-side doors.
- Basic columns.
