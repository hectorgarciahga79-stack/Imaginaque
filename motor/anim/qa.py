import subprocess, json, sys
from PIL import Image
for v in sys.argv[1:]:
    tl=json.load(open(f'build/{v}/timeline.json')); ims=[]
    for sc in tl['scenes']:
        t=sc['start']+(sc['end']-sc['start'])*0.7
        subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",f"{t:.2f}","-i",f"out/{v}.mp4","-frames:v","1","-vf","scale=216:384","/tmp/q.png"])
        ims.append(Image.open("/tmp/q.png").convert("RGB"))
    S=Image.new("RGB",(216*6,384*2),'white')
    for i,im in enumerate(ims): S.paste(im,((i%6)*216,(i//6)*384))
    S.save(f"/tmp/qa_{v}.jpg")
