#!/usr/bin/env python3
"""
Parametric putter head generator  -  "Phantom-style 9", Circle-F edition
========================================================================

A high-MOI mallet putter head inspired by the *proportions* of the
Scotty Cameron Phantom 9 (loft 3.5 deg, lie 70 deg, near-face-balanced,
perimeter-weighted mallet).  This is an original, trademark-free model:

  * NO Scotty Cameron / Titleist / Phantom logos or text.
  * The "Circle-T" mark is replaced with a custom "Circle-F" mark.

The output is a watertight, 3D-printable solid (STL) at 1:1 scale in
millimetres, ready to slice in Bambu Studio.

Coordinate system (millimetres)
    X : heel  <-->  toe   (width),  0 = centre
    Y : face  <-->  back  (depth),  0 = face
    Z : sole  <-->  crown (height), 0 = sole (flat on the bed)

Author: generated for an MYP personal project.
"""

import numpy as np
import shapely.geometry as sg
import shapely.affinity as sa
from shapely.ops import unary_union
import trimesh
from trimesh.creation import extrude_polygon, cylinder

# ----------------------------------------------------------------------
# MASTER PARAMETERS  - tweak these, re-run, re-slice
# ----------------------------------------------------------------------
W      = 112.0   # overall width  (heel <-> toe)
D      = 112.0   # overall depth  (face <-> back)
H      = 33.0    # overall height (sole -> crown)
CORNER = 20.0    # outer corner rounding radius

LOFT_DEG = 3.5   # face loft  (Phantom 9 spec)
LIE_DEG  = 70.0  # shaft lie  (Phantom 9 spec)

SHAFT_DIA = 9.7  # bore for a 0.370" (9.4 mm) parallel-tip putter shaft + glue gap

ARC = 64         # facet resolution for round shapes (higher = smoother)

# Crown feature depths
PORT_RECESS_DEPTH = 4.0
LOGO_DEPTH        = 1.3
SIGHTLINE_DEPTH   = 1.5

# ----------------------------------------------------------------------
# 2D helpers (shapely)
# ----------------------------------------------------------------------
def rounded_rect(cx, cy, w, h, r):
    """Axis-aligned rounded rectangle centred at (cx, cy)."""
    r = min(r, w / 2 - 1e-6, h / 2 - 1e-6)
    inner = sg.box(cx - w / 2 + r, cy - h / 2 + r, cx + w / 2 - r, cy + h / 2 - r)
    return inner.buffer(r, quad_segs=ARC // 2, join_style=1)

def circle(cx, cy, rad):
    return sg.Point(cx, cy).buffer(rad, quad_segs=ARC)

# ----------------------------------------------------------------------
# 3D helpers (trimesh)
# ----------------------------------------------------------------------
def solid(poly, z0, z1):
    """Extrude a shapely (Multi)Polygon between two Z heights."""
    polys = list(poly.geoms) if poly.geom_type == "MultiPolygon" else [poly]
    parts = []
    for p in polys:
        m = extrude_polygon(p, height=z1 - z0)
        m.apply_translation((0, 0, z0))
        parts.append(m)
    return trimesh.util.concatenate(parts) if len(parts) > 1 else parts[0]

# ----------------------------------------------------------------------
# 1.  BODY  - rounded mallet block, flat sole
# ----------------------------------------------------------------------
foot = rounded_rect(0, D / 2, W, D, CORNER)
body = solid(foot, 0, H)

# ----------------------------------------------------------------------
# 2.  THROUGH WINDOWS  -  open, perimeter-weighted frame (the high-MOI look)
#     Two windows flank a solid central bar; the face block stays solid.
# ----------------------------------------------------------------------
win_y0, win_y1 = 44.0, 72.0
win_cy = (win_y0 + win_y1) / 2
win_h  = win_y1 - win_y0
bar_half = 15.0          # central bar is x in [-15, +15]
rail     = 10.0          # outer rail thickness
win_xo   = W / 2 - rail  # outer edge of window
win_w    = win_xo - bar_half
win_cx   = (bar_half + win_xo) / 2

win_L = rounded_rect(-win_cx, win_cy, win_w, win_h, 9)
win_R = rounded_rect( win_cx, win_cy, win_w, win_h, 9)
windows = solid(unary_union([win_L, win_R]), -1, H + 1)
body = body.difference(windows)

# ----------------------------------------------------------------------
# 3.  ALIGNMENT / WEIGHT PORTS  -  front & back milled discs
#     Recessed ring with a raised central disc + cosmetic milled holes.
# ----------------------------------------------------------------------
def add_port(mesh, cx, cy):
    r_recess, r_disc = 19.0, 15.0
    # ring recess
    pocket = solid(circle(cx, cy, r_recess), H - PORT_RECESS_DEPTH, H + 1)
    mesh = mesh.difference(pocket)
    # raised disc back up to crown level
    disc = solid(circle(cx, cy, r_disc), H - PORT_RECESS_DEPTH, H)
    mesh = mesh.union(disc)
    # cosmetic milled holes around the disc
    holes = []
    for k in range(6):
        a = k * np.pi / 3
        holes.append(circle(cx + 9 * np.cos(a), cy + 9 * np.sin(a), 1.2))
    holes = solid(unary_union(holes), H - 2.0, H + 1)
    mesh = mesh.difference(holes)
    return mesh

body = add_port(body, 0, 26.0)   # front port (near face)
body = add_port(body, 0, 88.0)   # rear port  (near back)

# ----------------------------------------------------------------------
# 4.  SINGLE SIGHT LINE  -  one groove on the front flange (fill with paint)
# ----------------------------------------------------------------------
sight = solid(sg.box(-0.75, 6.0, 0.75, 24.0), H - SIGHTLINE_DEPTH, H + 1)
body = body.difference(sight)

# ----------------------------------------------------------------------
# 5.  CIRCLE-F LOGO  -  engraved on the central bar (replaces Circle-T)
# ----------------------------------------------------------------------
def circle_f(cx, cy):
    """Circle-F mark.  +y is toward the back, so the top of the 'F' is placed
    toward the face (-y) to read correctly from the player's address view."""
    parts = []
    # ring
    ring = circle(cx, cy, 8.6).difference(circle(cx, cy, 6.9))
    parts.append(ring)
    # letter "F" built from bars, centred in the ring, top toward the face
    stem = sg.box(cx - 2.8, cy - 4.6, cx - 1.0, cy + 4.6)        # vertical stem
    top  = sg.box(cx - 2.8, cy - 4.6, cx + 3.2, cy - 2.8)        # top arm (face side)
    mid  = sg.box(cx - 2.8, cy - 0.9, cx + 1.8, cy + 0.9)        # middle arm
    parts.append(unary_union([stem, top, mid]))
    return unary_union(parts)

logo = solid(circle_f(0, 61.5), H - LOGO_DEPTH, H + 1)
body = body.difference(logo)

# ----------------------------------------------------------------------
# 6.  LOFT  -  lean the front face back by LOFT_DEG (about the sole edge)
# ----------------------------------------------------------------------
loft = np.radians(LOFT_DEG)
# cutter: everything in front of the lofted face plane gets removed
cutter = trimesh.creation.box(extents=(W + 60, 60, H + 60))
cutter.apply_translation((0, -30, H / 2))                 # sits in front of face
cutter.apply_transform(
    trimesh.transformations.rotation_matrix(loft, (1, 0, 0), (0, 0, 0)))
body = body.difference(cutter)

# ----------------------------------------------------------------------
# 7.  SHAFT BORE  -  single-bend hosel entry at LIE_DEG, near centre
# ----------------------------------------------------------------------
# axis leans toward the heel (-X) in the heel-toe plane (y held constant)
horiz = (H + 8) / np.tan(np.radians(LIE_DEG))             # heel-ward run over the rise
p0 = np.array([ horiz / 2 + 4, 47.0, H + 8])             # above the crown
p1 = np.array([-horiz / 2 + 4, 47.0, 5.0])               # deep inside the head
bore = cylinder(radius=SHAFT_DIA / 2, segment=(p0, p1), sections=ARC)
body = body.difference(bore)

# ----------------------------------------------------------------------
# 8.  REAR WEIGHT POCKETS  -  blind holes in the sole near the back corners.
#     Insert steel/tungsten + epoxy to reach tour weight (~350 g) and
#     push mass to the perimeter for higher MOI = more forgiving putting.
# ----------------------------------------------------------------------
for sx in (-1, 1):
    pocket = cylinder(radius=6.0, height=22.0, sections=ARC)
    pocket.apply_translation((sx * 40.0, 92.0, 11.0 - 1.0))  # opens at sole
    body = body.difference(pocket)

# ----------------------------------------------------------------------
# FINALISE  -  clean up, report, export
# ----------------------------------------------------------------------
body.merge_vertices()
body.remove_duplicate_faces() if hasattr(body, "remove_duplicate_faces") else None
body.fix_normals()

print("watertight        :", body.is_watertight)
print("winding consistent:", body.is_winding_consistent)
bb = body.bounds
print("bounding box (mm) : "
      f"W={bb[1][0]-bb[0][0]:.1f}  D={bb[1][1]-bb[0][1]:.1f}  H={bb[1][2]-bb[0][2]:.1f}")
vol_cm3 = body.volume / 1000.0
print(f"solid volume      : {vol_cm3:.1f} cm^3")
print(f"  -> mass @100% PLA  (1.24 g/cm3): {vol_cm3*1.24:5.0f} g")
print(f"  -> mass @ 30% PLA  infill      : {vol_cm3*1.24*0.30:5.0f} g")

for out in ("Putter_PhantomStyle_9_CircleF.stl",
            "Putter_PhantomStyle_9_CircleF.3mf"):
    body.export(out)
    print("exported          :", out)
