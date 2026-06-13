import numpy as np, cv2
from PIL import Image
img = Image.open("/root/.claude/uploads/f0e28ff9-2608-5791-9f69-b4a0c0084a92/5cd25c3f-IMG_4830.jpeg").convert("RGB")
a = np.asarray(img).astype(int); H,W=a.shape[:2]
R,G,B=a[...,0],a[...,1],a[...,2]
ge=G-np.maximum(R,B)
mask=(ge<=16).astype(np.uint8)
k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,k)
mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,k)
n,lab,stats,cent=cv2.connectedComponentsWithStats(mask,8)
best=max(range(1,n),key=lambda i:stats[i,4]*(1-(abs(cent[i][0]-W/2)/W+abs(cent[i][1]-H/2)/H)) if stats[i,4]>2000 else -1)
head=(lab==best).astype(np.uint8)
# fill holes
ff=head.copy();mff=np.zeros((H+2,W+2),np.uint8);cv2.floodFill(ff,mff,(0,0),1)
head=(head|(ff==0)).astype(np.uint8)
# kill thin shaft via large opening -> bulky head for orientation
big=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(41,41))
bulk=cv2.morphologyEx(head,cv2.MORPH_OPEN,big)
n2,lab2,st2,ce2=cv2.connectedComponentsWithStats(bulk,8)
bi=max(range(1,n2),key=lambda i:st2[i,4])
bulk=(lab2==bi).astype(np.uint8)
rect=cv2.minAreaRect((np.argwhere(bulk)[:,::-1]).astype(np.int32))
ang=rect[2]
if rect[1][0]<rect[1][1]: ang=ang  # keep
# we want long axis vertical; normalize angle
(cx,cy),(rw,rh),angle=rect
if rw>rh: angle=angle+90
print("bulk center=(%.0f,%.0f) size=(%.0f,%.0f) rot angle=%.2f"%(cx,cy,rw,rh,angle))
# rotate head upright about bulk center
Mrot=cv2.getRotationMatrix2D((cx,cy),angle,1.0)
headR=cv2.warpAffine(head*255,Mrot,(W,H),flags=cv2.INTER_NEAREST)
headR=(headR>127).astype(np.uint8)
# scan rows: head rows are wide, shaft narrow -> find back(top) and face(bottom) of bulky head
cols_per_row=headR.sum(1)
ys=np.where(cols_per_row>40)[0]
y0,y1=ys.min(),ys.max()
# width profile to locate shaft (narrow) region near one end
prof=cols_per_row[y0:y1+1]
print("rotated head rows y0=%d y1=%d  width max=%d"%(y0,y1,prof.max()))
# Determine shaft end: the end where width stays small. Trim rows whose width< 0.35*max as shaft, only from the ends
thr=0.35*prof.max()
# from bottom up, trim
keep=np.ones_like(prof,bool)
for i in range(len(prof)):
    if prof[i]<thr: keep[i]=True if (i>len(prof)*0.2 and i<len(prof)*0.8) else False
yy=np.where(keep)[0]
# simpler: crop to rows where width>thr, take contiguous central block
wide=np.where(prof>=thr)[0]
yb0,yb1=y0+wide.min(),y0+wide.max()
crop=np.zeros_like(headR);crop[yb0:yb1+1]=headR[yb0:yb1+1]
# mirror about vertical axis through centroid x of crop
xs=np.argwhere(crop)[:,1]; axis=int(round(xs.mean()))
left=crop.copy();left[:,axis:]=0
mir=left[:,::-1]
# shift mirror so axis aligns
mir2=np.zeros_like(crop)
for x in range(axis):
    mir2[:,2*axis-x if 2*axis-x<W else W-1]=left[:,x]
sym=((left|mir2)>0).astype(np.uint8)
sym=cv2.morphologyEx(sym,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
cnts,_=cv2.findContours(sym,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cnts,key=cv2.contourArea)
print("clean head bbox:",cv2.boundingRect(c),"area",int(cv2.contourArea(c)))
vis=cv2.cvtColor(sym*60,cv2.COLOR_GRAY2RGB)
cv2.drawContours(vis,[c],-1,(255,80,0),2)
Image.fromarray(vis).save("clean_foot.png")
np.save("clean_contour.npy",c.reshape(-1,2))
