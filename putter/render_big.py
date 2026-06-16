import numpy as np, trimesh
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
m=trimesh.load("Putter_PhantomStyle_9_CircleF.stl"); tris=m.vertices[m.faces]; n=m.face_normals
def shade(ax,elev,azim,title):
    light=np.array([0.25,-0.55,0.8]);light/=np.linalg.norm(light)
    sh=np.clip(n.dot(light),0.12,1);base=np.array([0.62,0.64,0.68])
    cols=np.clip(base[None,:]*sh[:,None]+0.08,0,1)
    pc=Poly3DCollection(tris);pc.set_facecolor(cols);pc.set_edgecolor((0,0,0,0.04));pc.set_linewidth(0.1)
    ax.add_collection3d(pc);b=m.bounds
    ax.set_xlim(b[0][0],b[1][0]);ax.set_ylim(b[0][1],b[1][1]);ax.set_zlim(b[0][2],b[1][2])
    ax.set_box_aspect((b[1]-b[0]));ax.view_init(elev=elev,azim=azim);ax.set_title(title);ax.set_axis_off()
fig=plt.figure(figsize=(9,9)); shade(fig.add_subplot(111,projection="3d"),88,-90,"CROWN top-down")
plt.savefig("big_top.png",dpi=110,bbox_inches="tight")
fig=plt.figure(figsize=(9,9)); shade(fig.add_subplot(111,projection="3d"),30,-58,"3/4 view")
plt.savefig("big_iso.png",dpi=110,bbox_inches="tight")
fig=plt.figure(figsize=(9,5)); shade(fig.add_subplot(111,projection="3d"),6,-90,"FACE")
plt.savefig("big_face.png",dpi=110,bbox_inches="tight"); print("ok")
