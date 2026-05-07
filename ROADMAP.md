# Roadmap

Geplante Entwicklungsphasen für den FS25 Halle Generator.
Reihenfolge ist nicht in Stein gemeißelt — Issues und Pull Requests können
das umpriorisieren.

## Phase 1 — Polish (v1.1)

Kleinere Verbesserungen am bestehenden Code.

- [ ] **Hauptobjekt-Empty als Parent**: alle erzeugten Objekte hängen unter
      einem zentralen `Halle_Root` Empty. Sauberer Transform-Handle für FS25
      Placeables.
- [ ] **Slope-aligned UV** für Dachschrägen statt planar (XY-Projektion).
      Damit Trapezblech-Texturen am Dach vom Trauf zum First laufen.
- [ ] **Mullions / Sprossen** in Lichtbändern: vertikale Streben zwischen
      Glas-Segmenten, alle 1–2 m.
- [ ] **Fenster-Rahmen**: dünner Aluminium-Rahmen rund um das Lichtband.
- [ ] **Custom Color Mode**: in jedem Style-Dropdown die Option "Eigene Farbe"
      mit `FloatVectorProperty(subtype='COLOR')`.
- [ ] **Per-Wand UV-Skala**: Holz und Trapezblech haben verschiedene
      Texeldichten — getrennt einstellbar.

## Phase 2 — Animations & FS25-Integration (v1.2)

Was nach dem Generieren noch im GIANTS Editor händisch passieren muss,
direkt im Blender-Output mitliefern.

- [ ] **Tor-Animations-Keyframes**: Sektionaltor-Lamellen-Animation als
      fertige Action — Lamellen heben sich, kippen auf Schiene.
      Entweder in Blender als Action oder als FS25-XML-Schnipsel.
- [ ] **GIANTS User Attributes** als Blender Custom Properties direkt setzen:
      `movingPart`, `collision`, `decalLayer`, `castsShadowMap`. So entfällt
      Nacharbeit im GIANTS Editor.
- [ ] **Auto-Export-Hook**: Knopf "Halle generieren + I3D exportieren" der
      direkt den GIANTS-Exporter aufruft.
- [ ] **Collision-Mesh verbessern**: aktuell Box → optional vereinfachtes
      Convex-Hull pro Wand-Segment.
- [ ] **FS25-Templates**: Presets für Standardgrößen
      (`Kleine Werkstatt 12x8`, `Maschinenhalle 24x18`, `Lagerhalle 40x20`).

## Phase 3 — Mehr Variety (v1.3)

Mehr Stile, mehr Geometrie-Varianten.

- [ ] **3D-Profil für Holz-Wände**: vertikale Brett-Vertiefungen alle 20 cm.
- [ ] **3D-Profil für Klinker**: leichte Mauerwerk-Bumps.
- [ ] **Wellblech**-Profil als Alternative zum Trapezblech (sinusoidal).
- [ ] **Stülpschalung**-Wandstil: horizontale, sich überlappende Bretter.
- [ ] **Eternit / Faserzement**-Stil mit großen Plattenrastern.
- [ ] **Mehr Roof-Styles**: Bitumen-Schweißbahn, Gründach, Dachpappe.

## Phase 4 — Outdoor Details (v1.4)

Was außen an einer echten Halle hängt.

- [ ] **Wandlampen** an den Toren (Halogenstrahler-Look).
- [ ] **Notausgang-Schilder** mit grüner Beleuchtung.
- [ ] **Hausnummer-Schild** an der Vorderseite.
- [ ] **Briefkasten** neben der Schlupftür.
- [ ] **Boden-Markierungen** für Stellplätze als Decal-Plane.
- [ ] **Fallrohre** an den Ecken (Anschluss an Dachrinne).

## Phase 5 — Indoor Atmosphere (v2.0)

Mehr Innenleben für Hallen-Mods die das in-game zeigen wollen.

- [ ] **Stehender Doppelwand-Tank** als Alternative zum liegenden.
- [ ] **Hallenheizung**: Dunkelstrahler an der Decke.
- [ ] **Whiteboard / Wartungsplan** an der Wand.
- [ ] **Stundenzähler-Display** Plate.
- [ ] **Werkzeugwand mit Silhouetten**: erkennbare Werkzeug-Umrisse statt
      einer leeren Platte.
- [ ] **Innenwand-Verkleidung**: separates Material für Innenseiten.
- [ ] **Decken**: Sichtbalken bei Holzhalle, Sandwichpaneel bei Industrie.
- [ ] **Bodenstile** Innen: Industrieboden, Estrich, Klinker, Epoxidharz.

## Phase 6 — Tooling & QoL (v2.1)

Tools für Power-User.

- [ ] **Presets speichern und laden** als JSON-Datei. Nutzer kann eigene
      Halle-Configs teilen.
- [ ] **Multilingual UI**: EN/DE Toggle für die Property-Labels.
- [ ] **Preview-Render**-Knopf: rendert die aktuelle Halle mit Cycles in
      einem separaten Fenster.
- [ ] **CI mit GitHub Actions**: bei jedem Push die headless Smoke-Tests
      laufen lassen, Test-Output als Artifact.
- [ ] **Docs-Seite**: Sphinx oder MkDocs basierte Dokumentations-Site.
- [ ] **Auto-Update**: Extension-System nutzt das, wenn als Extension
      installiert.

## Out of scope (vorerst)

Sachen die jemand fragen könnte, aber bewusst nicht im Plan sind.

- Vollwertiger BIM-Editor (das ist ein Blender-Addon-für-Hallen, kein
  Architekturwerkzeug).
- Mehrgeschossige Hallen (Hochregal mit Mezzanine wäre die einzige sinnvolle
  Ausnahme, aber selten in FS25).
- Laufende physikalische Simulation (Fluid für Tank, Cloth für Plane etc.).

## Beitrag leisten

Wenn dich ein Punkt interessiert: Issue auf GitHub aufmachen mit
"Roadmap: Phase X — Punkt Y" als Titel. Pull Requests willkommen,
auch für Sachen die nicht auf der Liste stehen.
