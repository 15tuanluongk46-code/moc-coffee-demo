"""User-input scrolling must finish on readable stations, without trapping controls."""
import unittest
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8046/'


class ScrollStops(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width':1440,'height':900}, reduced_motion='reduce')
        self.page = self.context.new_page()
        self.page.set_default_timeout(5000)

    def tearDown(self):
        self.context.close()

    def open(self, hash=''):
        self.page.goto(BASE+hash, wait_until='networkidle')
        self.page.evaluate('document.fonts.ready')

    def fraction(self):
        return self.page.evaluate('scrollY/(document.querySelector("#journey").offsetHeight-innerHeight)')

    def test_wheel_burst_advances_exactly_one_scene_and_reverses(self):
        self.open()
        self.page.mouse.move(1200,500)
        for delta in [100,65,30,12,4]:
            self.page.mouse.wheel(0,delta); self.page.wait_for_timeout(40)
        self.page.wait_for_timeout(400)
        self.assertAlmostEqual(self.fraction(),1/3,delta=.002)
        self.assertEqual(self.page.locator('#chapter-number').inner_text(),'02')
        self.page.mouse.wheel(0,-100); self.page.wait_for_timeout(400)
        self.assertAlmostEqual(self.fraction(),0,delta=.002)

    def test_desktop_product_and_viewer_fit_below_header(self):
        for hash, selector in [('#collection','.product-story'),('#product-viewer','.product-viewer')]:
            self.open(hash)
            bounds=self.page.locator(selector).bounding_box()
            header=self.page.locator('.header').bounding_box()['height']
            self.assertGreaterEqual(bounds['y'],header-2)
            self.assertLessEqual(bounds['y']+bounds['height'],902)

    def test_journey_exit_and_reverse_have_no_halfway_handoff(self):
        self.open('#ritual'); self.page.mouse.move(1200,500)
        self.page.mouse.wheel(0,100); self.page.wait_for_timeout(400)
        box=self.page.locator('.product-story').bounding_box()
        self.assertAlmostEqual(box['y'],self.page.locator('.header').bounding_box()['height'],delta=3)
        self.page.mouse.wheel(0,-100); self.page.wait_for_timeout(400)
        self.assertAlmostEqual(self.fraction(),1,delta=.002)

    def test_mobile_long_sections_do_not_skip_content(self):
        self.page.set_viewport_size({'width':390,'height':844})
        self.open('#collection'); self.page.mouse.move(380,400)
        previous=self.page.evaluate('scrollY')
        for _ in range(5):
            self.page.mouse.wheel(0,110); self.page.wait_for_timeout(400)
            current=self.page.evaluate('scrollY')
            self.assertGreater(current,previous+2)
            self.assertLessEqual(current-previous,744+3)
            previous=current

    def test_popup_and_zoom_wheel_are_not_intercepted(self):
        self.open('#ritual'); self.page.locator('#discover').click()
        before=self.page.evaluate('scrollY')
        self.page.mouse.move(10,200); self.page.mouse.wheel(0,150)
        self.page.wait_for_timeout(400)
        self.assertEqual(self.page.evaluate('scrollY'),before)
        self.page.keyboard.press('Escape')
        canceled=self.page.evaluate('!window.dispatchEvent(new WheelEvent("wheel",{deltaY:100,ctrlKey:true,cancelable:true}))')
        self.assertFalse(canceled)

    def test_desktop_wheel_from_product_lands_on_complete_viewer(self):
        self.open('#collection'); self.page.mouse.move(1400,500)
        self.page.mouse.wheel(0,100); self.page.wait_for_timeout(400)
        box=self.page.locator('.product-viewer').bounding_box()
        self.assertAlmostEqual(box['y'],108,delta=3)

    def test_motion_burst_and_midflight_reverse_end_on_clear_scene(self):
        self.page.emulate_media(reduced_motion='no-preference'); self.open()
        self.page.mouse.move(1200,500)
        for delta in [100,60,20,3]:
            self.page.mouse.wheel(0,delta); self.page.wait_for_timeout(40)
        self.page.wait_for_function('Math.abs(scrollY/(document.querySelector("#journey").offsetHeight-innerHeight)-1/3)<.002')
        self.page.wait_for_timeout(250)
        self.page.mouse.wheel(0,100); self.page.wait_for_timeout(150)
        self.page.mouse.wheel(0,-100)
        self.page.wait_for_function('Math.abs(scrollY/(document.querySelector("#journey").offsetHeight-innerHeight)-1/3)<.002',timeout=1800)
        self.assertAlmostEqual(self.fraction(),1/3,delta=.002)
        self.page.wait_for_function('Math.abs(document.querySelector("#film").currentTime-287/72)<.06')
        self.assertGreater(float(self.page.locator('.copy.active .copy-content').evaluate('(e)=>getComputedStyle(e).opacity')),.99)

    def test_keyboard_settles_but_form_wheel_remains_native(self):
        self.open()
        self.page.keyboard.press('PageDown')
        self.page.wait_for_timeout(600)
        self.assertAlmostEqual(self.fraction(),1/3,delta=.002)
        self.open('#advisor')
        card=self.page.locator('.advisor-card')
        box=card.bounding_box(); self.page.mouse.move(box['x']+30,box['y']+30)
        before=self.page.evaluate('scrollY')
        self.page.mouse.wheel(0,110); self.page.wait_for_timeout(400)
        self.assertAlmostEqual(self.page.evaluate('scrollY')-before,110,delta=3)


if __name__ == '__main__': unittest.main(verbosity=2)
