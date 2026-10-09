# Antigense Daisy — 051 new local judge + historical sponsor video

**State:** SCRIPT_PREPARED; VIDEO_NOT_RECORDED; NEW_VIDEO_URL_UNKNOWN.
**Suggested runtime:** 3m15s–3m45s, actual chapter times to be measured after edit.
**Audience:** Tokens& Cyberhack judges.
**Canonical entry:** https://tokensand.com/p/antigense-daisy
**Recording host:** magicPRObox; loopback judge UI is private to the host.
**Never include a session capability, .env, token, email, PHI, private security notes, or Mac terminal history in frame.** If a capability ever appears, rotate the session again before release.

## Pre-recording preparation

1. Open https://antigense-cyberhack.vercel.app/judges/ and https://antigense-cyberhack.vercel.app/judges-043.html in browser tabs. These are earlier public, hosted historical proofs.
2. On magicPRObox open http://127.0.0.1:8850/. The recording session is at `.runtime/judge050-video-r1`, created after the exposed old capability was retired. Use a masked field for the fresh secret, with the terminal and clipboard kept OFF CAMERA; do not type it on screen while recording.
3. Verify the local judge page shows a passing 2-leaf starting checkpoint. Keep a separate window with the landing page ready to show.
4. Use a test phrase like `DEMO: review based on frozen authorization oracle`. This is synthetic, not patient data and not a claim of cryptographically authenticated reviewer identity.
5. On macOS, use Shift-Command-5 > Record Selected Portion, select microphone, avoid desktop notifications and secrets. Or QuickTime Player > File > New Screen Recording. Record at readable zoom.
6. Keep the initial recorded video at https://youtu.be/hpLH88V6PF0 as the submission fallback until the new upload is completed and independently checked.

## Spoken narration: approximately 3m30s

### Scene A — 00:00–00:25 | Public landing page

**ON SCREEN:** https://antigense-cyberhack.vercel.app/ then /judges/

**SAY:**
"Antigense Daisy is an evidence-driven agentic cyberdefense prototype. A corrupted AI-worker result should never turn a failed integrity check into unauthorized access. We preserve the source, the detected flaw, the review decision, and the recovery evidence so another person can independently inspect what happened."

### Scene B — 00:25–00:53 | Semgrep and deterministic repair

**ON SCREEN:** Existing /judges/ sponsor evidence section, or the historical walkthrough showing the Semgrep fixture and the before/after policy.

**SAY:**
"We reproduce a controlled fail-open authorization bug—not damaged physical hardware. Semgrep Community Edition finds one pinned rule violation before the repair and zero afterward. A four-case authorization oracle checks that unauthorized work is denied while legitimate work continues. We also scanned our own code and addressed a risky execution helper. A clean rule scan is not a proof that all vulnerabilities are gone."

### Scene C — 00:53–01:17 | Akash historical GPU execution

**ON SCREEN:** Existing hosted /judges/ Akash historical receipt or /walkthrough-035.html Akash chapter. Do NOT present this as a new GPU run.

**SAY:**
"An Akash GPU deployment ran a bounded Qwen2.5 half-billion-parameter model. The recorded inference returned HTTP 200 in about 3.47 seconds, and the deployment close request succeeded. Model output remained untrusted advice: it could not authorize a patch or a payment. We also retain an earlier HTTP 401 failure. GPU hardware attestation was not verified."

### Scene D — 01:17–01:40 | ClickHouse historical Cloud readback

**ON SCREEN:** Existing /judges/ ClickHouse receipts or historical public interactive replay, with the exact-rows result.

**SAY:**
"ClickHouse Cloud provides a queryable projection of the custody records. We previously ingested, replayed and read back 55 distinct historical occurrence rows with exact reconciliation. Those are separately recorded Cloud operations. The new local judge interaction I am about to show has not yet been written into ClickHouse."

### Scene E — 01:40–01:58 | Recompute existing browser proof

**ON SCREEN:** https://antigense-cyberhack.vercel.app/judges-043.html; use its actual recompute control.

**SAY:**
"Every custody event is a Fractal Custody Object linked through a typed Fractal Custody Graph relationship. An ordered Merkle Mountain Range commits the recorded transitions. This browser recomputes a separate historical twelve-leaf local review proof. Hashes attest to these bytes, not to truth or human identity."

### Scene F — 01:58–02:48 | NEW live local judge — actual actions

**ON SCREEN:** http://127.0.0.1:8850/; zoom to show 2-leaf starting root and two panels. The fresh private capability must already be entered into the MASKED field BEFORE recording begins.

**SAY, FIRST ACTION (DENY):**
"Now we are on the actual local review server, not prerecorded playback. The public panel begins with a live MMR commitment. I select DENY and record a synthetic review note. The server checks my local capability, the browser origin, the exact previous root, and the authorization oracle before appending a new FCO."

**ACTION:** Choose DENY, use `DEMO: deny untrusted security action`, click Record judge action. Wait for public root/leaf count to advance to 3. Do not show private note panel if it would contain sensitive text.

**SAY, SECOND ACTION (ALLOW):**
"The public spectator receives a new SSE checkpoint without seeing my note or credential. I can then record a second, independent ALLOW decision, again bound to the current root. The commitment advances to the next leaf. A stale replay is rejected, rather than silently rewriting the graph."

**ACTION:** Choose ALLOW, use `DEMO: synthetic tested review approval`, click Record judge action. Show leaf count advancing to 4 and new MMR root.

### Scene G — 02:48–03:10 | Tests and negative controls

**ON SCREEN:** Nonsecret terminal tab (do not show the capability); run:
```sh
cd /Users/byron/projects/hackathon/antigense-live-judge-050
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q
curl -fsS http://127.0.0.1:8850/api/public | python3 -c 'import json,sys; j=json.load(sys.stdin);print("verified",j["chain_pass"],"leaves",j["mmr"]["leaf_count"],"root",j["mmr"]["root"])'
```
**SAY:**
"This local suite passes seventeen tests. It checks live server updates, independent MMR recomputation, private-note integrity, and negative controls for unauthorized requests, cross-origin actions and stale review roots. No cloud credits or customer funds are spent by this judge demonstration."

### Scene H — 03:10–03:32 | Limitations and closing

**ON SCREEN:** Public /judges/ guide and project gallery link.

**SAY:**
"Antigense demonstrates real historical Semgrep, Akash and ClickHouse integrations and a newly executed local real-time review mechanism. They are not yet one continuously running production deployment. The human review is not digitally signed, Pi and hardware attestation remain untested, and financial ROI has not been computed. Our goal is a system that preserves failures and unknowns as carefully as successes—so judges can verify what actually happened."

## Safe recording verification

After editing or recording, check your actual MP4:

```bash
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_type,codec_name,width,height -of json "/path/to/your-recording.mp4"
```

Listen to the narration and manually inspect frames around the private-control segment to ensure NO capability or private notes were exposed. Do not auto-upload raw recorded desktop footage. If your new video exceeds three minutes slightly, keep clarity rather than aggressively cutting proof transitions.

## New upload metadata (paste when actually uploaded)

**Video title:**

Antigense Daisy 051 | Live Judge FCO/FCG Review — Semgrep, Akash & ClickHouse

**Short description:**

New local real-time security-review demonstration, with older separately recorded sponsor receipts. Watch an operator append synthetic DENY and ALLOW reviews; the public SSE feed displays advancing FCO/FCG and Merkle/MMR checkpoints while private notes remain local. Local tests: 17/17 PASS. Semgrep CE found and resolved the pinned fail-open teaching-fixture pattern; Akash GPU inference and ClickHouse Cloud replay are historical evidence, not new API calls during this recording. Hardware/GPU attestation, real payments, digitally signed reviewer identity, Pi execution and ROI are NOT_TESTED/NOT_COMPUTED. Public judge guide: https://antigense-cyberhack.vercel.app/judges/ . Existing project: https://tokensand.com/p/antigense-daisy . New local judge source commit b9b0cfa3626ced8dfcf1971039eedb8dbec30574 was not publicly pushed as of script creation.

**Suggested chapter labels — replace provisional times with actual timestamps:**

00:00 — Threat and application
00:25 — Semgrep finding and regression oracle
00:53 — Historical Akash GPU inference
01:17 — Historical ClickHouse exact readback
01:40 — Browser MMR recomputation
01:58 — New local live public/private judge action
02:48 — Local tests and fail-closed controls
03:10 — Evidence limits and closing

## Release gate

- Actual recording completed, edited and reviewed: NOT_YET.
- Credentials absent from every frame/audio/transcript: NOT_YET_TESTED.
- New uploaded public/unlisted video URL: UNKNOWN.
- Existing official Tokens& project saved with replacement: NOT_DONE.
- New local 050 branch pushed/merged: NO.
- Existing canonical project and published hosted site: unchanged.
