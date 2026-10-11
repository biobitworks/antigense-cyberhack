#!/usr/bin/env python3
"""Successor recorder 040. Records an UNCHANGED copy of walkthrough-034 (page+data byte hashes checked) from a NEW folder,
with out-of-page DOM observers logging scene activation and proof start/leaf progress/result.
Event times are page epoch ms (performance.timeOrigin+now). Video is NOT trimmed; PTS mapping is calibrated afterwards from decoded frames.
These are recorder logs, not independent attestation. No sponsor calls; page is local and static.
Usage: record_walkthrough040.py <newoutdir>"""
import argparse,hashlib,json,shutil,subprocess,sys,threading,time,http.server,functools
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent;ap=argparse.ArgumentParser();ap.add_argument("outdir");ap.add_argument("--site-dir");ap.add_argument("--page",default="walkthrough-034.html");ap.add_argument("--seconds",type=float,default=220);A_=ap.parse_args();out=Path(A_.outdir).resolve();out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prev=json.loads((ROOT/"media/walkthrough-034b/screen-034.receipt.json").read_text())
if A_.site_dir:
    site=Path(A_.site_dir).resolve()
else:
    site=out/"site";(site/"data").mkdir(parents=True)
    shutil.copy(ROOT/"public/walkthrough-034.html",site/"walkthrough-034.html");shutil.copy(ROOT/"public/data/walkthrough-034.json",site/"data/walkthrough-034.json")
    assert sha(site/"walkthrough-034.html")==prev["page_sha256"] and sha(site/"data/walkthrough-034.json")==prev["data_sha256"],"page/data differ from the recorded 034b inputs"
OBS=r"""
(()=>{window.__ev=[];const T=()=>performance.timeOrigin+performance.now();
const log=(o)=>window.__ev.push(Object.assign({epoch_ms:T(),perf_ms:performance.now()},o));
const start=()=>{const idOf=n=>{while(n&&!(n.id))n=n.parentNode;return n&&n.id};
new MutationObserver(ms=>{for(const m of ms){
 const t=m.target;
 if(m.type==='attributes'&&t.classList){
  if(t.classList.contains('scene')&&t.classList.contains('on')&&m.oldValue!==null&&!(m.oldValue||'').split(' ').includes('on')){const all=[...document.querySelectorAll('.scene')];log({type:'scene_activation',scene:all.indexOf(t)+1})}
  if(t.classList.contains('leaf')&&t.classList.contains('ok')&&!(m.oldValue||'').split(' ').includes('ok')){const idx=[...t.parentNode.children].indexOf(t);log({type:'proof_leaf_progress',proof:t.parentNode.id.replace('-leaves',''),leaf_index:idx+1,leaf_count:t.parentNode.children.length})}
  if(t.id&&/^(inc|gpu|rev|fcg)-res$/.test(t.id)&&t.className!==m.oldValue)log({type:'proof_result_class',proof:t.id.replace('-res',''),cls:t.className})}
 else{const id=idOf(t);
  if(/^(inc|gpu|rev|fcg)-exp$/.test(id))log({type:'proof_start',proof:id.slice(0,3),expected_root:(document.getElementById(id).textContent||'')});
  if(/^(inc|gpu|rev|fcg)-got$/.test(id))log({type:'proof_recomputed_root',proof:id.slice(0,3),root:document.getElementById(id).textContent});
  if(/^(inc|gpu|rev|fcg)-res$/.test(id))log({type:'proof_result',proof:id.slice(0,3),text:document.getElementById(id).textContent})}}
}).observe(document.documentElement,{subtree:true,attributes:true,attributeOldValue:true,childList:true,characterData:true})};
if(document.documentElement)start();else document.addEventListener('DOMContentLoaded',start)})();
"""
srv=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(site)))
srv.RequestHandlerClass.log_message=lambda *a:None
port=srv.server_address[1];threading.Thread(target=srv.serve_forever,daemon=True).start()
chromium=str(next((Path.home()/"Library/Caches/ms-playwright/chromium_headless_shell-1234").glob("*/chrome-headless-shell")))
raw=out/"raw";marks={}
print("START record040",flush=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=chromium)
    marks["context_create_epoch_s"]=time.time();marks["context_create_mono_s"]=time.monotonic()
    ctx=b.new_context(viewport={"width":1440,"height":900},record_video_dir=str(raw),record_video_size={"width":1440,"height":900})
    ctx.add_init_script(OBS)
    page=ctx.new_page();marks["page_created_epoch_s"]=time.time();marks["page_created_mono_s"]=time.monotonic()
    errs=[];page.on("pageerror",lambda e:errs.append(str(e)))
    marks["goto_start_epoch_s"]=time.time();page.goto("http://127.0.0.1:%d/%s?autoplay=1"%(port,A_.page),wait_until="networkidle");marks["goto_end_epoch_s"]=time.time()
    t=time.monotonic()
    while not page.title().endswith("done") and time.monotonic()-t<A_.seconds:
        page.wait_for_timeout(5000);print("RUNNING page_s=%.0f title_done=%s"%(time.monotonic()-t,page.title().endswith("done")),flush=True)
    done=page.title().endswith("done");page.wait_for_timeout(2500)
    ev=page.evaluate("window.__ev");res={k:page.inner_text(k) for k in("#inc-res","#gpu-res")}
    marks["context_close_epoch_s"]=time.time();ctx.close();b.close()
webm=next(raw.glob("*.webm"));mp4=out/"screen-040.mp4"
subprocess.run(["ffmpeg","-nostdin","-n","-v","error","-i",str(webm),"-an","-c:v","libx264","-crf","14","-pix_fmt","yuv420p","-r","30",str(mp4)],check=True)
dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(mp4)],text=True))
(out/"runtime_events.jsonl").write_text("".join(json.dumps(e,sort_keys=True)+"\n" for e in ev))
rec={"id":"screen-040","parent":"screen-034 (034b)","page":A_.page,"page_sha256":sha(site/A_.page),"data_sha256":sha(site/"data/walkthrough-034.json"),"raw_webm_sha256":sha(webm),"mp4_sha256":sha(mp4),"mp4_seconds":dur,"trimmed_lead_seconds":0,"timeline_finished":done,"in_browser_recompute":res,"page_errors":errs,"event_count":len(ev),"marks":marks,"recorder":"headless Chromium viewport only; recorder log, not independent attestation","publication":"NOT_EXECUTED","paid_compute":"NONE","ingestion":"NONE"}
(out/"screen-040.receipt.json").write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
print("PASS" if done and not errs else "FAIL",json.dumps({k:rec[k] for k in("mp4_seconds","timeline_finished","in_browser_recompute","event_count","page_errors")}),flush=True)
sys.exit(0 if done and not errs else 1)
