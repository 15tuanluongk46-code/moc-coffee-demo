"""Original scenes stay inside the presentation frame at all motion phases."""
import unittest
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8046/'

class SceneFrame(unittest.TestCase):
    def test_original_media_and_safe_edges(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for w,h in [(1440,900),(2494,1100),(768,1024),(390,844),(320,568),(844,390)]:
                page = browser.new_page(viewport={'width':w,'height':h})
                requests=[]
                page.on('request',lambda r:requests.append(r.url))
                page.goto(BASE,wait_until='domcontentloaded')
                page.wait_for_function('document.querySelector(".stage").classList.contains("video-ready")')
                self.assertEqual(page.locator('#extraction').count(),0)
                for i in range(4):
                    page.evaluate('(i)=>scrollTo(0,i/3*(document.querySelector("#journey").offsetHeight-innerHeight))',i)
                    page.wait_for_function('(i)=>Math.abs(document.querySelector("#film").currentTime-i/3*287/24)<.08&&!document.querySelector("#film").seeking',arg=i)
                    for phase in [0,8000]:
                        box=page.locator('.scene-drift').evaluate('''(el,t)=>{for(const a of el.getAnimations()){a.pause();a.currentTime=t;}const r=el.getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom};}''',phase)
                        self.assertGreaterEqual(box['x'],8)
                        self.assertGreaterEqual(box['y'],8)
                        self.assertLessEqual(box['right'],w-8)
                        self.assertLessEqual(box['bottom'],h-8)
                self.assertFalse(any('/extraction/' in url for url in requests))
                self.assertTrue(any('/journey-v2/journey-' in url for url in requests))
                self.assertFalse(any('/media/journey-desktop.mp4' in url or '/media/journey-mobile.mp4' in url for url in requests))
                page.close()
            browser.close()

if __name__=='__main__':unittest.main(verbosity=2)
