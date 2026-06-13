import numpy as np, cv2
from PIL import Image
img = Image.open("/root/.claude/uploads/f0e28ff9-2608-5791-9f69-b4a0c0084a92/5cd25c3f-IMG_4830.jpeg").convert("RGB")
a = np.asarray(img).astype(int)
H,W = a.shape[:2]
R,G,B = a[...,0],a[...,1],a[...,2]
green_excess = G - np.maximum(R,B)

# non-grass = candidate (head + hand + shaft)
mask = (green_excess <= 16).astype(np.uint8)
# clean
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)

# largest connected component
n,lab,stats,cent = cv2.connectedComponentsWithStats(mask,8)
# pick the component whose centroid is most central and is large
best=None;bestscore=-1
for i in range(1,n):
    area=stats[i,cv2.CC_STAT_AREA]
    cx,cy=cent[i]
    if area<2000: continue
    centrality = 1.0 - (abs(cx-W/2)/W + abs(cy-H/2)/H)
    score = area*centrality
    if score>bestscore: bestscore=score;best=i
head=(lab==best).astype(np.uint8)
# fill holes (the dark center & discs are part of head; grass-through would be holes)
hf = head.copy()
ff = hf.copy(); h2,w2=ff.shape
maskff=np.zeros((h2+2,w2+2),np.uint8)
cv2.floodFill(ff,maskff,(0,0),1)
holes = (ff==0)
head_filled = (head|holes).astype(np.uint8)

cnts,_=cv2.findContours(head_filled,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cnts,key=cv2.contourArea)
print("head area px:",int(cv2.contourArea(c)))
rect=cv2.minAreaRect(c)
print("minAreaRect center=%s size=(%.0f,%.0f) angle=%.1f"%(tuple(np.round(rect[0],0)),rect[1][0],rect[1][1],rect[2]))

# overlay
ov=a.astype(np.uint8).copy()
cv2.drawContours(ov,[c],-1,(255,0,0),2)
box=cv2.boxPoints(rect).astype(int)
cv2.drawContours(ov,[box],-1,(255,255,0),1)
Image.fromarray(ov).save("seg_overlay.png")
Image.fromarray((head_filled*255).astype(np.uint8)).save("seg_mask.png")
np.save("contour.npy",c.reshape(-1,2))
print("saved seg_overlay.png, seg_mask.png, contour.npy")
