"""Capture the studio composition and check readable controls across viewports."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(reduced_motion='reduce')
    results = []
    for width, height in [(1440,900),(768,1024),(390,844),(360,640),(320,568),(844,390),(667,375)]:
        page.set_viewport_size({'width':width,'height':height})
        page.goto('http://127.0.0.1:8046/#brew')
        page.evaluate('document.fonts.ready')
        row = page.evaluate('''() => {
          const a=document.querySelector('.copy.active').getBoundingClientRect();
          const b=document.querySelector('#extraction-controls').getBoundingClientRect();
          const footer=document.querySelector('.footer').getBoundingClientRect();
          return {copy:[a.x,a.y,a.width,a.height],controls:[b.x,b.y,b.width,b.height],
            overlap:a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top,
            footerOverlap:b.bottom>footer.top,
            overflow:document.documentElement.scrollWidth>innerWidth};
        }''')
        row['viewport']=[width,height]
        results.append(row)
        assert not row['overlap'] and not row['footerOverlap'] and not row['overflow'], row
        if width in (1440,390):
            page.screenshot(path=str(ROOT/f'renders/browser/extraction-{width}.png'))
    browser.close()
    (ROOT/'renders/browser/extraction-layout.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))
