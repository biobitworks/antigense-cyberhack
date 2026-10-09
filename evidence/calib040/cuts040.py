#!/usr/bin/env python3
"""Detect visual transitions in the source video from decoded frames (own diff, no tolerance fitting)."""
import subprocess,json,sys,numpy as np
V=sys.argv[1];W,H=192,120
p=subprocess.run(["ffmpeg","-nostdin","-v","error","-i",V,"-map","0:v:0","-vf","scale=%d:%d,format=gray"%(W,H),"-f","rawvideo","-"],capture_output=True)
a=np.frombuffer(p.stdout,np.uint8).reshape(-1,W*H).astype(np.int16)
d=np.abs(np.diff(a,axis=0)).mean(axis=1)
idx=np.argsort(-d)[:40];res=sorted([(int(i+1),round((i+1)/30,4),round(float(d[i]),2)) for i in idx])
json.dump({"frames":len(a),"fps":30,"top_diffs":res},open(sys.argv[2],"w"))
for r in res:print(r)
