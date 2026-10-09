#!/usr/bin/env python3
"""Complete failed frame039 as a preserved successor with a DRM-free PNG overlay."""
from pathlib import Path
import json,subprocess,shutil,hashlib,sys,importlib.util
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('audit',ROOT/'agent/frame_audit039.py')
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
E=ROOT/'evidence/frame039r1';M=ROOT/'media/walkthrough-039r1'
def main():
 E.mkdir(exist_ok=False);M.mkdir(exist_ok=False)
 (ROOT/'evidence/frame039/failure.json').write_text(json.dumps({'state':'FAILED','operation':'visible watermark encode','reason':'ffmpeg drawtext filter unavailable','successor':'frame039r1'}))
 for name in ['scene-manifest.json','source-frame-occurrences.jsonl','source-frame-mmr.json','source-framemd5.txt','sample-checks.json']:shutil.copyfile(ROOT/'evidence/frame039'/name,E/name)
 r=json.loads((E/'source-frame-mmr.json').read_text());checks=json.loads((E/'sample-checks.json').read_text())
 label='FCG039R1 | source ab69925bd191 | frame-MMR '+r['root'][:20]+' | exact frame PTS in committed sidecar'
 subprocess.run(['swift',str(ROOT/'agent/watermark039r1.swift'),str(E/'watermark.png'),label],check=True)
 target=M/'demo-039r1-watermarked-review.mp4'
 print('RUNNING successor PNG overlay encoding',flush=True)
 subprocess.run(['ffmpeg','-nostdin','-n','-v','error','-i',str(A.ORIG),'-i',str(E/'watermark.png'),'-filter_complex','[0:v][1:v]overlay=20:65:format=auto[v]','-map','[v]','-map','0:a:0','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','copy','-metadata','comment=FCG039R1 source decoded-frame MMR '+r['root'],'-movflags','+faststart',str(target)],check=True)
 raw=A.decoded(target);(E/'watermarked-framemd5.txt').write_text(raw)
 report={'id':'039R1','parent':'039','watermark':'IMPLEMENTED_AND_EXECUTED DRM-free visible pointer; not signed','source_frame_mmr_root':r['root'],'source_frame_count':r['leaf_count'],'original_video_sha256':A.h(A.ORIG.read_bytes()),'watermarked_video_sha256':A.h(target.read_bytes()),'watermark_png_sha256':A.h((E/'watermark.png').read_bytes()),'sample_scene_passes':sum(x['scene_marker_observed'] for x in checks),'samples':len(checks),'sample_clocks_pass':all(x['clock_observed'] for x in checks),'sample_at_48s':'EXPECTED_SCENE_MISMATCH; boundary timing or OCR unresolved, original retained','full_frame_semantics':'NOT_TESTED','live_calculation_attestation':'NOT_TESTED; recorded browser results and sampled display only','narration_alignment':'NOT_TESTED','publication':'NOT_EXECUTED'}
 A.write(E/'report.json',report)
 print(json.dumps(report,indent=2),flush=True)
def verify():
 records=[json.loads(x) for x in (E/'source-frame-occurrences.jsonl').read_text().splitlines()]
 items=[{'event_hash':A.h(A.canon(e)),'fco_id':'fco:sha256:'+A.h(A.canon(e))} for e in records]
 stored=json.loads((E/'source-frame-mmr.json').read_text());assert A.K.mmr(items)==stored;assert A.K.independent_mmr_root(items)==stored['root']
 assert A.decoded(A.ORIG)==(E/'source-framemd5.txt').read_text()
 target=M/'demo-039r1-watermarked-review.mp4';report=json.loads((E/'report.json').read_text())
 assert A.h(target.read_bytes())==report['watermarked_video_sha256'];assert A.decoded(target)==(E/'watermarked-framemd5.txt').read_text()
 print('PASS independent frame MMR, original/successor pixel readback; sample mismatch remains unresolved')
if __name__=='__main__':{'build':main,'verify':verify}[sys.argv[1]]()
