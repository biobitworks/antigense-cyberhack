#!/usr/bin/env python3
"""Antigense 053 public REVIEW candidate: preserve original 039R1 and append local 050 action footage.
Does not assert word-level synchronization or complete per-frame privacy screening.
Nimble opening 8 s replaced by sanitized title card; later authentic judge screen frames retained.
"""
import subprocess, hashlib, json, pathlib, os, datetime
from PIL import Image, ImageDraw, ImageFont
B=pathlib.Path('/Users/byron/projects/hackathon/antigense-video-053')
PUB=B/'public'/'video-053-review'
PUB.mkdir(parents=True,exist_ok=True)
PREV=pathlib.Path('/Users/byron/projects/hackathon/antigense-public-backup-052/public/video/antigense-039r1-audio-clean.mp4')
J=pathlib.Path('/Users/byron/Documents/Screen Recording 2026-10-09 at 3.39.20\u202fPM.mov')
VOICE=pathlib.Path('/Users/byron/Library/Mobile Documents/com~apple~CloudDocs/Hackathon/AWS Builder Loft 3.m4a')
if not all(p.is_file() for p in (PREV,J,VOICE)): raise SystemExit('MISSING SOURCE')
font='/System/Library/Fonts/Supplemental/Arial.ttf'
bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def title(name,eyebrow,title,lines):
 im=Image.new('RGB',(1440,900),'#0c171d')
 d=ImageDraw.Draw(im)
 d.ellipse((960,-250,1550,330),outline='#1c595e',width=4)
 d.rounded_rectangle((68,82,1372,815),radius=25,fill='#132832',outline='#37606a',width=3)
 d.rectangle((104,138,1324,147),fill='#74dba0')
 d.text((106,188),eyebrow,font=ImageFont.truetype(bold,32),fill='#77dcb1')
 d.text((106,274),title,font=ImageFont.truetype(bold,64),fill='#e4f3ed')
 for i,t in enumerate(lines):d.text((110,425+i*75),t,font=ImageFont.truetype(font,34),fill='#cadad5')
 d.text((106,742),'ANTIGENSE DAISY  /  SYNTHETIC LOCAL DEMONSTRATION',font=ImageFont.truetype(bold,23),fill='#9fc2b4')
 p=PUB/name;im.save(p);return p
# Source frames 0-8 are retained as moving background, irreversibly blurred across the full image.
# A separate transparent overlay labels Nimble and explains that the local credential is redacted.
im=Image.new('RGBA',(1440,900),(0,0,0,0))
d=ImageDraw.Draw(im)
d.rounded_rectangle((46,40,1394,253),radius=25,fill=(12,26,34,242),outline=(101,203,156,255),width=4)
d.text((80,78),'NIMBLE  /  LOCAL JUDGE 050',font=ImageFont.truetype(bold,45),fill=(227,245,237,255))
d.text((80,150),'Source motion retained; ALL opening pixels blurred to mask the API key.',font=ImageFont.truetype(font,27),fill=(184,214,202,255))
d.text((80,190),'Observable DENY / ALLOW interactions follow in the unblurred local interface.',font=ImageFont.truetype(font,24),fill=(184,214,202,255))
nimble=PUB/'nimble-mask-overlay.png'
im.save(nimble)

outro=title('closing-evidence.png','03 / EVIDENCE AND LIMITS','Evidence has an address',['Semgrep / Akash / ClickHouse: prior bounded execution.','050: local judge action, not remote judge identity.','Independent proof: antigense-cyberhack.vercel.app'])
OUT=PUB/'antigense-daisy-053-r3-three-minute-review.mp4'
D0=142.166667
D1=8.0
D2=22.666667
D3=7.166666
fc=(
 f'[0:v]fps=30,trim=duration={D0},setpts=PTS-STARTPTS,scale=1440:900,setsar=1,format=yuv420p[v0];'
 f'[0:a]atrim=duration={D0},asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=mono,apad=pad_dur=0.1,atrim=duration={D0}[a0];'
 f'[1:v]trim=duration={D1},setpts=PTS-STARTPTS,fps=30,scale=1440:900:force_original_aspect_ratio=decrease,pad=1440:900:(ow-iw)/2:(oh-ih)/2,setsar=1,boxblur=35:3[blurred];[3:v]fps=30,trim=duration={D1},setpts=PTS-STARTPTS,format=rgba[label];[blurred][label]overlay=x=0:y=0:shortest=1,format=yuv420p[v1];'
 f'anullsrc=r=48000:cl=mono,atrim=duration={D1},asetpts=PTS-STARTPTS[a1];'
 f'[1:v]trim=start=8:duration=15.0,setpts=PTS-STARTPTS,fps=30,scale=1440:900:force_original_aspect_ratio=decrease,pad=1440:900:(ow-iw)/2:(oh-ih)/2,setsar=1,tpad=stop_mode=clone:stop_duration=8.0,trim=duration={D2},format=yuv420p[v2];'
 f'[2:a]atrim=duration={D2},asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=mono,loudnorm=I=-17:TP=-1.6:LRA=11[a2];'
 f'[4:v]fps=30,trim=duration={D3},setpts=PTS-STARTPTS,setsar=1,format=yuv420p[v3];'
 f'anullsrc=r=48000:cl=mono,atrim=duration={D3},asetpts=PTS-STARTPTS[a3];'
 '[v0][a0][v1][a1][v2][a2][v3][a3]concat=n=4:v=1:a=1[v][a]'
)
cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-stats','-i',str(PREV),'-i',str(J),'-i',str(VOICE),'-loop','1','-framerate','30','-i',str(nimble),'-loop','1','-framerate','30','-i',str(outro),'-filter_complex',fc,'-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','144k','-ar','48000','-ac','1','-movflags','+faststart','-t','180','-frames:v','5400',str(OUT)]
print('START_RENDER',OUT,flush=True)
subprocess.run(cmd,check=True)
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(OUT)]))
print('RENDER_RESULT_DURATION',info['format'].get('duration'),'BYTES',OUT.stat().st_size,flush=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
receipt={'schema':'antigense.media053.review_render.v1','status':'R3_REVIEW_CANDIDATE_NOT_FINAL_PRIVACY_OR_AUDIO_VERIFIED','target_seconds':180,'output_duration_seconds':float(info['format']['duration']),'output_file':OUT.name,'output_sha256':sha(OUT),'source_sha256':{'039r1_existing_published_video':sha(PREV),'050_original_screen_recording':sha(J),'050_narration':sha(VOICE)},'segments':[{'kind':'039R1_RETAINED_HISTORICAL_VIDEO','start':0,'duration':D0},{'kind':'NIMBLE_REAL_SOURCE_FULL_FRAME_PIXEL_BLUR_WITH_OPAQUE_LABEL','start':D0,'duration':D1},{'kind':'LIVE_050_UNRETOUCHED_REAL_SCREEN_T8_TO_T23_THEN_HELD_RESULT_TO_AVOID_OS_UI','start':D0+D1,'duration':D2},{'kind':'EVIDENCE_LIMITS_OUTRO','start':D0+D1+D2,'duration':D3}],'credential_scope':'FIRST_8_SECONDS_RETENTION_AS_WHOLE_FRAME_IRREVERSIBLY_BLURRED_MOVING_SOURCE; NIMBLE_OVERLAY_LABEL; LATER_FRAMES_MANUAL_REVIEW_REQUIRED','speech_sync':'MANUAL_LISTEN_NOT_TESTED','source_interpretation':'EARLIER_SPONSOR_EXECUTIONS_SEPARATE_FROM_NEW_LOCAL_050','mmr':'NOT_COMPUTED','signature':'NOT_SIGNED','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(PUB/'media_receipt_r3.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print('RENDER_SHA256',receipt['output_sha256'],flush=True)
