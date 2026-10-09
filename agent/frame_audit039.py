#!/usr/bin/env python3
"""Audit existing walkthrough frames and make a DRM-free successor watermark.
No sponsor calls; original media and receipts are immutable inputs.
Usage: python agent/frame_audit039.py build | verify
"""
from pathlib import Path
import sys,json,hashlib,subprocess,re,datetime,importlib.util
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'evidence/frame039'
MEDIA=ROOT/'media/walkthrough-039'
ORIG=ROOT/'media/walkthrough-034b/demo-034-review.mp4'
spec=importlib.util.spec_from_file_location('custody039',ROOT/'src/custody.py')
K=importlib.util.module_from_spec(spec);spec.loader.exec_module(K)
def h(b):return hashlib.sha256(b).hexdigest()
def canon(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def write(p,o):p.write_bytes(canon(o)+b'\n')
def run(cmd):return subprocess.check_output(cmd,text=True)
def decoded(video):
 return run(['ffmpeg','-nostdin','-v','error','-i',str(video),'-map','0:v:0','-an','-pix_fmt','yuv420p','-f','framemd5','-hash','sha256','-'])
def build():
 BASE.mkdir(exist_ok=False);MEDIA.mkdir(exist_ok=False)
 print('START frame039',flush=True)
 datafile=ROOT/'public/data/walkthrough-034.json';page=ROOT/'public/walkthrough-034.html'
 recording=json.loads((ROOT/'media/walkthrough-034b/screen-034.receipt.json').read_text())
 assembly=json.loads(ORIG.with_suffix('.mp4.receipt.json').read_text())
 assert h(ORIG.read_bytes())==assembly['output_sha256']
 assert h(page.read_bytes())==recording['page_sha256']
 assert h(datafile.read_bytes())==recording['data_sha256']
 D=json.loads(datafile.read_text())
 for path,expected in D['sources'].items():assert h((ROOT/path).read_bytes())==expected,path
 durations=[float(x) for x in re.findall(r'data-t="([0-9.]+)"',page.read_text())]
 durations[-1]+=2.856
 labels=['The incident','Device first','Controlled fault','Semgrep','Custody','ClickHouse','Akash GPU','Separate custody branch','Live vs replay','Privacy and rights']
 scenes=[];start=0
 for i,(dur,label) in enumerate(zip(durations,labels)):
  lane='gpu' if i in [6,7] else 'incident'
  scenes.append({'scene':i+1,'label':label,'expected_start_s':round(start,3),'expected_end_s':round(start+dur,3),'relation':'PRESENTS_RECORDED_BRANCH','branch':lane,'source_mmr_root':D[lane]['expected_mmr_root'],'source_fco_ids':[x['fco_id'] for x in D[lane]['ledger']]})
  start+=dur
 manifest={'schema':'antigense.FrameSceneManifest.v039','parent':'walkthrough-034b','source_video_sha256':assembly['output_sha256'],'source_audio_sha256':assembly['audio_input_sha256'],'source_page_sha256':recording['page_sha256'],'source_data_sha256':recording['data_sha256'],'source_files':D['sources'],'scenes':scenes,'timing_scope':'Expected presentation timing from page; not wall-clock attestation or measured narration alignment','recording_timeline_finished':recording['timeline_finished'],'browser_results_recorded':recording['in_browser_recompute'],'watermark_scheme':'NEW visible DRM-free overlay; prior watermark implementation UNRECOVERED'}
 write(BASE/'scene-manifest.json',manifest);mh=h(canon(manifest))
 print('RUNNING source bindings PASS; decoding all source frames',flush=True)
 raw=decoded(ORIG);(BASE/'source-framemd5.txt').write_text(raw)
 tb=re.search(r'#tb 0: (\d+)/(\d+)',raw);num,den=map(int,tb.groups())
 records=[];items=[]
 for line in raw.splitlines():
  if line.startswith('#') or not line.strip():continue
  fields=[x.strip() for x in line.split(',')];pts=int(fields[2]);sec=pts*num/den
  scene=next((s for s in scenes if s['expected_start_s']<=sec<s['expected_end_s']),scenes[-1])
  e={'schema':'antigense.DecodedFrameOccurrence.v039','frame_index':len(records),'pts':pts,'time_base':[num,den],'pixel_format':'yuv420p','decoded_frame_sha256':fields[5],'source_video_sha256':assembly['output_sha256'],'scene_manifest_sha256':mh,'expected_scene':scene['scene'],'relation':'FRAME_OF_RECORDED_PRESENTATION','source_mmr_root':scene['source_mmr_root']}
  eh=h(canon(e));records.append(e);items.append({'event_hash':eh,'fco_id':'fco:sha256:'+eh})
 (BASE/'source-frame-occurrences.jsonl').write_bytes(b''.join(canon(x)+b'\n' for x in records))
 mmr=K.mmr(items);assert K.independent_mmr_root(items)==mmr['root']
 write(BASE/'source-frame-mmr.json',mmr)
 samples=BASE/'samples';samples.mkdir()
 times=[5,30,48,60,72,90,110,125,141]
 for t in times:
  subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(t),'-i',str(ORIG),'-frames:v','1',str(samples/f'frame-{t:03d}.png')],check=True)
 print('RUNNING all source frames committed; OCR sample checks',flush=True)
 ocr=json.loads(run(['swift',str(ROOT/'agent/frame_ocr039.swift')]+[str(x) for x in sorted(samples.glob('*.png'))]))
 checks=[]
 for o in ocr:
  t=int(re.search(r'frame-(\d+)',o['file'])[1]);scene=next(s for s in scenes if s['expected_start_s']<=t<s['expected_end_s'])
  text=' '.join(o.get('lines',[]));pattern=f"scene {scene['scene']}/10"
  clock=f"{t//60}:{t%60:02d}"
  checks.append({'seconds':t,'image':o['file'],'image_sha256':h((samples/o['file']).read_bytes()),'expected_scene':scene['scene'],'scene_marker_observed':pattern.lower() in text.lower(),'clock_expected':clock,'clock_observed':clock in text,'ocr':o,'human_visual_review':'NOT_TESTED'})
 write(BASE/'sample-checks.json',checks)
 overlay=f"FCG039 | source {assembly['output_sha256'][:12]} | manifest {mh[:12]} | frame %{{n}} | %{{pts\\:hms}}"
 target=MEDIA/'demo-039-watermarked-review.mp4'
 print('RUNNING encoding visible watermark successor',flush=True)
 subprocess.run(['ffmpeg','-nostdin','-n','-v','error','-i',str(ORIG),'-vf',"drawtext=fontfile=/System/Library/Fonts/Monaco.ttf:text='"+overlay+"':x=20:y=20:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.8:boxborderw=5",'-map','0:v:0','-map','0:a:0','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','copy','-metadata','comment=FCG039 scene manifest SHA256 '+mh,'-movflags','+faststart',str(target)],check=True)
 wmraw=decoded(target);(BASE/'watermarked-framemd5.txt').write_text(wmraw)
 report={'id':'039','parent':'038','source_frame_mmr_root':mmr['root'],'frame_count':len(records),'independent_mmr_recompute':True,'scene_manifest_sha256':mh,'input_video_sha256':assembly['output_sha256'],'watermarked_video_sha256':h(target.read_bytes()),'watermarked_frame_digest_file_sha256':h(wmraw.encode()),'samples':len(checks),'sample_scene_checks_pass':all(c['scene_marker_observed'] for c in checks),'sample_clock_checks_pass':all(c['clock_observed'] for c in checks),'recording_timeline_finished':False,'watermark':'IMPLEMENTED_AND_EXECUTED new successor; DRM-free; not a signature','full_frame_semantic_verification':'NOT_TESTED','real_time_calculation_attestation':'NOT_TESTED; original recorder reports PASS at end and sampled frames show display','narration_alignment':'NOT_TESTED','publication':'NOT_EXECUTED','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ffmpeg_version':run(['ffmpeg','-version']).splitlines()[0]}
 write(BASE/'report.json',report);(BASE/'recording-receipt034.json').write_bytes((ROOT/'media/walkthrough-034b/screen-034.receipt.json').read_bytes());(BASE/'assembly-receipt034.json').write_bytes(ORIG.with_suffix('.mp4.receipt.json').read_bytes())
 print(json.dumps(report,indent=2),flush=True)
def verify():
 manifest=json.loads((BASE/'scene-manifest.json').read_text());assert h(canon(manifest))==json.loads((BASE/'report.json').read_text())['scene_manifest_sha256']
 records=[json.loads(x) for x in (BASE/'source-frame-occurrences.jsonl').read_text().splitlines()]
 items=[{'event_hash':h(canon(e)),'fco_id':'fco:sha256:'+h(canon(e))} for e in records]
 stored=json.loads((BASE/'source-frame-mmr.json').read_text());assert K.mmr(items)==stored;assert K.independent_mmr_root(items)==stored['root']
 assert decoded(ORIG)==(BASE/'source-framemd5.txt').read_text()
 report=json.loads((BASE/'report.json').read_text());video=MEDIA/'demo-039-watermarked-review.mp4'
 assert h(video.read_bytes())==report['watermarked_video_sha256'];assert decoded(video)==(BASE/'watermarked-framemd5.txt').read_text()
 print('PASS frame ledger, independent MMR and source/successor decoded-frame readback')
if __name__=='__main__':
 {'build':build,'verify':verify}[sys.argv[1]]()
