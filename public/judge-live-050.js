'use strict';
const $ = id => document.getElementById(id);
let observedRoot = '';
function render(s) {
  observedRoot = s.mmr.root;
  $('root').textContent = observedRoot;
  $('leaves').textContent = String(s.mmr.leaf_count);
  $('valid').textContent = s.chain_pass ? 'PASS (custody only)' : 'FAILED';
  $('valid').className = s.chain_pass ? 'pass' : 'bad';
  const wrap = $('events');
  wrap.replaceChildren();
  for (const e of (s.events || [])) {
    const item = document.createElement('section');
    item.className = 'event';
    const lines = [
      'Leaf ' + e.index + ' · ' + e.kind + ' · ' + e.decision,
      'FCO: ' + e.occurrence_fco_id,
      'Parent: ' + (e.predecessor || '(genesis)'),
      'MMR: ' + e.mmr_root,
    ];
    for (const line of lines) {
      const lineItem = document.createElement('div');
      lineItem.className = 'hash';
      lineItem.textContent = line;
      item.appendChild(lineItem);
    }
    wrap.appendChild(item);
  }
}
async function refresh() {
  const r = await fetch('/api/public', {cache:'no-store'});
  if (r.ok) render(await r.json());
}
async function privateRead() {
  const token = $('token').value;
  const r = await fetch('/api/private', {cache:'no-store',headers: {'Authorization':'Bearer ' + token}});
  const j = await r.json();
  if (!r.ok) throw Error('private read rejected: ' + j.error);
  $('notes').textContent = JSON.stringify(j.private_notes, null, 2);
}
$('private').addEventListener('click', async () => {
  try { await privateRead(); $('response').textContent='Private readback authorized locally.'; }
  catch (e) {$('response').textContent=e.message;}
});
$('review').addEventListener('click', async () => {
  const root = observedRoot;
  if (!root) return;
  const headers = {'Content-Type':'application/json','Authorization':'Bearer '+$('token').value};
  try {
    const r = await fetch('/api/review', {method:'POST', headers,
      body:JSON.stringify({decision:$('decision').value,expected_root:root,note:$('note').value})});
    const j = await r.json();
    if (!r.ok) throw Error('Action rejected ('+r.status+'): '+j.error);
    $('response').textContent='Review appended at leaf '+j.receipt.index+'; signed=false; no patch applied';
    await refresh();
    await privateRead();
  } catch (e) {
    $('response').textContent=e.message;
    if (e.message.includes('stale_mmr_root')) await refresh();
  }
});
const source = new EventSource('/api/stream');
source.addEventListener('checkpoint', e => {
  render(JSON.parse(e.data));
  $('stream').textContent='Public live stream connected';
  $('stream').className='pass';
});
source.onerror = () => {
  $('stream').textContent='Reconnecting public stream…';
  $('stream').className='dim';
};
refresh().catch(e => { $('stream').textContent=e.message; });
