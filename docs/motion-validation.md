# Motion v2 validation — 2026-10-06

## Approved direction

Stronger scene-led motion after feedback that v1 was too subtle. Presentation is
isolated in `web/motion.js`; navigation, media seeking, resize preservation and
focus remain owned by `web/app.js`. Native CSS/WAAPI only; no new media or libraries.

| Interaction | Actual implementation |
|---|---|
| Opening | Scene opacity .55→1, scale .94→1 and 18px push over 1400ms; once per document |
| Headline | Two line masks preserving original text/emphasis; 105% reveal, 850ms intro / 580ms chapter; reverse direction when scrolling back |
| Camera travel | Copy opacity follows decoded video time; minimum .12 during travel, full opacity at station holds; static mode stays opaque |
| Idle scene | 8s alternate cycle, -3/+4px horizontal, +3/-5px vertical, scale 1→1.012; text layout stays fixed |
| Pause | Idle pauses while scrolling, modal open or document hidden; obsolete finite effects are canceled |
| Rail marker | 480ms movement; position synchronized for navigation, deep links and resize |
| Ambient | Warm wash below reading shade, 9s alternate opacity/transform cycle |
| Scroll hint | 5px, two 950ms cycles after 1500ms; cancels on first progress and never restarts |
| Hover / press | Arrow 3px/180ms; press scale .98/140ms; no layout displacement |
| Dialog entry | 16px/420ms entry; notes 380ms with delays 120/210/300ms |
| Dialog exit | 220ms fade/down/scale; modal stays open and scroll remains locked until completion, then focus returns to CTA |

Static/reduced mode cancels decoration, including idle and delayed effects.
Reduced-motion remains respected if video is explicitly enabled. Hidden-tab
handling cancels finite effects and does not replay the intro on return.

## Executed checks

Working directory: `/home/sss/Projects/moc-coffee-demo`.

- PASS: `/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_motion_v2.py`
  — 6 tests, 10.809s: camera intro, masks/text, idle versus fixed text, scroll pause,
  camera-synced opacity, deep-link/resize marker, delayed modal exit and static cancellation.
- PASS: `/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_motion.py`
  — 6 tests, 12.654s: once-only intro, finite hint, hover geometry, reverse and rapid
  cancellation, reduced/static behavior, modal stagger/focus and visibility lifecycle.
- PASS: `/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_ux.py`
  — 10 tests, 22.700s: landscape controls, history/focus, rotation preservation,
  modal background lock, no-JS reading, responsive poster, timeout/retry and wheel over copy.
- PASS: `/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_web.py`
  — 1440×900, 390×844 and 360×640: forward/reverse and interrupted video seeks,
  no horizontal overflow, modal keyboard behavior, reduced mode without MP4,
  source switching, failed-video fallback, HTTP 206; no page JS errors.
- PASS: `node --check web/app.js`, `node --check web/motion.js`.
- PASS: `python3 -m compileall -q scripts`.

V2 cases were run red before implementation. Deep-link marker regression was
also reproduced red and fixed by synchronizing marker geometry during updates.
Prior tests were updated to the approved line-mask/stagger timings and now wait
for the intentional 220ms modal exit before checking native close/focus.

## Live browser evidence

Opened a fresh tab at `http://127.0.0.1:8046/?v=motion-2#origin`, leaving old tabs
untouched. The Chrome window was minimized; after restoring it, animation startup
was initially pending, then began advancing. Two live samples 1200ms apart showed
idle animation time 11228→12432ms and different computed transform matrices;
finite intro animations had completed. Playback rate was 1 and reduced-motion off.
This confirms that motion executes in the user's live browser, not just headless tests.

## Evidence limits

Behavioral checks: **PASS**. Live animation execution: **confirmed**. These are
not a professional visual or temporal aesthetic approval. Real Safari/iPhone,
native touch, screen-reader output and measured rendering FPS remain untested.
Screenshots refreshed by browser tests are static evidence only. Overall
cross-device and visual verification remains **partial**.
