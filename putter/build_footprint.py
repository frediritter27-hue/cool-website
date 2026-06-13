import numpy as np
c = np.load("clean_contour.npy").astype(float)   # px, upright frame
# center
cen = c.mean(0); c -= cen
# polar
ang = np.arctan2(c[:,1], c[:,0]); rad = np.hypot(c[:,0], c[:,1])
o = np.argsort(ang); ang=ang[o]; rad=rad[o]
# resample to uniform theta
T = np.linspace(-np.pi, np.pi, 721)
# wrap-safe interpolation
ang_ext = np.concatenate([ang-2*np.pi, ang, ang+2*np.pi])
rad_ext = np.concatenate([rad, rad, rad])
r = np.interp(T, ang_ext, rad_ext)
# symmetrize about vertical axis (x->-x  =>  theta -> pi-theta)
r_mir = np.interp(T, T, r[::-1])              # reflect index
# reflection of angle theta about vertical axis maps theta->pi-theta; build via flip of r over theta sign about pi/2
def reflectV(rvals):
    # new r at theta = old r at (pi - theta)
    th = np.pi - T
    th = (th+np.pi)%(2*np.pi)-np.pi
    return np.interp(th, T, rvals, period=2*np.pi)
r = 0.5*(r + reflectV(r))
# circular smoothing (gaussian)
def csmooth(x, sig=9):
    n=len(x); k=np.arange(-3*sig,3*sig+1); g=np.exp(-0.5*(k/sig)**2); g/=g.sum()
    return np.array([np.sum(np.take(x, (i+k)%n)*g) for i in range(n)])
r = csmooth(r, 9)
x = r*np.cos(T); y = r*np.sin(T)
pts = np.column_stack([x,y])
# scale: width(x-span) -> target mm
WIDTH_MM = 109.0
span_x = x.max()-x.min()
s = WIDTH_MM/span_x
pts *= s
# orient: make Y = face(0)..back. The shaft/face side was +y (bottom rows after rotate). 
# put face at min y -> shift so min y = 0; flip so face (was bottom=+y) becomes y=0 front.
pts[:,1] = -pts[:,1]                      # flip
pts[:,1] -= pts[:,1].min()
pts[:,0] -= (pts[:,0].max()+pts[:,0].min())/2
W=pts[:,0].max()-pts[:,0].min(); D=pts[:,1].max()-pts[:,1].min()
print("footprint  width=%.1f mm  depth=%.1f mm  (npts=%d)"%(W,D,len(pts)))
# flatten the FACE: clip the front (low-y) to a straight line at y=face_y
# find min y region; set all points within 4mm of front to the straight chord
np.save("foot_mm.npy", pts)
# preview
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.figure(figsize=(6,6)); plt.fill(pts[:,0],pts[:,1],alpha=.3); plt.plot(pts[:,0],pts[:,1],'r-')
plt.gca().set_aspect('equal'); plt.grid(True,alpha=.3); plt.title("Footprint (mm) - face at bottom(y=0)")
plt.xlabel("x heel<->toe"); plt.ylabel("y face->back")
plt.savefig("foot_mm.png",dpi=110,bbox_inches='tight'); print("saved foot_mm.png")
