# Frame custody successor 039R1

Parent: Codex UI038 and recorded walkthrough034b; failed frame039 watermark attempt is preserved.

The walkthrough page and recorder were committed earlier in PR1. This successor adds every source decoded frame as an addressable occurrence in a JSONL pointer ledger. Each occurrence binds source MP4 hash, PTS/time base, YUV420P pixel hash, expected scene, scene-manifest hash and source branch MMR. HYDRALAMP_MMR_V1 commits the occurrence ledger; a separate decomposition independently recomputes the root.

Nine PNG samples retain SHA256 hashes and Apple Vision OCR observations. Eight expected scene markers match; the 48-second frame displays scene5 where the uncalibrated expected timeline predicts scene4. All nine sampled clocks match the expected whole second. This mismatch remains recorded and needs timing calibration or a successor recording. Visual inspection confirmed scene5 and a computation-in-progress display at 48 seconds. Do not claim all-frame semantic alignment PASS.

The watermark is a NEW visible DRM-free pointer overlay referencing source identity and the frame MMR. It is not recovered prior watermark code, authentication, remote attestation or access control. The existing source video, narration and earlier receipts remain unchanged. The first encode failed because drawtext was unavailable; successor039R1 uses an AppKit PNG and FFmpeg overlay.

Review video: media/walkthrough-039r1/demo-039r1-watermarked-review.mp4 (outside git).
Source: media/walkthrough-034b/demo-034-review.mp4 (outside git).
Input recording/assembly hashes are recoverable in media/walkthrough-034b/*.receipt.json and the scene manifest.
No public publication is performed. Media retention beyond these local paths remains unresolved.

Reproduce checks:
.venv/bin/python agent/frame_successor039r1.py verify
Requires original and successor media, FFmpeg and the repository source verifier.

What this supports: exact media identity, decoded-frame integrity, declared scene/source relations and sampled visible proof behavior. The recorder reports both browser roots PASS at completion. This does not independently attest wall-clock computation, prove the sponsor calls happened during recording, establish hardware truth or verify speech alignment.

Current sponsor summary: Semgrep before/after observed; ClickHouse exact readback observed; Akash deployed inference and close receipt observed. Historical AkashML failures remain failed. Hardware/TEE attestation, final deployment-state readback, billing, local bridge delivery and persistent public interaction-generated FCG state remain unverified.

Before a new walkthrough: obtain read-only final closed-state evidence if available, calibrate the scene boundary mismatch, test append-only interaction persistence/readback separately, then record a successor. Reuse narration if factual claims remain unchanged; otherwise revise only the affected passage. Do not rerun paid compute to make the status panel green.
