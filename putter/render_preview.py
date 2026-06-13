import numpy as np, trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

m = trimesh.load("Putter_PhantomStyle_9_CircleF.stl")
print("faces:", len(m.faces))
tris = m.vertices[m.faces]

def view(ax, elev, azim, title):
    pc = Poly3DCollection(tris, alpha=1.0)
    # simple shading by face normal vs light
    n = m.face_normals
    light = np.array([0.3,-0.4,0.85]); light=light/np.linalg.norm(light)
    shade = np.clip(n.dot(light),0.15,1.0)
    base = np.array([0.45,0.5,0.6])
    cols = np.clip(base[None,:]*shade[:,None]+0.12,0,1)
    pc.set_facecolor(cols); pc.set_edgecolor((0,0,0,0.05)); pc.set_linewidth(0.1)
    ax.add_collection3d(pc)
    b=m.bounds
    ax.set_xlim(b[0][0],b[1][0]); ax.set_ylim(b[0][1],b[1][1]); ax.set_zlim(b[0][2],b[1][2])
    ax.set_box_aspect((b[1]-b[0]))
    ax.view_init(elev=elev,azim=azim); ax.set_title(title); ax.set_axis_off()

fig=plt.figure(figsize=(16,5))
ax1=fig.add_subplot(131,projection="3d"); view(ax1,90,-90,"TOP (address view)")
ax2=fig.add_subplot(132,projection="3d"); view(ax2,12,-90,"FACE / front")
ax3=fig.add_subplot(133,projection="3d"); view(ax3,32,-60,"ISO")
plt.tight_layout(); plt.savefig("preview.png",dpi=110,bbox_inches="tight")
print("saved preview.png")
