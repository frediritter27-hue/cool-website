import numpy as np, trimesh
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
m=trimesh.load("Putter_PhantomStyle_9_CircleF.stl"); tris=m.vertices[m.faces]; n=m.face_normals
def shade(ax,elev,azim,title):
    light=np.array([0.3,-0.5,0.8]);light/=np.linalg.norm(light)
    sh=np.clip(n.dot(light),0.15,1);base=np.array([0.52,0.56,0.62])
    cols=np.clip(base[None,:]*sh[:,None]+0.1,0,1)
    pc=Poly3DCollection(tris);pc.set_facecolor(cols);pc.set_edgecolor((0,0,0,0.03));pc.set_linewidth(0.1)
    ax.add_collection3d(pc);b=m.bounds
    ax.set_xlim(b[0][0],b[1][0]);ax.set_ylim(b[0][1],b[1][1]);ax.set_zlim(b[0][2],b[1][2])
    ax.set_box_aspect((b[1]-b[0]));ax.view_init(elev=elev,azim=azim);ax.set_title(title);ax.set_axis_off()
fig=plt.figure(figsize=(18,5))
shade(fig.add_subplot(141,projection="3d"),62,-90,"CROWN / address")
shade(fig.add_subplot(142,projection="3d"),7,-90,"FACE")
shade(fig.add_subplot(143,projection="3d"),-62,-90,"SOLE (discs + Circle-F)")
shade(fig.add_subplot(144,projection="3d"),26,-55,"ISO")
plt.tight_layout();plt.savefig("preview.png",dpi=120,bbox_inches="tight");print("ok")
