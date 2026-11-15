---
name: app-flow-demo
description: Create deterministic, studio-grade end-to-end app flow demo videos and technical explainers across any repository. Captures live UI/UX via Playwright with 2x Retina resolution and visible cursor, synthesizes humanized ElevenLabs narration, burns clean subtitles, speed-ramps wait states, and renders verified MP4 masters via decoded filter-complex concatenation.
---

# App Flow Demo & Explainer Pipeline

Produces reproducible, high-polish application walkthroughs and code-driven explainers for any project without manual video editing, audio desync, or bitstream glitches.

## When to Use

- User asks for an "app flow demo", "live walkthrough", "product video", "show how it works e2e", or "explainer video".
- User wants to record real application interaction (inputs, loading states, live outputs) with voiceover and subtitles.
- Target is any web application (React, Vite, Next.js, FastAPI, Go, etc.) in the workspace.

---

## The 6-Phase Production Protocol

```
[Phase 1: Discover Flow] ──> [Phase 2: Rehearse & Record E2E] ──> [Phase 3: Explainer Intro (Optional)]
                                        │
[Phase 6: Verify & Deliver] <── [Phase 5: Assemble & Subtitle] <── [Phase 4: Synthesize Narration]
```

### Phase 1: Flow Discovery

Before writing recording scripts, inspect the target project to determine exact ports, seed data, and DOM locators:
1. Identify backend/frontend startup commands (`pnpm dev`, `uv run uvicorn`, `docker compose up`).
2. Discover existing test fixtures or seed states (e.g. frozen database records, mock models, pre-ingested files) so the demo starts in a clean, predictable state.
3. Map the exact interactive flow:
   - Initial scene establishment (book, document, or dashboard view).
   - Core interactive actions (buttons clicked, dropdowns selected, queries typed).
   - Expected loading states and dynamic result cards.

### Phase 2: Live UI Recording with Telemetry

Record using Playwright with strict visual density and wall-clock telemetry logging:

1. **Retina Density**: Set `viewport: { width: 1920, height: 1080 }` and `deviceScaleFactor: 2` for razor-sharp text and controls.
2. **Cursor & Ripple Injection**: Inject `~/.local/share/flow-demo/cursor-overlay.js` after navigation. Use cubic Bezier interpolation (`generateTrajectory`) for smooth, humanized mouse moves.
3. **Telemetry Logging (`action_log.json`)**:
   Log timestamps for every milestone instead of relying on manual timing guesses:
   ```typescript
   logEvent("playback_started");
   logEvent("drawer_opened");
   logEvent("query_submitted");
   logEvent("answer_rendered");
   ```
4. **Outro Hold**: Maintain a comfortable 2.5-second camera hold on the final result card before closing the context.

### Phase 3: Technical Architecture Explainer (fframes)

If an explainer is requested before cutting to the live app:
1. Scaffold an `fframes` project (Rust + Skia GPU + SVG) in `demo/<app>-explainer/`.
2. Model 2 to 3 conceptual scenes:
   - The problem / naive baseline (e.g. unfiltered global retrieval, race condition, data leak).
   - The architectural solution (e.g. mathematical horizon clamp, state machine boundary).
   - The open-weights or infrastructure stack (e.g. SQLite FTS5, Qwen, Kokoro, Redis).
3. Render at `1920x1080 @ 30fps`.

### Phase 4: Technical Narration (ElevenLabs)

Synthesize voiceover narration using the standardized configuration or the automated CLI:
- Run `flow-demo tts` to synthesize all beats declared in `storyboard.yaml` into `narration/<id>.mp3`.
- **Voice**: `River` (`voice_id: SAz9YHcvj6GT2YYXdXww`) — relaxed, neutral, informative.
- **Model**: `eleven_turbo_v2_5`, `stability: 0.35`, `output_format: mp3_44100_128`.
- **Tone Rules**:
  - Zero corporate marketing buzzwords: never say "studio grade", "game changer", "cutting edge", or "revolutionary".
  - Direct, engineer-to-engineer delivery: describe mechanisms, data flows, and guarantees.
  - Split beats around UI actions: describe queries as they are typed, and explain conclusions as they appear on screen.

### Phase 5: Pacing, Subtitles & Audio Mixdown

1. **Dynamic Speed Ramping**:
   - Locate slow CPU inference or long API wait states in `action_log.json`.
   - Speed-ramp loading skeletons or spinners (e.g. 10x-12x) down to ~2.5 seconds using ffmpeg `setpts=(PTS-STARTPTS)/speed`.
2. **Audio Mixdown Contract**:
   - Mix voice tracks using `adelay` mapped directly to telemetry events in `action_log.json`.
   - **Never mix overlapping background audio** (e.g. audiobook audio or video audio) simultaneously with voiceover—it sounds like muffled demonic murmuring.
   - Force strict stereo resampling and broadcast loudness: `aformat=sample_rates=44100:channel_layouts=stereo,loudnorm=I=-16:LRA=11:TP=-1.5`.
3. **Subtitle Styling**:
   - Format: 14pt `DejaVu Sans`, pure white, subtle semi-transparent black 1px outline + drop shadow, `MarginV=55` (floating above docks/navbars).
   - No opaque background boxes (`BorderStyle=1`).

### Phase 6: Decoded Concatenation & Automated Assembly

1. **Turnkey CLI Assembly**:
   Run the all-in-one orchestrator:
   ```bash
   flow-demo assemble [--dir demo/] [-o master.mp4]
   ```
   Or alias: `flow-demo build`. This automatically applies trimming, speed-ramps, audio mixdown with `loudnorm`, subtitles burn-in, and decoded `filter_complex concat`.

2. **Decoded Filter-Complex Concat**:
   **NEVER** use the `-f concat` demuxer on container files (MP4/WebM). Differing sample rates (e.g. 44.1kHz vs 96kHz) will pass un-resampled packets to the decoder, slowing speech to 0.46x and pitching voice into a demonic growl.
   Always decode to raw PCM first:
   ```bash
   ffmpeg -y -i scene1.mp4 -i scene2.mp4 \
     -filter_complex "[0:v]fps=30,scale=1920:1080,setsar=1[v0];[1:v]fps=30,scale=1920:1080,setsar=1[v1];[0:a]aformat=sample_rates=44100:channel_layouts=stereo[a0];[1:a]aformat=sample_rates=44100:channel_layouts=stereo[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" \
     -map "[v]" -map "[a]" \
     -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p \
     -c:a aac -b:a 192k -ar 44100 master.mp4
   ```

3. **Automated Verification**:
   Always run before declaring complete:
   ```bash
   flow-demo verify <output_master.mp4>
   ```
   Verify:
   - Bitstream error count == 0.
   - Framerate is constant 30 fps.
   - Sample rate is strictly 44,100 Hz stereo.
   - Audio and video durations match within 3.5 seconds.
