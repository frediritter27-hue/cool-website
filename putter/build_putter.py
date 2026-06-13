#!/usr/bin/env python3
"""
Putter head generator v2  -  "Phantom-style 9", Circle-F edition
================================================================
Now built from the REAL silhouette traced from the reference photo
(foot_mm.npy) instead of a guessed rounded square, and lofted with
rounded crown + sole edges so it reads like a real milled head, not a slab.

Trademark-free: no Scotty Cameron / Titleist / Phantom logos or text.
The "Circle-T" mark is replaced with a custom "Circle-F" mark.

Coords (mm):  X heel<->toe,  Y face(0)->back,  Z sole(0)->crown.
"""
import numpy as np
import shapely.geometry as sg
import shapely.affinity as sa
from shapely.ops import unary_union
import trimesh
from trimesh.creation import extrude_polygon, cylinder, triangulate_polygon

# ---------------- parameters ----------------
H      = 35.0     # crown height at the back
R_CROWN = 9.0     # crown edge roll radius (rounded top edge)
R_SOLE  = 2.5     # sole edge roll radius
LOFT_DEG = 3.5
LIE_DEG  = 70.0
SHAFT_DIA = 9.7
FACE_Y   = 4.0    # flatten the striking face at this y
NLAY = 90         # vertical loft layers
ARC = 96

# ---------------- base outline (real trace) ----------------
foot = np.load("foot_mm.npy")              # (M,2) mm, face at y=0
base_poly = sg.Polygon(foot).buffer(0)     # clean
D = foot[:,1].max() - foot[:,1].min()
W = foot[:,0].max() - foot[:,0].min()

def resample(poly, n):
    """Resample a polygon exterior to n points evenly by arc length."""
    ring = np.asarray(poly.exterior.coords)[:-1]
    seg = np.linalg.norm(np.diff(np.vstack([ring, ring[:1]]), axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)]); total = s[-1]
    targ = np.linspace(0, total, n, endpoint=False)
    out = np.empty((n, 2))
    for i, t in enumerate(targ):
        out[i] = [np.interp(t, s, np.append(ring[:,0], ring[0,0])),
                  np.interp(t, s, np.append(ring[:,1], ring[0,1]))]
    return out

N = 220
base_pts = resample(base_poly, N)
# lock vertex correspondence: angular order around centroid
cx0, cy0 = base_pts.mean(0)
order = np.argsort(np.arctan2(base_pts[:,1]-cy0, base_pts[:,0]-cx0))
base_pts = base_pts[order]

def offset_at(z):
    """Inward offset (negative) for the loft profile at height z."""
    if z <= R_SOLE:
        return -(R_SOLE - np.sqrt(max(0.0, R_SOLE**2 - (z - R_SOLE)**2)))
    if z >= H - R_CROWN:
        return -(R_CROWN - np.sqrt(max(0.0, R_CROWN**2 - (z - (H - R_CROWN))**2)))
    return 0.0

def offset_ring(off):
    """Offset the base polygon inward by |off| and resample to N pts, kept ordered."""
    if abs(off) < 1e-6:
        return base_pts.copy()
    p = base_poly.buffer(off, quad_segs=32, join_style=1)
    if p.is_empty:
        return base_pts.copy() * 0.0 + [cx0, cy0]
    if p.geom_type == "MultiPolygon":
        p = max(p.geoms, key=lambda g: g.area)
    pts = resample(p, N)
    o = np.argsort(np.arctan2(pts[:,1]-cy0, pts[:,0]-cx0))
    return pts[o]

# ---------------- build lofted mesh ----------------
zs = np.linspace(0, H, NLAY)
rings = [offset_ring(offset_at(z)) for z in zs]
verts = []
for z, ring in zip(zs, rings):
    verts.append(np.column_stack([ring, np.full(N, z)]))
verts = np.vstack(verts)                    # (NLAY*N, 3)

faces = []
for k in range(NLAY - 1):
    a0 = k * N; b0 = (k + 1) * N
    for i in range(N):
        j = (i + 1) % N
        faces.append([a0 + i, a0 + j, b0 + j])
        faces.append([a0 + i, b0 + j, b0 + i])

# caps via earcut triangulation of the (offset) polygon at top & bottom
def cap(ring, zval, base_index, flip):
    poly = sg.Polygon(ring)
    v2, f2 = triangulate_polygon(poly, engine="earcut")
    # map triangulated verts to nearest ring index where possible; simpler: add new verts
    return v2, f2

# bottom cap (z=0)
vb, fb = triangulate_polygon(sg.Polygon(rings[0]), engine="earcut")
base_b = len(verts)
verts = np.vstack([verts, np.column_stack([vb, np.zeros(len(vb))])])
for f in fb:
    faces.append([base_b + f[0], base_b + f[2], base_b + f[1]])  # downward normal
# top cap (z=H)
vt, ft = triangulate_polygon(sg.Polygon(rings[-1]), engine="earcut")
base_t = len(verts)
verts = np.vstack([verts, np.column_stack([vt, np.full(len(vt), H)])])
for f in ft:
    faces.append([base_t + f[0], base_t + f[1], base_t + f[2]])

body = trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=True)
body.merge_vertices(); body.fix_normals()
print("lofted body watertight:", body.is_watertight, "| vol %.0f cm3"%(body.volume/1000))

# ---------------- helpers for features ----------------
def solid(poly, z0, z1):
    polys = list(poly.geoms) if poly.geom_type == "MultiPolygon" else [poly]
    ms = []
    for p in polys:
        m = extrude_polygon(p, height=z1 - z0); m.apply_translation((0,0,z0)); ms.append(m)
    return trimesh.util.concatenate(ms) if len(ms) > 1 else ms[0]
def circ(cx, cy, r): return sg.Point(cx, cy).buffer(r, quad_segs=ARC)

# ---------------- flatten + loft the FACE ----------------
loft = np.radians(LOFT_DEG)
cutter = trimesh.creation.box(extents=(W + 80, 60, H + 80))
cutter.apply_translation((0, -30 + FACE_Y, H/2))
cutter.apply_transform(trimesh.transformations.rotation_matrix(loft, (1,0,0), (0,0,0)))
body = body.difference(cutter)

# ---------------- SOLE styling (discs + bar + Circle-F, exactly as in the photo) ----------------
fy, by = 0.27*D, 0.76*D          # front / back disc centres
def add_disc(mesh, cy):
    r_rec, r_disc = 18.0, 14.0
    mesh = mesh.difference(solid(circ(0, cy, r_rec), -2, 3.5))   # ring recess in the sole
    mesh = mesh.union(solid(circ(0, cy, r_disc), 0, 3.5))        # disc flush with the sole
    hs = [circ(8.5*np.cos(k*np.pi/3), cy+8.5*np.sin(k*np.pi/3), 1.1) for k in range(6)]
    mesh = mesh.difference(solid(unary_union(hs), -2, 1.8))      # cosmetic milled holes
    return mesh
body = add_disc(body, fy)
body = add_disc(body, by)

# central bar channel between the discs (recessed into the sole)
bar = sg.box(-13, fy, 13, by).buffer(3, join_style=1)
body = body.difference(solid(bar, -2, 2.2))

# ---------------- Circle-F logo engraved on the sole bar ----------------
# mirrored in x so it reads correctly when the sole is viewed from below
def circle_f(cx, cy):
    ring = circ(cx, cy, 8.6).difference(circ(cx, cy, 6.9))
    stem = sg.box(cx-2.8, cy-4.6, cx-1.0, cy+4.6)
    top  = sg.box(cx-2.8, cy-4.6, cx+3.2, cy-2.8)
    mid  = sg.box(cx-2.8, cy-0.9, cx+1.8, cy+0.9)
    f = unary_union([ring, stem, top, mid])
    return sa.scale(f, xfact=-1, origin=(cx, cy))
# engrave 1.4 mm deeper than the 2.2 mm bar floor so it stands out (paint-fill it red)
body = body.difference(solid(circle_f(0, 0.5*D), -2, 3.6))

# ---------------- CROWN: clean, single sight line ----------------
body = body.difference(solid(sg.box(-0.8, FACE_Y+2, 0.8, 0.34*D), H-2.0, H+2))

# ---------------- shaft bore (single bend, ~lie) ----------------
horiz = (H + 10) / np.tan(np.radians(LIE_DEG))
hy = 0.43*D
p0 = np.array([ horiz/2 + 5, hy, H + 10])
p1 = np.array([-horiz/2 + 5, hy, 6.0])
body = body.difference(cylinder(radius=SHAFT_DIA/2, segment=(p0, p1), sections=ARC))

# ---------------- rear sole weight pockets (MOI + reach tour weight) ----------------
for sx in (-1, 1):
    pk = cylinder(radius=6.0, height=22.0, sections=ARC)
    pk.apply_translation((sx*38.0, 0.82*D, 10.0))
    body = body.difference(pk)

# ---------------- finalise ----------------
body.merge_vertices(); body.fix_normals()
bb = body.bounds
print("watertight:", body.is_watertight, "| winding:", body.is_winding_consistent)
print("bbox W=%.1f D=%.1f H=%.1f mm"%(bb[1][0]-bb[0][0], bb[1][1]-bb[0][1], bb[1][2]-bb[0][2]))
v = body.volume/1000
print("vol %.0f cm3 | PLA 100%%: %.0f g | 30%%: %.0f g"%(v, v*1.24, v*1.24*0.30))
for out in ("Putter_PhantomStyle_9_CircleF.stl", "Putter_PhantomStyle_9_CircleF.3mf"):
    body.export(out); print("exported", out)
