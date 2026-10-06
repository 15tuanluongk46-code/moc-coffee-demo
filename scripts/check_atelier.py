"""Capture the product redesign at reading sizes and validate real image loads."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'renders/browser'

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    results = []
    for label, width, height in [('wide',2494,1100),('desktop',1440,1000),('tablet',768,1024),('mobile',390,844),('small',320,568)]:
        context = browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
        page = context.new_page()
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        for anchor in ['collection','product-viewer','advisor','brew-guide']:
            page.goto('http://127.0.0.1:8046/?v=atelier-2#'+anchor,wait_until='networkidle')
            page.evaluate('document.fonts.ready')
            page.wait_for_timeout(100)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(label,anchor,'horizontal overflow')
            if anchor=='collection':
                hero=page.locator('.product-hero img')
                assert hero.evaluate('(e)=>e.complete&&e.naturalWidth>0'),(label,'missing hero')
                bounds=page.locator('.product-story').bounding_box()
                assert bounds['width']<=1461,(label,'unbounded hero')
            if anchor=='product-viewer':
                assert page.locator('#spin-image').evaluate('(e)=>e.complete&&e.naturalWidth>0'),(label,'missing turntable')
            if label in {'desktop','mobile'}:
                page.screenshot(path=str(OUT/f'atelier-{label}-{anchor}.png'))
            results.append({'viewport':label,'anchor':anchor,'overflow':False})
        assert not errors,errors
        context.close()
    browser.close()
    (OUT/'atelier-layout.json').write_text(json.dumps(results,indent=2))
    print(json.dumps({'checks':len(results),'result':'PASS'},indent=2))
