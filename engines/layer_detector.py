import subprocess
import sys
import re

audio=sys.argv[1]

cmd=[
"ffmpeg","-hide_banner","-i",audio,
"-af","aspectralstats=measure=centroid:win_size=4096:overlap=0.5",
"-f","null","-"
]

p=subprocess.run(cmd,stderr=subprocess.PIPE,text=True)

centroids=[]

for line in p.stderr.splitlines():
    m=re.search(r"Centroid: ([0-9.]+)",line)
    if m:
        centroids.append(float(m.group(1)))

print("="*60)
print("LAYER DETECTOR")
print("="*60)

if not centroids:
    print("No centroid data.")
    raise SystemExit

step=max(1,len(centroids)//30)

for i,c in enumerate(centroids[::step]):
    print(f"{i*5:4d}s  Spectral centroid {c:.1f} Hz")
