#!/usr/bin/env python3
"""Assemble local screen video and voice; preserve inputs and record file identity."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--video',required=True);p.add_argument('--audio',required=True);p.add_argument('--output',required=True);a=p.parse_args()
video=Path(a.video).resolve();audio=Path(a.audio).resolve();output=Path(a.output).resolve();receipt=Path(str(output)+'.receipt.json')
for exe in ['ffmpeg','ffprobe']:
    if not shutil.which(exe):sys.exit('FAIL missing '+exe)
if not video.is_file() or not audio.is_file():sys.exit('FAIL input missing')
if output.exists() or receipt.exists():sys.exit('FAIL output or receipt exists; choose a new output name')
if output.suffix.lower()!='.mp4':sys.exit('FAIL output must end in .mp4')
def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type','-of','json',str(path)],text=True))
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
v=probe(video);s=probe(audio)
if not any(x['codec_type']=='video' for x in v['streams']):sys.exit('FAIL video stream absent')
if not any(x['codec_type']=='audio' for x in s['streams']):sys.exit('FAIL narration stream absent')
vd=float(v['format']['duration']);ad=float(s['format']['duration']);pad=max(0,ad-vd)
if pad>30:sys.exit('FAIL narration exceeds video by over 30 seconds; record a longer walkthrough')
print('START audio assembly; inputs preserved',flush=True)
cmd=['ffmpeg','-nostdin','-n','-v','error','-i',str(video),'-i',str(audio),'-map','0:v:0','-map','1:a:0']
if pad:cmd+=['-vf','tpad=stop_mode=clone:stop_duration='+str(pad)]
cmd+=['-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(ad),'-movflags','+faststart',str(output)]
subprocess.run(cmd,check=True)
result=probe(output)
ok=any(x['codec_type']=='video' for x in result['streams']) and any(x['codec_type']=='audio' for x in result['streams']) and abs(float(result['format']['duration'])-ad)<0.5
record={'state':'OBSERVED' if ok else 'FAILED','video_input_sha256':sha(video),'audio_input_sha256':sha(audio),'output_sha256':sha(output),'video_seconds':vd,'voice_seconds':ad,'final_frame_padding_seconds':pad,'output_seconds':float(result['format']['duration']),'audio_video_streams_present':ok,'semantic_alignment':'NOT_TESTED','publication':'NOT_EXECUTED','mmr_root':'NOT_COMPUTED'}
with receipt.open('x') as f:json.dump(record,f,sort_keys=True,indent=2)
print(('PASS' if ok else 'FAIL')+' audio/video assembly; listen and review before publishing',flush=True)
sys.exit(0 if ok else 1)
