#!/usr/bin/env python3
"""Build the successor walkthrough page: an unchanged copy of public/walkthrough-034.html (scenes 1-10 byte-identical)
plus appended scenes 11 (Semgrep + end-to-end review) and 12 (Merkle breakpoints + FCG update). Writes ONLY to the new site dir.
Usage: build_page040.py <new_site_dir> <review_run_dir>"""
import hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;S=Path(sys.argv[1]).resolve();RUN=Path(sys.argv[2]).resolve();(S/"data").mkdir(parents=True)
src=(ROOT/"public/walkthrough-034.html").read_text()
shutil.copy(ROOT/"public/data/walkthrough-034.json",S/"data/walkthrough-034.json");shutil.copy(RUN/"site_data.json",S/"data/review040.json")
sec11='''<section class="scene" data-t="20.0"><div class="kicker">07 · Semgrep, then a full code review</div><h2>Semgrep found <span class="warn" id="r-sg-n"></span> issue. A full read found <em class="good" id="r-all"></em>.</h2><div class="grid"><div class="card"><div class="kicker">Semgrep CE · static scan of our own AI-written code</div><table id="r-sg-t"></table><p class="mono" id="r-sg-note" style="margin-top:10px"></p></div><div class="card"><div class="kicker">Controlled test (fixture only)</div><table id="r-demo-t"></table><div class="kicker" style="margin-top:14px">Review by reading · not found by Semgrep</div><div class="mono" id="r-find" style="white-space:pre-line"></div></div></div></section>
<section class="scene" data-t="30.0"><div class="kicker">08 · Merkle breakpoints for review</div><h2>Change one file. <em class="good">The tree points to it.</em></h2><div class="grid"><div class="card"><div class="kicker" id="rev-k">Code tree, recomputed now from recorded leaves</div><div class="leaves" id="rev-leaves"></div><div class="mono">expected <span id="rev-exp"></span></div><div class="mono">computed <span id="rev-got"></span></div><div class="big" id="rev-res"></div><pre id="rev-bp" style="margin-top:10px;max-height:150px"></pre></div><div class="card"><div class="kicker">Review steps appended to the FCG, each with typed edges</div><div class="leaves" id="fcg-leaves"></div><div class="mono">expected <span id="fcg-exp"></span></div><div class="mono">computed <span id="fcg-got"></span></div><div class="big" id="fcg-res"></div><table id="rev-m" style="margin-top:8px"></table></div></div></section>
'''
js='''
async function merkleLevels(strs,onLeaf){let lv=[];for(let i=0;i<strs.length;i++){const h1=await sha(new TextEncoder().encode(strs[i]));lv.push(await sha(cat(new Uint8Array([0]),unhex(h1))));onLeaf&&await onLeaf(i)}
 const levels=[lv];while(lv.length>1){const nx=[];for(let i=0;i<lv.length;i+=2)nx.push(i+1<lv.length?await sha(cat(new Uint8Array([1]),unhex(lv[i]),unhex(lv[i+1]))):lv[i]);lv=nx;levels.push(lv)}return levels}
function localize(a,b){let i=0,c=1;for(let d=a.length-2;d>=0;d--){const l=2*i,r=l+1;if(l<a[d].length){c++;if(a[d][l]!==b[d][l]){i=l;continue}}c++;i=r}return [i,c]}
let R;const row=(a,b,c)=>`<tr><td>${a}</td><td>${b}</td>${c!==undefined?`<td>${c}</td>`:''}</tr>`;
async function showSemgrep(){if(!R)R=await (await fetch('data/review040.json',{cache:'no-store'})).json();
 $('r-sg-n').textContent=R.semgrep.findings;$('r-all').textContent=R.findings.total+' findings';
 $('r-sg-t').innerHTML=row('tool','Semgrep CE '+R.semgrep.version)+row('rule sets',R.semgrep.sets.join(', '))+row('files scanned',`${R.semgrep.files} (${R.semgrep.tree_files} in the reviewed tree, ${R.semgrep.untracked_scanned} untracked and not reviewed)`)+row('finding',R.semgrep.finding);
 $('r-sg-note').textContent='Semgrep CE, not Guardian. Registry rules, not exhaustive. Zero findings in a file means only that this scan found none.';
 const D=R.demos;$('r-demo-t').innerHTML=row('exec() path ran attacker-controlled fixture',D.exec_runs_fixture,'<span class="bad">yes</span>')+row('exec-free evaluator ran it',!D.safe_eval_blocks,'<span class="good">no</span>')+row('deny-everything repair',D.deny_all_rejected?'rejected':'accepted','blocks unauthorized, breaks healthy work')+row('same exec risk elsewhere (cascade.py)',D.cascade_exec,'not flagged by Semgrep');
 $('r-find').textContent=R.findings.list.map(f=>`${f.id} [${f.severity}] ${f.file}${f.semgrep?'  (Semgrep)':''}`).join('\\n')+`\\nSemgrep CE detected ${R.findings.semgrep_detectable} of ${R.findings.total}.`}
async function showReview(){if(!R)R=await (await fetch('data/review040.json',{cache:'no-store'})).json();
 const T=R.tree,box=$('rev-leaves');box.replaceChildren();T.paths.forEach((p,i)=>{const d=document.createElement('div');d.className='leaf';d.title=p;d.textContent=i+1;d.style.width='44px';if(T.has_finding[i])d.style.borderColor='var(--orange)';box.append(d)});
 $('rev-exp').textContent=T.root;
 const lv=await merkleLevels(T.canon,async i=>{box.children[i].classList.add('ok');await sleep(110)});
 $('rev-got').textContent=lv[lv.length-1][0];const ok=lv[lv.length-1][0]===T.root;$('rev-res').textContent=ok?'PASS · tree root matches':'FAIL · roots differ';$('rev-res').className='big '+(ok?'good':'bad');
 const ti=R.breakpoints.tamper_index;const c2=T.canon.slice();c2[ti]=c2[ti].replace(/"sha256":"([0-9a-f])/,(m,d)=>'"sha256":"'+(d==='0'?'1':'0'));
 const lv2=await merkleLevels(c2);const [li,cmp]=localize(lv,lv2);
 $('rev-bp').textContent=`One byte changed in ${T.paths[ti]}\\nroot now ${lv2[lv2.length-1][0].slice(0,20)}…  (was ${lv[lv.length-1][0].slice(0,20)}…)\\nbreakpoint found: leaf ${li+1} = ${T.paths[li]}\\n${cmp} node comparisons from the root, not ${T.paths.length}`;
 await sleep(1500);
 const F=R.fcg,fb=$('fcg-leaves');fb.replaceChildren();F.ledger.forEach((r,i)=>{const d=document.createElement('div');d.className='leaf';d.textContent='#'+r.event_index;fb.append(d)});
 $('fcg-exp').textContent=F.expected_root;const got=await mmr(F.ledger,async i=>{fb.children[i].classList.add('ok');await sleep(260)});
 $('fcg-got').textContent=got;const ok2=got===F.expected_root;$('fcg-res').textContent=ok2?'PASS · roots match':'FAIL · roots differ';$('fcg-res').className='big '+(ok2?'good':'bad');
 const I=R.incremental;$('rev-m').innerHTML=row('FCG now',`${F.nodes} nodes · ${F.edges} typed edges`)+row('files changed since '+I.baseline,`${I.changed} of ${I.files} (${I.lines_changed} of ${I.lines_total} lines)`)+row('Semgrep wall time, full',I.semgrep_full_s.map(x=>x[0]).join(' / ')+' s')+row('Semgrep wall time, changed files only',I.semgrep_changed_s.map(x=>x[0]).join(' / ')+' s')+row('review-time saving','<span class="warn">NOT_TESTED</span> (no matched baseline)')}
'''
a="const run=async(i)=>{scenes.forEach((s,j)=>s.classList.toggle('on',j===i));$('sc').textContent=`scene ${i+1}/${scenes.length}`;\n if(i===4)showChain('inc',D.incident.ledger,D.incident.expected_mmr_root);if(i===7)showChain('gpu',D.gpu.ledger,D.gpu.expected_mmr_root)};"
assert a in src
b=a.replace("if(i===7)showChain('gpu',D.gpu.ledger,D.gpu.expected_mmr_root)};","if(i===7)showChain('gpu',D.gpu.ledger,D.gpu.expected_mmr_root);if(i===10)showSemgrep();if(i===11)showReview()};")
out=src.replace(a,js+b)
mark="</main>"
assert mark in out
out=out.replace(mark,sec11+mark,1)
out=out.replace("Walkthrough 034 (recorded replay)","Walkthrough 040 (recorded replay, successor)").replace("RECORDED REPLAY · WALKTHROUGH 034","RECORDED REPLAY · WALKTHROUGH 040")
# scenes 1-10 durations unchanged; last-scene padding moves to the new last scene automatically
(S/"walkthrough-040.html").write_text(out)
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
json.dump({"source_page_sha256":h(ROOT/"public/walkthrough-034.html"),"page_sha256":h(S/"walkthrough-040.html"),"data_sha256":h(S/"data/review040.json"),"base_data_sha256":h(S/"data/walkthrough-034.json"),"scenes_1_10":"byte-identical markup from 034 (only title/tag text and run() hooks changed)"},open(S/"page.receipt.json","w"),indent=1)
print("built",S/"walkthrough-040.html")
