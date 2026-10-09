#!/usr/bin/env python3
import argparse,hashlib,importlib.util,json,os,shutil,struct,subprocess,sys,time,uuid,urllib.request,urllib.parse
from pathlib import Path
import custody
ROOT=Path(__file__).resolve().parents[1]
RUNTIME=ROOT/'.runtime'
LATEST=RUNTIME/'latest.json'
def sha(x):return hashlib.sha256(x).hexdigest()
def atomic(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(o,sort_keys=True,indent=2));tmp.replace(p)
def load(p):return json.loads(p.read_text())
def auth(name,a,h):
 spec=importlib.util.spec_from_file_location('policy_'+name,ROOT/'fixtures'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m.authorize(a,h)
def export(run):
 base=Path(run['custody']);g=load(base/'genesis.json');rows=custody.rows(base)
 proof={'genesis':g,'ledger':rows,'objects':[load(base/x['object_file']) for x in rows[1:]],'prefixes':[load(base/f'prefix-{i:06d}.json') for i in range(1,len(rows)+1)]}
 run['verification']=custody.verify(base,g['project_root']);run['project_root']=g['project_root'];run['mmr_root']=custody.mmr(rows)['root'];run['leaf_count']=len(rows)
 atomic(LATEST,run);atomic(ROOT/'public/data/proof.json',proof);atomic(ROOT/'public/data/run.json',{k:v for k,v in run.items() if k!='custody'})
 return run
class Recorder:
 def __init__(self,run):self.run=run
 def step(self,name,state,value,checks):
  observation={'name':name,'state':state,'value':value,'checks':checks,'origin':'local-execution','recorded_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
  receipt=custody.append_step(Path(self.run['custody']),observation)
  self.run['stages'].append({'name':name,'state':state,'value':value,'checks':checks,'receipt':receipt});export(self.run);print(json.dumps({'stage':name,'state':state,**receipt}),flush=True)
  return receipt
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
def ai(route):
 facts={'fault':'software-injected byte corruption','integrity_mismatch':True,'unsafe_fallback':'health failure returns True without authorization','task':'Give a short root-cause hypothesis and recommend denying unauthorized requests even during hardware failure. No commands or code execution.'}
 prompt=json.dumps(facts,sort_keys=True);url='http://127.0.0.1:11434/api/generate';headers={'Content-Type':'application/json'}
 if route=='akash':
  url=os.environ.get('ANTIGENSE_AKASH_URL','');token=os.environ.get('ANTIGENSE_AKASH_TOKEN','')
  parsed=urllib.parse.urlparse(url)
  if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or not token:return {'state':'NOT_TESTED','reason':'authenticated HTTPS Akash endpoint not configured','attestation':'NOT_TESTED'}
  headers['Authorization']='Bearer '+token
 model=os.environ.get('ANTIGENSE_MODEL','qwen2.5:0.5b')
 body={'model':model,'prompt':prompt,'stream':False,'options':{'temperature':0,'seed':9,'num_predict':160},'keep_alive':'2m'}
 try:
  t=time.monotonic();req=urllib.request.Request(url,data=json.dumps(body).encode(),headers=headers)
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
  with opener.open(req,timeout=45) as r:
   raw=r.read(262145)
  if len(raw)>262144:raise ValueError('response exceeds bound')
  result=json.loads(raw);text=result.get('response')
  if not isinstance(text,str) or not text.strip():raise ValueError('no model response')
  return {'state':'OBSERVED','route':route,'model':model,'response':text[:5000],'request_sha256':sha(json.dumps(body,sort_keys=True).encode()),'response_sha256':sha(raw),'elapsed_ms':round((time.monotonic()-t)*1000,3),'gpu_execution':'NOT_TESTED','attestation':'NOT_TESTED','claim':'observed model advice; no execution authority; endpoint ownership unverified for Akash'}
 except Exception as e:return {'state':'FAILED','route':route,'error_class':type(e).__name__,'reason':'inference failed; no advice invented'}
def scan(name):
 exe=ROOT/'.venv/bin/semgrep';cmd=str(exe) if exe.exists() else shutil.which('semgrep')
 if not cmd:return {'state':'NOT_TESTED','reason':'Semgrep executable unavailable','findings':None}
 env=dict(os.environ);env.pop('SEMGREP_APP_TOKEN',None);env['SEMGREP_SEND_METRICS']='off';env['SEMGREP_ENABLE_VERSION_CHECK']='0'
 args=[cmd,'scan','--config',str(ROOT/'rules/fallback.yaml'),'--metrics=off','--disable-version-check','--json','--no-git-ignore',str(ROOT/'fixtures'/f'{name}.py')]
 try:
  proc=subprocess.run(args,capture_output=True,text=True,timeout=30,env=env,cwd=ROOT);o=json.loads(proc.stdout)
  if proc.returncode!=0 or o.get('errors'):return {'state':'FAILED','exit_code':proc.returncode,'reason':'scan errors','error_count':len(o.get('errors',[]))}
  findings=[{'rule':x['check_id'],'line':x['start']['line'],'message':x['extra']['message']} for x in o['results']]
  return {'state':'OBSERVED','version':o.get('version'),'findings':findings,'count':len(findings),'target_sha256':sha((ROOT/'fixtures'/f'{name}.py').read_bytes()),'rule_sha256':sha((ROOT/'rules/fallback.yaml').read_bytes()),'json_output_sha256':sha(proc.stdout.encode()),'metrics':'off','target':f'fixtures/{name}.py'}
 except Exception as e:return {'state':'FAILED','reason':'scan failed','error_class':type(e).__name__}
def run(route='local'):
 RUNTIME.mkdir(exist_ok=True);lock=RUNTIME/'run.lock';lock.mkdir()
 try:
  ident='run-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+uuid.uuid4().hex[:8];base=RUNTIME/ident/'custody';g=custody.freeze(base,ROOT)
  r={'id':ident,'custody':str(base),'stages':[],'phase':'running','mode':'EXECUTED_CONTROLLED_SIMULATION','sponsors':{'Semgrep':'NOT_TESTED','Akash':'NOT_TESTED','Pi':'NOT_TESTED'},'human_action':'PENDING','active_policy':'before'};rec=Recorder(r)
  expected=load(ROOT/'policy.json')['expected_arithmetic'];t=time.monotonic();actual=sum(i*i for i in range(1000));raw=struct.pack('>Q',actual)
  rec.step('01 Baseline worker','OBSERVED',{'arithmetic':actual,'expected':expected,'output_sha256':sha(raw),'elapsed_ms':round((time.monotonic()-t)*1000,3),'fault':'NONE'}, {'arithmetic_matches':actual==expected})
  b=bytearray(raw);b[0]^=1;corrupted=bytes(b);detected=sha(corrupted)!=sha(raw)
  rec.step('02 Injected integrity fault','OBSERVED',{'fault':'SIMULATED_BYTE_XOR','byte_index':0,'xor_mask':1,'original_sha256':sha(raw),'corrupted_sha256':sha(corrupted),'detected':detected,'hardware_fault_observed':False},{'fault_detected':detected,'physical_fault_observed':False})
  allowed=auth('before',False,not detected)
  rec.step('03 Unsafe fallback reproduced','OBSERVED',{'unauthorized_request_allowed':allowed,'scope':'pure boolean teaching fixture; no real access granted'},{'bypass_reproduced':allowed,'security_policy_pass':not allowed})
  s=scan('before');r['sponsors']['Semgrep']=s['state'];rec.step('04 Semgrep before scan',s['state'],s,{'finding_present':s.get('count',0)>0})
  result=ai(route);r['sponsors']['Akash']=result['state'] if route=='akash' else 'NOT_TESTED';rec.step('05 AI incident analysis',result['state'],result,{'response_observed':result['state']=='OBSERVED','ai_authorized_to_patch':False,'akash_attestation_verified':False})
  pi={'state':'NOT_TESTED','packet':'docs/PI_INTAKE.md','request':'reproduce, review attack path and patch, verify no variants','local_deployment':'UNKNOWN','api':'UNKNOWN','not_a_pi_response':True}
  rec.step('06 Pi review handoff','NOT_TESTED',pi,{'pi_execution_observed':False,'intake_prepared':True})
  rec.step('07 Review gate','OBSERVED',{'pending':True,'pinned_patch_sha256':sha((ROOT/'fixtures/after.py').read_bytes()),'action':'requires current MMR-bound local action; signature NOT_SIGNED'},{'patch_applied':False,'gate_enforced':True})
  r['phase']='awaiting_review';export(r);return r
 finally:lock.rmdir()
def approve(expected,actor,provenance):
 lock=RUNTIME/'run.lock';lock.mkdir()
 try:
  r=load(LATEST);base=Path(r['custody']);v=custody.verify(base,r['project_root'])
  if not v['PASS'] or not custody.verify_artifacts(base,ROOT) or r['phase']!='awaiting_review' or custody.mmr(custody.rows(base))['root']!=expected:raise ValueError('stale or invalid approval; refusing change')
  rec=Recorder(r);r['human_action']={'actor':actor[:100],'provenance':provenance[:100],'identity':'UNVERIFIED','signature':'NOT_SIGNED','approved_mmr':expected}
  rec.step('08 Local review action','OBSERVED',r['human_action'],{'mmr_bound':True,'cryptographic_identity_verified':False})
  r['active_policy']='after';rec.step('09 Pinned fail-closed fix','OBSERVED',{'scope':'teaching fixture selected; no host patch','sha256':sha((ROOT/'fixtures/after.py').read_bytes())},{'pinned_fix_selected':True})
  matrix=[{'authorized':a,'worker_healthy':h,'allowed':auth('after',a,h),'expected':a and h} for a in [False,True] for h in [False,True]]
  good=all(x['allowed']==x['expected'] for x in matrix)
  rec.step('10 Recovery and negative checks','OBSERVED' if good else 'FAILED',{'cases':matrix,'known_workload':sum(i*i for i in range(1000)),'expected':332833500},{'matrix_pass':good,'healthy_authorized_continues':auth('after',True,True),'unauthorized_on_failure_denied':not auth('after',False,False)})
  s=scan('after');rec.step('11 Semgrep after scan',s['state'],s,{'custom_rule_clear':s.get('count')==0,'scanner_executed':s['state']=='OBSERVED'})
  r['phase']='verified' if good and s.get('count')==0 else 'partial';export(r);return r
 finally:lock.rmdir()
def main():
 a=argparse.ArgumentParser();sub=a.add_subparsers(dest='cmd',required=True);x=sub.add_parser('run');x.add_argument('--ai',choices=['local','akash'],default='local');x=sub.add_parser('approve');x.add_argument('--expected-mmr',required=True);x.add_argument('--actor',required=True);x.add_argument('--provenance',required=True);sub.add_parser('verify');o=a.parse_args()
 if o.cmd=='run':r=run(o.ai)
 elif o.cmd=='approve':r=approve(o.expected_mmr,o.actor,o.provenance)
 else:
  r=load(LATEST);v=custody.verify(Path(r['custody']),r['project_root']);v['source_files_match']=custody.verify_artifacts(Path(r['custody']),ROOT);print(json.dumps(v,indent=2));sys.exit(0 if v['PASS'] and v['source_files_match'] else 1)
 print(json.dumps({'id':r['id'],'phase':r['phase'],'project_root':r['project_root'],'mmr_root':r['mmr_root'],'leaves':r['leaf_count']},indent=2))
if __name__=='__main__':main()
