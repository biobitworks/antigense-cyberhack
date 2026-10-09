#!/usr/bin/env python3
import http.server,json,os,secrets,threading,time,urllib.parse
from pathlib import Path
import cascade
TOKEN=secrets.token_hex(32);HOST='127.0.0.1:8790';busy=threading.Lock()
def snapshot():
 try:
  run=cascade.load(cascade.LATEST);run={k:v for k,v in run.items() if k!='custody'}
 except Exception:run=None
 mem=None
 try:
  import subprocess
  x=subprocess.run(['sysctl','-n','hw.memsize'],capture_output=True,text=True,timeout=1);mem=int(x.stdout)
 except Exception:pass
 return {'source':'LIVE_OS_POLL','observed_epoch_ms':int(time.time()*1000),'cpu_count':os.cpu_count(),'memory_bytes':mem,'load_average':list(os.getloadavg()),'gpu_temperature':'UNKNOWN','gpu_ecc':'UNKNOWN','run':run}
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(cascade.ROOT/'public'),**k)
 def valid(self):return self.headers.get('Host')==HOST
 def reply(self,o,status=200):
  b=json.dumps(o).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(b)
 def do_GET(self):
  if not self.valid():return self.reply({'error':'invalid host'},403)
  path=urllib.parse.urlparse(self.path).path
  if path=='/api/session':return self.reply({'token':TOKEN})
  if path=='/api/snapshot':return self.reply(snapshot())
  if path.startswith('/api/'):return self.reply({'error':'not found'},404)
  if path not in ['/', '/index.html','/verify.js','/data/run.json','/data/proof.json','/demo.mp4']:return self.reply({'error':'not found'},404)
  super().do_GET()
 def do_POST(self):
  if not self.valid() or self.headers.get('Origin')!='http://'+HOST or not secrets.compare_digest(self.headers.get('X-Custody-Token',''),TOKEN):return self.reply({'error':'origin/session check failed'},403)
  try:
   size=int(self.headers.get('Content-Length','0'))
   if size>4096 or size<2:return self.reply({'error':'request size'},400)
   o=json.loads(self.rfile.read(size));path=urllib.parse.urlparse(self.path).path
   if path not in ['/api/run','/api/approve']:return self.reply({'error':'not found'},404)
   if path=='/api/approve':
    current=cascade.load(cascade.LATEST)
    if current['phase']!='awaiting_review' or current['mmr_root']!=o.get('expected_mmr'):return self.reply({'error':'stale review'},409)
   if not busy.acquire(blocking=False):return self.reply({'error':'busy'},409)
   def work():
    try:
     if path=='/api/run':cascade.run('local')
     else:cascade.approve(o['expected_mmr'],'local-browser-action',o.get('provenance','UNSIGNED_LOCAL_REVIEW'))
    except Exception as e:print('Action failed:',type(e).__name__,str(e),flush=True)
    finally:busy.release()
   threading.Thread(target=work,daemon=True).start();return self.reply({'accepted':True},202)
  except Exception:return self.reply({'error':'invalid request'},400)
 def log_message(self,*a):pass
if __name__=='__main__':
 print('Antigense local cockpit http://'+HOST,flush=True);http.server.ThreadingHTTPServer(('127.0.0.1',8790),Handler).serve_forever()
