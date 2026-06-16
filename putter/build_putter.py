#!/usr/bin/env python3
"""
Putter head generator v3  -  fang-style high-MOI mallet, Circle-F edition
=========================================================================
Now models the DEFINING features that were missing: two large windows cut
THROUGH the rear wings (the "gaps"), a central spine carrying the crown sight
line, rear fang tips with a central notch, and a flowing heel neck/hosel.

Trademark-free: no Scotty Cameron / Titleist / Phantom logos, names or text.
The sole "Circle-T" mark is replaced with a custom "Circle-F" mark.

Coords (mm):  X heel(+)<->toe(-),  Y face(0)->back,  Z sole(0)->crown.
"""
import numpy as np
import shapely.geometry as sg
import shapely.affinity as sa
from shapely.ops import unary_union
import trimesh
from trimesh.creation import extrude_polygon, cylinder
import trimesh.boolean as tb

# ---------------- master parameters ----------------
D      = 118.0      # depth face->back
H      = 34.0       # crown height at the back
H_FACE = 29.0       # crown height at the face (crown slopes gently up to the back)
R_CR   = 4.0        # crown edge round
R_SO   = 2.0        # sole edge round
WFACE  = 86.0       # face width
LOFT_DEG = 3.5
LIE_DEG  = 70.0
SHAFT_DIA = 9.7
ARC = 96

def circ(cx, cy, r): return sg.Point(cx, cy).buffer(r, quad_segs=ARC)
def rr(cx, cy, w, h, r):
    return sg.box(cx-w/2+r, cy-h/2+r, cx+w/2-r, cy+h/2-r).buffer(r, quad_segs=24, join_style=1)

# ---------------- outer silhouette (right half, mirrored) ----------------
# face at y=0 (front), fangs at back (y=D). Tune these points vs the photos.
half = [
    (0,    0),     # face centre
    (44,   0),     # face toe corner
    (56,   8),     # wing front shoulder (flare out)
    (61,   32),    # widest (toe side)
    (61,   90),    # hold the wing wide & square
    (57,   108),
    (48,   117),   # rounded back-toe corner (squared, not a spike)
    (34,   118),
    (18,   110),   # inner notch wall
    (6,    104),
    (0,    103),   # shallow rear-notch centre
]
right = np.array(half)
left = right[::-1].copy(); left[:,0] *= -1
outline = np.vstack([right, left[1:]])
foot = sg.Polygon(outline).buffer(0)
# central spine rib extends back into the notch, carrying the sight line
spine = rr(0, 50, 24, 100, 6)
foot = unary_union([foot, spine]).buffer(0)
W = outline[:,0].max() - outline[:,0].min()
print("footprint W=%.1f D=%.1f"%(W, D))

# ---------------- build body with rounded top/bottom edges ----------------
def off(p, d):
    g = p.buffer(d, quad_segs=24, join_style=1)
    if g.geom_type == "MultiPolygon": g = max(g.geoms, key=lambda x: x.area)
    return g
def slab(p, z0, z1):
    geoms = list(p.geoms) if p.geom_type == "MultiPolygon" else [p]
    ms = []
    for g in geoms:
        m = extrude_polygon(g, height=z1-z0); m.apply_translation((0,0,z0)); ms.append(m)
    return trimesh.util.concatenate(ms) if len(ms) > 1 else ms[0]

parts = []
# sole roll
ns = 4
for i in range(ns):
    z0 = R_SO*i/ns; z1 = R_SO*(i+1)/ns
    d = -(R_SO - np.sqrt(max(0, R_SO**2 - (R_SO - z1)**2)))
    parts.append(slab(off(foot, d), z0, z1))
# straight middle
parts.append(slab(foot, R_SO, H-R_CR))
# crown roll
nc = 6
for i in range(nc):
    z0 = H-R_CR + R_CR*i/nc; z1 = H-R_CR + R_CR*(i+1)/nc
    d = -(R_CR - np.sqrt(max(0, R_CR**2 - (z1-(H-R_CR))**2)))
    parts.append(slab(off(foot, d), z0, z1))

body = tb.union(parts)
body.merge_vertices(); body.fix_normals()
print("body watertight:", body.is_watertight)

# ---------------- crown slope (face lower than back) ----------------
# cutting plane rises from z=H_FACE at the face (y=0) to z=H at the back (y=D);
# everything above it is removed, so the crown slopes up toward the back.
slope = np.arctan2(H - H_FACE, D)
cut = trimesh.creation.box(extents=(W+80, D+120, 60))
cut.apply_translation((0, D/2, 30 + H_FACE))     # bottom face flat at z=H_FACE
cut.apply_transform(trimesh.transformations.rotation_matrix(slope, (1,0,0), (0,0,H_FACE)))
body = body.difference(cut)

# ---------------- FACE loft ----------------
loft = np.radians(LOFT_DEG)
fc = trimesh.creation.box(extents=(W+80, 60, H+80))
fc.apply_translation((0, -30+3.0, H/2))
fc.apply_transform(trimesh.transformations.rotation_matrix(loft, (1,0,0), (0,0,0)))
body = body.difference(fc)

# ---------------- WINDOWS through the wings (the "gaps") ----------------
def window(cx, cy, tilt):
    w = rr(cx, cy, 30, 47, 8)
    w = sa.rotate(w, tilt, origin=(cx, cy))
    return slab(w, -5, H+5)
body = body.difference(window( 35, 58, -7))
body = body.difference(window(-35, 58,  7))

# ---------------- crown sight line on the spine ----------------
body = body.difference(slab(sg.box(-1.0, 6, 1.0, 40), H-2.0, H+5))

# ---------------- SOLE: discs + bar + Circle-F (from the owner's photo) ----------------
fy, by = 0.30*D, 0.74*D
def add_disc(mesh, cy):
    mesh = mesh.difference(slab(circ(0, cy, 16), -5, 3.2))
    mesh = mesh.union(slab(circ(0, cy, 12), 0, 3.2))
    hs = [circ(7.5*np.cos(k*np.pi/3), cy+7.5*np.sin(k*np.pi/3), 1.0) for k in range(6)]
    mesh = mesh.difference(slab(unary_union(hs), -5, 1.6))
    return mesh
body = add_disc(body, fy)
body = add_disc(body, by)
body = body.difference(slab(rr(0, 0.5*D, 22, (by-fy)+10, 5), -5, 2.0))   # sole bar channel
def circle_f(cx, cy):
    ring = circ(cx, cy, 8.4).difference(circ(cx, cy, 6.7))
    stem = sg.box(cx-2.7, cy-4.4, cx-1.0, cy+4.4)
    top  = sg.box(cx-2.7, cy-4.4, cx+3.0, cy-2.7)
    mid  = sg.box(cx-2.7, cy-0.8, cx+1.7, cy+0.8)
    return sa.scale(unary_union([ring, stem, top, mid]), xfact=-1, origin=(cx, cy))
body = body.difference(slab(circle_f(0, 0.5*D), -5, 3.4))

# ---------------- rear weight pockets ----------------
for sx in (-1, 1):
    pk = cylinder(radius=5.5, height=12, sections=ARC); pk.apply_translation((sx*40, 94, 6))
    body = body.difference(pk)

# ---------------- finalise ----------------
body.merge_vertices(); body.fix_normals()
bb = body.bounds
print("watertight:", body.is_watertight, "| winding:", body.is_winding_consistent)
print("bbox W=%.1f D=%.1f H=%.1f"%(bb[1][0]-bb[0][0], bb[1][1]-bb[0][1], bb[1][2]-bb[0][2]))
v = body.volume/1000
print("vol %.0f cm3 | PLA100%% %.0f g | 30%% %.0f g"%(v, v*1.24, v*1.24*0.30))
for o in ("Putter_PhantomStyle_9_CircleF.stl", "Putter_PhantomStyle_9_CircleF.3mf"):
    body.export(o); print("exported", o)
