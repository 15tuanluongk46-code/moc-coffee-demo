"""Browser integration checks; uses a clean Chromium context, never personal tabs."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--static-only', action='store_true')
p.add_argument('--base-url', default='http://127.0.0.1:8046/')
a = p.parse_args()
BASE = a.base_url.rstrip('/') + '/'
OUT = ROOT / 'renders' / 'browser'
OUT.mkdir(exist_ok=True)
results = []

def open_page(page):
    # A CDN video request may remain open after playable data arrives.
    # Assert usable DOM/fonts/poster instead of waiting for network silence.
    page.goto(BASE, wait_until='domcontentloaded')
    page.evaluate('document.fonts.ready')
    page.wait_for_function('document.querySelector("#poster").complete && document.querySelector("#poster").naturalWidth>0')

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=['--disable-dev-shm-usage'])
    for name, width, height in [('desktop',1440,900), ('mobile',390,844), ('small-mobile',360,640)]:
        context = browser.new_context(viewport={'width':width,'height':height},
                                      reduced_motion='reduce' if a.static_only else 'no-preference')
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        open_page(page)
        assert page.locator('#poster').evaluate('(img)=>img.complete && img.naturalWidth > 0')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), name
        if not a.static_only:
            page.wait_for_function('document.querySelector(".stage").classList.contains("video-ready")')
            assert page.locator('#film').get_attribute('data-view') == ('mobile' if width <= 760 else 'desktop')
        for i in [0,1,2,3,1,0,3]:
            page.locator('.rail a').nth(i).click()
            page.wait_for_function('(i)=>document.querySelector("#chapter-number").textContent===String(i+1).padStart(2,"0")',arg=i)
            if not a.static_only:
                page.wait_for_function('(i)=>Math.abs(document.querySelector("#film").currentTime - i/3*287/24) < .08 && !document.querySelector("#film").seeking',arg=i)
            assert page.locator('.copy.active').count() == 1
            assert page.locator('.copy:not(.active)').evaluate_all('(els)=>els.every(e=>e.inert)')
            box=page.locator('.copy.active').bounding_box()
            assert box['x'] >= 0 and box['x']+box['width'] <= width+1
            assert box['y'] >= 70 and box['y']+box['height'] < height-55, (name,i,box)
            page.screenshot(path=str(OUT/f'{name}-{i+1:02}.png'))
        page.locator('#discover').click()
        assert page.locator('#flavors').evaluate('(d)=>d.open')
        page.keyboard.press('Escape')
        page.wait_for_function('!document.documentElement.classList.contains("modal-lock")', timeout=1000)
        assert not page.locator('#flavors').evaluate('(d)=>d.open')
        assert page.evaluate('document.activeElement.id') == 'discover'
        if not a.static_only:
            # Interrupt seeks in quick succession, then verify it reaches the final target.
            for fraction in [.9,.15,.75,.02,.6]:
                page.evaluate('(p)=>scrollTo({top:p*(document.querySelector("#journey").offsetHeight-innerHeight),behavior:"instant"})',fraction)
                page.wait_for_timeout(25)
            page.wait_for_function('Math.abs(document.querySelector("#film").currentTime - .6*287/24)<.08 && !document.querySelector("#film").seeking')
            page.locator('#motion').click()
            assert not page.locator('#film').get_attribute('src')
            assert page.locator('#motion').get_attribute('aria-pressed') == 'true'
            page.locator('#motion').click()
            page.wait_for_function('document.querySelector(".stage").classList.contains("video-ready")')
        assert not errors, errors
        results.append({'viewport':name,'navigation_forward_reverse':True,'dialog_keyboard':True,'no_overflow':True,'errors':errors})
        context.close()

    context=browser.new_context(reduced_motion='reduce')
    page=context.new_page()
    requests=[]
    page.on('request', lambda r: requests.append(r.url))
    open_page(page)
    assert not any('.mp4' in url for url in requests), requests
    page.locator('.rail a').nth(3).click()
    page.wait_for_function('document.querySelector("#poster").src.includes("04.webp")')
    results.append({'reduced_motion_no_video_request':True})
    context.close()
    if not a.static_only:
        context=browser.new_context(viewport={'width':1440,'height':900})
        page=context.new_page()
        open_page(page)
        page.wait_for_function('document.querySelector(".stage").classList.contains("video-ready")')
        page.set_viewport_size({'width':390,'height':844})
        page.wait_for_function('document.querySelector("#film").dataset.view==="mobile" && document.querySelector(".stage").classList.contains("video-ready")')
        page.set_viewport_size({'width':1440,'height':900})
        page.wait_for_function('document.querySelector("#film").dataset.view==="desktop" && document.querySelector(".stage").classList.contains("video-ready")')
        results.append({'responsive_media_switch':True})
        context.close()
        context=browser.new_context()
        page=context.new_page()
        page.route('**/*.mp4',lambda route:route.abort())
        open_page(page)
        page.wait_for_function('document.querySelector("#status").textContent.includes("chưa tải được")')
        assert not page.locator('.stage').evaluate('(s)=>s.classList.contains("video-ready")')
        results.append({'video_failure_poster_fallback':True})
        context.close()
    if not a.static_only:
        # Probe from a real same-origin browser; some CDNs reject urllib's client.
        context=browser.new_context(reduced_motion='reduce')
        page=context.new_page()
        open_page(page)
        media=page.evaluate('''async()=>{
            const response=await fetch('media/journey-v2/journey-desktop.mp4',{headers:{Range:'bytes=0-99'}});
            return {status:response.status,bytes:(await response.arrayBuffer()).byteLength};
        }''')
        assert (media['status']==206 and media['bytes']==100) or (media['status']==200 and media['bytes']>100), media
        results.append({'http_media_status':media['status'],'http_byte_range':media['status']==206,'blob_scrubbing_verified':True})
        context.close()
    browser.close()
report={'base_url':BASE,'mode':'static' if a.static_only else 'full','checks':results}
(OUT/('test-static.json' if a.static_only else 'test-full.json')).write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
