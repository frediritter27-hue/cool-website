# Fang-style 9 Putter — Circle-F edition (MYP Personal Project)

A 1:1, 3D-printable **fang-style high-MOI mallet putter head**, modelled on the
Scotty Cameron Phantom 9 look from the reference photos: two large **windows cut
through the wings** (the "gaps"), a central spine carrying the crown sight line,
rounded rear fang corners with a shallow centre notch, and a flowing **heel
neck**. High perimeter weighting = a forgiving, stable putter.

**Trademark-free:** no Scotty Cameron / Titleist / Phantom logos, names, or
"FOR TOUR USE ONLY" text. The sole "Circle-T" mark is replaced with a custom
**Circle-F** mark.

> Personal school project — don't sell it or pass it off as a Scotty Cameron.

## Files

| File | Use |
|------|-----|
| `Putter_PhantomStyle_9_CircleF.stl` | Import into **Bambu Studio** (drag & drop). |
| `Putter_PhantomStyle_9_CircleF.3mf` | Bambu-native format (same mesh). |
| `build_putter.py` | Parametric generator — edit numbers/points, re-run. |
| `render_final.py` | Renders the preview images. |
| `preview.png`, `big_top.png`, `big_iso.png` | What it looks like. |

## Key features (the ones that were missing before)

- **Two through-windows** in the wings — the defining "gap" of this head, and
  what makes it high-MOI / forgiving.
- **Winged / fang body** with a shallow rear notch (squared corners, not spikes).
- **Central spine** with a single **sight line** on the crown.
- **Head only — no shaft / neck** (removed on request). Tell me where you want a
  shaft bore and I'll add it.
- **Sole:** two milled discs + central bar + engraved **Circle-F** (paint-fill
  it red), faithful to the owner's photo. The F is mirrored so it reads
  correctly when you look at the sole.
- **Rear sole weight pockets** to add mass / tune MOI.

## Dimensions (1:1, mm)

| Spec | Value |
|------|-------|
| Width (heel↔toe) | ~122 mm |
| Depth (face↔back) | ~118 mm |
| Height (sole↔crown) | 34 mm back, 29 mm at the face |
| Loft | 3.5° |

The shape is built **parametrically** to match the photos (it is not a CAD copy
of the real head). The silhouette is an editable list of points (`half`) at the
top of `build_putter.py`, and every dimension (`D`, `H`, `WFACE`, window size,
neck, …) is a variable — measure your real head and tweak to taste.

## Printing in Bambu Studio

1. Drag the STL onto the plate. Orientation: **crown up / sole on the bed**.
2. PLA (or PETG for durability), 0.16 mm layers, 4+ walls.
3. Supports: light tree/auto for the window undersides; otherwise minimal.
4. Paint-fill the **sight line** and **Circle-F** for contrast.

### Weight

Solid PLA ≈ 210 g; at 30 % infill ≈ 65 g (too light). Print at high infill
and/or pack the two **rear sole pockets** with steel/lead/tungsten + epoxy to
reach a real ~340–360 g putting weight (this also boosts MOI).

## Regenerate

```bash
pip install trimesh manifold3d shapely mapbox_earcut numpy scipy lxml
python3 build_putter.py
python3 render_final.py
```
