"""Interaction contracts for the extraction studio and the boutique refinements."""
import unittest
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8046/'

class ExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = sync_playwright().start()
        cls.browser = cls.p.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.p.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width':1440,'height':900})
        self.page = self.context.new_page()
        self.page.set_default_timeout(10000)

    def tearDown(self):
        self.context.close()

    def open(self, hash='brew'):
        self.page.goto(BASE+'#'+hash, wait_until='domcontentloaded')
        self.page.evaluate('document.fonts.ready')

    def test_station_loop_and_leave_pause(self):
        self.open()
        self.page.wait_for_function("document.querySelector('#extraction-loop')?.currentTime > .1")
        self.assertTrue(self.page.locator('#extraction').evaluate('(e)=>e.classList.contains("active")'))
        self.page.locator('.rail a[href="#ritual"]').click()
        self.page.wait_for_function("document.querySelector('#extraction-loop').paused && !document.querySelector('#extraction').classList.contains('active')")

    def test_static_poster_hotspots_no_loop_request(self):
        self.page.emulate_media(reduced_motion='reduce')
        requests=[]; self.page.on('request',lambda r:requests.append(r.url))
        self.open()
        self.page.locator('[data-extraction="cup"]').click()
        self.assertIn('crema',self.page.locator('#extraction-detail').inner_text())
        self.assertEqual(self.page.locator('[data-extraction="cup"]').get_attribute('aria-pressed'),'true')
        self.assertFalse(any('/extraction/' in r and '.mp4' in r for r in requests))
        self.assertTrue(self.page.locator('#extraction-loop').evaluate('(e)=>e.paused'))

    def test_mobile_controls_fit_and_static_toggle_stops(self):
        self.page.set_viewport_size({'width':390,'height':844})
        self.open()
        self.page.wait_for_function("document.querySelector('#extraction-loop')?.currentTime > .1")
        self.page.locator('#motion').click()
        self.page.wait_for_function("document.querySelector('#extraction-loop').paused")
        for button in self.page.locator('[data-extraction]').all():
            b=button.bounding_box()
            self.assertGreaterEqual(b['width'],44); self.assertGreaterEqual(b['height'],44)
            self.assertGreaterEqual(b['x'],0); self.assertLessEqual(b['x']+b['width'],390)

    def test_advisor_motion_direction_and_reduced_cancel(self):
        self.open('advisor')
        self.page.locator('#advisor-start').click()
        self.page.locator('#advisor-question input').first.check()
        self.page.locator('#advisor-next').click()
        self.assertEqual(self.page.locator('#advisor-question').get_attribute('data-direction'),'forward')
        self.page.locator('#advisor-back').click()
        self.assertEqual(self.page.locator('#advisor-question').get_attribute('data-direction'),'back')
        self.page.emulate_media(reduced_motion='reduce')
        self.page.wait_for_function("document.querySelector('#advisor-question').getAnimations({subtree:true}).length===0")

    def test_product_intro_interrupt_and_reset(self):
        self.open('product-viewer')
        self.page.wait_for_function("document.querySelector('#spin-surface')?.dataset.intro === 'done'",timeout=20000)
        self.page.locator('#spin-next').click()
        self.page.wait_for_function("document.querySelector('#spin-image').dataset.frame === '1'")
        self.page.locator('#spin-reset').click()
        self.page.wait_for_function("document.querySelector('#spin-image').dataset.frame === '0' && document.querySelector('#spin-surface').getAttribute('aria-busy')!=='true'")

    def test_small_phone_copy_and_controls_do_not_overlap(self):
        self.page.set_viewport_size({'width':320,'height':568})
        self.page.emulate_media(reduced_motion='reduce')
        self.open()
        copy=self.page.locator('.copy.active').bounding_box()
        controls=self.page.locator('#extraction-controls').bounding_box()
        self.assertLessEqual(copy['y']+copy['height']+8,controls['y'])

    def test_product_intro_actually_visits_other_angles_once(self):
        self.page.add_init_script("""window.introFrames=[];new MutationObserver(()=>{
          const s=document.querySelector('#spin-surface'),i=document.querySelector('#spin-image');
          if(s?.dataset.intro==='running'&&i)window.introFrames.push(i.dataset.frame);
        }).observe(document,{subtree:true,attributes:true,attributeFilter:['data-frame']});""")
        self.open('product-viewer')
        self.page.wait_for_function("document.querySelector('#spin-surface')?.dataset.intro==='done'")
        self.assertIn('2',self.page.evaluate('window.introFrames'))

    def test_loop_failure_keeps_poster_and_controls(self):
        self.page.route('**/media/extraction/*.mp4',lambda r:r.abort())
        self.open()
        self.page.wait_for_function("document.querySelector('#extraction-poster').naturalWidth > 0")
        self.page.locator('[data-extraction="group"]').click()
        self.assertIn('Đầu chiết xuất',self.page.locator('#extraction-detail').inner_text())
        self.assertFalse(self.page.locator('#extraction').evaluate('(e)=>e.classList.contains("ready")'))
        self.assertFalse(self.page.locator('#extraction').evaluate('(e)=>e.classList.contains("playing")'))

    def test_loop_pauses_hidden_and_switches_portrait(self):
        self.open()
        self.page.wait_for_function("document.querySelector('#extraction-loop').currentTime>.1")
        self.page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))")
        self.assertTrue(self.page.locator('#extraction-loop').evaluate('(v)=>v.paused'))
        self.page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))")
        self.page.set_viewport_size({'width':390,'height':844})
        self.page.wait_for_function("document.querySelector('#extraction-loop').videoWidth===720 && document.querySelector('#extraction-loop').currentTime>.1")

if __name__=='__main__': unittest.main()
