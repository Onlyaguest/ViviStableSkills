#!/usr/bin/env python3
"""Build transparent desktop video frames from user-provided MP4 originals."""
from pathlib import Path
import subprocess,tempfile,json,hashlib
from PIL import Image, ImageFilter
root=Path(__file__).resolve().parent.parent
sources={'read':'83c6e470-eb27-48d0-a38f-fad66038ff56.mp4','doze':'doze_loop.mp4','happy':'happy_loop.mp4','piqued':'piqued_loop.mp4'}
manifest={}
for name,filename in sources.items():
 src=Path.home()/'Downloads'/filename
 dst=root/'Assets/Animations'/name;dst.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  subprocess.run(['ffmpeg','-v','error','-i',str(src),'-vf','fps=8,crop=720:1000:0:150,format=rgba',str(Path(tmp)/'%04d.png')],check=True)
  files=sorted(Path(tmp).glob('*.png'))
  for i,path in enumerate(files):
   im=Image.open(path).convert('RGBA').resize((288,400),Image.Resampling.LANCZOS)
   from collections import deque
   width,height=im.size;rgb=list(im.convert('RGB').getdata())
   background=[False]*(width*height)
   candidates=[sum((c-v)**2 for c,v in zip(pixel,(233,229,220))) < 90**2 and min(pixel)>195 and max(pixel)-min(pixel)<55 for pixel in rgb]
   # Flood only exterior paper; enclosed face, collar and stone-table whites stay intact.
   q=deque()
   for y in range(height):
    for x in (0,width-1):
     idx=y*width+x
     if candidates[idx] and not background[idx]:background[idx]=True;q.append(idx)
   for x in range(width):
    for y in (0,height-1):
     idx=y*width+x
     if candidates[idx] and not background[idx]:background[idx]=True;q.append(idx)
   while q:
    idx=q.popleft();x=idx%width;y=idx//width
    for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
     j=ny*width+nx
     if 0<=nx<width and 0<=ny<height and candidates[j] and not background[j]:
      background[j]=True;q.append(j)
   alpha=Image.new('L',im.size);alpha.putdata([0 if value else 255 for value in background]);im.putalpha(alpha)
   # Remove isolated paper specks, preserving the connected character/table/stool.
   alpha=im.getchannel('A');mask=alpha.point(lambda a:255 if a>30 else 0)
   from collections import deque
   seen=set();keep=set()
   for y in range(im.height):
    for x in range(im.width):
     if (x,y) in seen or not mask.getpixel((x,y)):continue
     q=deque([(x,y)]);seen.add((x,y));component=[]
     while q:
      px,py=q.popleft();component.append((px,py))
      for nx,ny in ((px-1,py),(px+1,py),(px,py-1),(px,py+1)):
       if 0<=nx<im.width and 0<=ny<im.height and (nx,ny) not in seen and mask.getpixel((nx,ny)):
        seen.add((nx,ny));q.append((nx,ny))
     if len(component)>=200:keep.update(component)
   # Preserve antialiased edges adjacent to kept components.
   edge=set(keep)
   for x,y in keep:
    for dx in (-1,0,1):
     for dy in (-1,0,1):edge.add((x+dx,y+dy))
   alpha.putdata([alpha.getpixel((x,y)) if (x,y) in edge else 0 for y in range(im.height) for x in range(im.width)])
   alpha=alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.4))
   im.putalpha(alpha);im.save(dst/f'{i:04d}.png')
  manifest[name]={'frames':len(files),'fps':8,'width':288,'height':400,'source':filename,'sha256':hashlib.sha256(src.read_bytes()).hexdigest()}
 print(name,len(files),flush=True)
(root/'Assets/Animations/manifest.json').write_text(json.dumps(manifest,indent=2))
