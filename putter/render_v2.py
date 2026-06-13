import numpy as np, trimesh
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.collections import PolyCollection
m = trimesh.load("Putter_PhantomStyle_9_CircleF.stl")
tris = m.vertices[m.faces]; n=m.face_normals
def shade(ax,elev,azim,title):
    light=np.array([0.3,-0.5,0.8]); light/=np.linalg.norm(light)
    sh=np.clip(n.dot(light),0.15,1); base=np.array([0.5,0.55,0.62])
    cols=np.clip(base[None,:]*sh[:,None]+0.10,0,1)
    pc=Poly3DCollection(tris); pc.set_facecolor(cols); pc.set_edgecolor((0,0,0,0.04)); pc.set_linewidth(0.1)
    ax.add_collection3d(pc); b=m.bounds
    ax.set_xlim(b[0][0],b[1][0]);ax.set_ylim(b[0][1],b[1][1]);ax.set_zlim(b[0][2],b[1][2])
    ax.set_box_aspect((b[1]-b[0])); ax.view_init(elev=elev,azim=azim); ax.set_title(title); ax.set_axis_off()
fig=plt.figure(figsize=(17,5))
shade(fig.add_subplot(131,projection="3d"),60,-90,"CROWN / address")
shade(fig.add_subplot(132,projection="3d"),8,-90,"FACE")
shade(fig.add_subplot(133,projection="3d"),28,-55,"ISO")
plt.tight_layout(); plt.savefig("v2_views.png",dpi=115,bbox_inches="tight")
# top height map
up=n[:,2]>0.15; t=tris[up]; o=np.argsort(t[:,:,2].mean(1)); t=t[o]
fig2,ax=plt.subplots(figsize=(6,6))
pc=PolyCollection([x[:,:2] for x in t],array=t[:,:,2].mean(1),cmap="viridis",edgecolors="none")
ax.add_collection(pc); b=m.bounds; ax.set_xlim(b[0][0]-3,b[1][0]+3);ax.set_ylim(b[0][1]-3,b[1][1]+3)
ax.set_aspect("equal"); ax.invert_yaxis(); ax.set_title("CROWN height map (face at top)")
plt.colorbar(pc); plt.savefig("v2_top.png",dpi=115,bbox_inches="tight")
print("ok")
