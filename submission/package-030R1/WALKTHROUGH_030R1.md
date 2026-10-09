# Record a fresh walkthrough (target 2:00–2:30)

Use VOICE_SCRIPT_030R1.txt as narration. Rehearse once and adjust pauses to your own speaking pace. These times are presentation cues, not measured execution latency.

| Time | Screen/action | Narration focus |
|---|---|---|
| 0:00–0:20 | Open https://antigense-cyberhack.vercel.app/ at the hardware diagram. | The client incident and the device-first view. |
| 0:20–0:40 | Start custody replay. Pause at checkpoint 02 or click it. | Software-injected fault; physical failure not observed. |
| 0:40–1:00 | Click 03, then 04, then 10/11. | Unsafe fallback, Semgrep finding, legitimate work preserved. |
| 1:00–1:20 | Scroll to Active custody handoff. Show FCO and prefix. Click Recompute proofs. | Recomputable commitments; integrity versus truth. |
| 1:20–1:40 | Click 12 and Inspect ClickHouse branch. | Same incident, 11 rows, replay count preserved, exact readback, 160.7 ms. |
| 1:40–2:00 | Show the separate GPU receipts in Terminal using the read-only commands below; public Console card is historical until its UI successor is deployed. | Show GPU verification and inference receipt: 3466.4 ms, schema valid, advice not applied; close HTTP 200. |
| 2:00–2:20 | Show footer notices; optionally show localhost OS polling. | Privacy, rights, public replay versus local live polling. |

Recording sequence:
1. Record your narration in Voice Memos or another recorder. Export as voice.m4a.
2. Record a NEW silent screen video following the table. Do not use the older 62-second video for this narration.
3. Do not record TextEdit/.env, terminal credentials, private tabs or judge instructions. Disable microphone capture for the screen video if using separate narration.
4. Put screen.mov and voice.m4a next to assemble_audio_030R1.sh and assemble_audio_030R1.py.
5. Run: sh assemble_audio_030R1.sh --video screen.mov --audio voice.m4a --output demo-030R1.mp4
6. Watch and listen to the entire result. Check that narration and the selected checkpoints agree. The assembly script can pad the final frame by at most 30 seconds; it does not synchronize semantic content for you.
7. Provide the reviewed demo-030R1.mp4 for publication. The script does not deploy or replace public/demo.mp4.

Local presentation: http://127.0.0.1:8790 on magicPRO shows live OS polling and the recorded run. Start custody replay makes no sponsor requests. The local Run bounded scenario button runs the older local fixture route; it is not the complete three-sponsor presentation runner.

The included sponsor-custody-029.jpg shows the earlier Console operation. It is historical and does not show the GPU run.

The screenshot sponsor-results-022.jpg predates the successful Console call and shows its earlier failure; it is retained as historical evidence. It contains public status information and explicit failures. Hardware-020.jpg shows the hardware-first layout from an earlier UI state; its historical Pi checkpoint is not a completed sponsor integration.


GPU recording commands (read-only; do not run the paid deployment again):
```bash
cd /Users/byron/projects/hackathon/antigense-cyberhack
.venv/bin/python agent/akash_gpu024.py verify
python3 - <<'PY'
import json,pathlib
for f in sorted(pathlib.Path('evidence/successor_024').glob('step-*.json')):
    d=json.loads(f.read_text()); o=d.get('observation',{})
    if o.get('name') in ('gpu_inference','gpu_provider_reported_vram','gpu_close_deployment'):
        print(json.dumps(o,indent=2))
PY
```
Record the inference and close summaries, not credentials or the private environment file. Current screenshots remain historical; a fresh combined screenshot has not been captured for this package.
