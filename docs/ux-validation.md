# UX fixes — 2026-10-06

Scope: complete the approved user-flow audit fixes for the existing MỘC Coffee demo.

## Changes and evidence

| Audit finding | Implementation | Verification |
| --- | --- | --- |
| Landscape header/footer intercept chapter links and CTA | Separate short-landscape layout; bounded, scrollable copy; footer does not intercept pointer events | Real clicks at 844×390 and 667×375, including opening the final dialog |
| Rotation changes chapter unexpectedly | Preserve normalized progress before reading the resized scroll position | Portrait → landscape → portrait → tablet, plus normal-motion media switching |
| Dialog allows background scroll and loses return focus | Lock document scrolling, preserve progress, restore CTA focus on close | Wheel behind dialog + Escape in static and video modes |
| Small type, weak text colors and small chapter controls | Larger body/metadata type; darker muted/accent colors; 44px chapter, motion and close targets | DOM measurements; navigation/control tests |
| Back leaves the page instead of returning to prior selected chapter | Push explicit chapter selections; replace passive scroll location; handle popstate | Back/Forward between chapters and focus on destination heading |
| Mobile hides loading/error information | Visible status, dynamic motion button label, 12-second timeout with poster and retry | Held video request until timeout, successful retry, forced-error fallback |
| Unnecessary desktop poster request on phones | Responsive picture source selected by aspect ratio | Network assertion: no desktop first-poster request at 390×844 |
| No-JavaScript page shows only first chapter | Readable four-section document as the default; enhanced layout only with JS | All four headings visible without JavaScript; no inert sections |
| End of journey still says to keep scrolling | Final-station hint and compact footer text | Final chapter feedback assertion |
| Wheel over copy can stop the journey | Allow scroll chaining from the copy container; retain confinement inside the dialog | Reproduced timeout before fix; wheel-over-description test now advances page/chapter |

## Commands executed

- PASS: `/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_ux.py` — **10 tests passed**, 21.360 seconds in the final run.
- PASS: `/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_web.py` — full video integration, three viewports, actual forward/reverse seeks, interrupted seeks, dialog, reduced-motion, responsive media switch, failed-video fallback, HTTP 206. No page errors in the three viewport runs.
- PASS: `node --check web/app.js`.
- PASS: `python3 -m compileall -q scripts`.

The original audit regression cases were exercised before production changes and failed on the reported symptoms. The timeout/retry and normal-motion cases add coverage; they are not claimed as pre-fix reproductions.

Additional DOM inspection covered all four chapters at 1440×900, 1024×768, 768×1024, 761×700, 760×700, 390×844, 360×640, 844×390, 667×375 and 320×568. Copy bounds stayed between the fixed header/footer, with no horizontal page overflow. Short windows may scroll text within the copy panel before continuing the journey.

## Remaining verification limits

- Automated tests use Chromium, including simulated mobile dimensions. Physical touch devices and iOS Safari have not been tested.
- One resized mobile screenshot was inspected through local vision: no reported headline/farm overlap or footer clipping in that sample. This does not establish a comprehensive visual/accessibility pass.
- No fresh every-frame aesthetic review or screen-reader session was performed. Existing Blender renders and videos were not modified in this UX pass.
- The CTA remains the agreed demo flavor dialog, not a checkout flow.

Verdict: approved functional UX fixes pass the automated checks; cross-browser, real-device and comprehensive visual/accessibility validation remain partial.
