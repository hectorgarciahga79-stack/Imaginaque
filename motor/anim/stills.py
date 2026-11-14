"""QA de escenas sin voz: python3 stills.py VID [modulo]  -> /tmp/qa_VID.jpg (fotograma al 75 % de cada escena)"""
import sys, os, subprocess, importlib; sys.path.insert(0, '/home/claude/anim')
from engine import *
vid = sys.argv[1]; mod = importlib.import_module(sys.argv[2] if len(sys.argv) > 2 else 'scenes')
out = f'/tmp/st_{vid}'; os.makedirs(out, exist_ok=True)
for i, f in enumerate(mod.SCENES[vid]):
    for j, fr in enumerate((0, 0.35, 0.75, 0.999)):
        d = 5.0; surf, c = new_surface(); c.set_source_rgb(0, 0, 0); c.paint()
        f(c, fr*d, d, 10+i*5+fr*d); surf.write_to_png(f'{out}/{i:02d}_{j}.png')
subprocess.run(f"ffmpeg -loglevel error -y -pattern_type glob -i '{out}/*_2.png' -vf scale=270:480,tile=6x2 /tmp/qa_{vid}.jpg", shell=True)
print('OK', f'/tmp/qa_{vid}.jpg')
