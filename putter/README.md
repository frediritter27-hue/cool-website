# Phantom-style 9 Putter — Circle-F edition (MYP Personal Project)

A 1:1, 3D-printable **high-MOI mallet putter head**, inspired by the
*proportions* of the Scotty Cameron Phantom 9 (loft **3.5°**, lie **70°**,
near-face-balanced, perimeter-weighted mallet).

This is an **original, trademark-free model**:

- ❌ No Scotty Cameron / Titleist / Phantom logos, names, or "FOR TOUR USE ONLY" text.
- ✅ The "Circle-T" mark is replaced with a custom **Circle-F** mark.

> Made for a personal school project. Don't sell it or pass it off as a
> Scotty Cameron — the brand names and logos are trademarked. The shape here is
> a generic mallet built to similar dimensions, which is fine for personal use.

## Files

| File | Use |
|------|-----|
| `Putter_PhantomStyle_9_CircleF.stl` | Import into **Bambu Studio** (drag & drop). |
| `Putter_PhantomStyle_9_CircleF.3mf` | Bambu-native format (same mesh). |
| `build_putter.py` | The parametric generator — edit numbers, re-run, get a new file. |

## Dimensions (1:1, millimetres)

| Spec | Value |
|------|-------|
| Width (heel ↔ toe) | **109 mm** (traced from the photo) |
| Depth (face ↔ back) | **~109 mm** (traced) |
| Height (sole ↔ crown) | **35 mm** (estimated) |
| Loft | 3.5° |
| Lie | 70° |
| Shaft bore | Ø 9.7 mm (fits a 0.370" / 9.4 mm parallel-tip putter shaft + glue gap) |

### How the shape was made (v2)

The silhouette is **traced from the reference photo**, not guessed:

1. `trace_head.py` segments the head from the green background.
2. `trace_clean.py` rotates it upright, removes the hand/shaft, and mirrors the
   clean half (the head is symmetric) → `clean_contour.npy`.
3. `build_footprint.py` smooths + scales it to millimetres → `foot_mm.npy`.
4. `build_putter.py` lofts that outline into a solid with **rounded crown and
   sole edges** (so it looks like a milled head, not a slab) and adds the
   discs, central bar, sight line, Circle-F, shaft bore and weight pockets.

`seg_overlay.png` shows the trace on the photo; `foot_mm.png` shows the final
outline; `v2_views.png` shows the 3D result.

### Accuracy note

The **width (109 mm)** and the **silhouette** are traced from the photo and are
reliable. The **height (35 mm), loft (3.5°) and side profile** are sensible
estimates — they can't be read from a single top/sole view. If you ever want
true 1:1 on those, measure your real head (or shoot a face-on + heel/toe photo)
and edit the parameters at the top of `build_putter.py` (`H`, `R_CROWN`,
`LOFT_DEG`, `LIE_DEG`, `FACE_Y`, …), then re-run.

## Design features (these are what "help you putt better")

- **Open, perimeter-weighted frame** — two through-windows push mass to the
  edges for **high MOI** (more forgiving on off-centre hits).
- **Clean crown** with a **single sight line** for clean aim.
- **Two milled alignment/weight discs + central bar + Circle-F** on the **sole**
  (faithful to the reference photo). Paint-fill the Circle-F red for contrast.
- **Rounded crown & sole edges** (lofted), so it looks like a milled head.
- **Rear weight pockets** (two Ø12 mm blind holes in the sole) — see below.

## Printing in Bambu Studio

1. Drag `Putter_PhantomStyle_9_CircleF.stl` onto the plate.
2. Orientation: it's modelled **sole-down, crown-up** — keep it that way
   (flat sole = great bed adhesion, no supports needed for the top features).
3. Suggested settings:
   - Material: **PLA** (or PETG for more durability).
   - Layer height: 0.16 mm (0.12 mm for a crisper logo).
   - **Walls: 4+, Infill: 30–100%** — see weight note below.
   - Supports: **none** needed in this orientation. The shaft bore prints as a
     clean downward hole.
4. Paint-fill the engraved **sight line** and **Circle-F** with a paint pen for
   contrast (let the print, then wipe paint off the top surface).

### Weight (important!)

A real tour putter head is ~**350 g** (steel). Printed solid in PLA this model
is ~**420 g**; at 30% infill ~**125 g** (too light to putt well). To dial it in:

- Print at **higher infill** (60–100%), **and/or**
- Pack the two **rear sole pockets** with steel/lead/tungsten + epoxy. Putting
  the mass at the back corners both adds weight **and** raises MOI.

Aim for roughly 330–360 g total head weight for a good putting feel.

## Assembling the putter

1. Print the head.
2. Get a **0.370" parallel-tip putter shaft** + grip (cheap online).
3. Cut the shaft to your length (standard ~34"), de-burr the tip.
4. Epoxy the tip into the Ø9.7 mm bore (it enters near centre at 70° lie —
   that's the single-bend, near-face-balanced position).
5. Add tip weights / fill pockets to reach your target head weight.
6. Slide on and glue the grip. Done.

## Regenerating / tweaking the model

```bash
pip install trimesh manifold3d shapely mapbox_earcut numpy scipy lxml
python3 build_putter.py
```

Everything is parametric — head size, loft, lie, port positions, window size,
logo, and weight pockets are all variables near the top of the script.
