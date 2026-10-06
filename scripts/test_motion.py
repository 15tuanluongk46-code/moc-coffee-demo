"""Motion behavior and cancellation contracts in a clean Chromium session."""
import unittest
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8046/'


class MotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 390, 'height': 844})
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def open(self):
        self.page.goto(BASE, wait_until='domcontentloaded')

    def jump(self, fraction):
        self.page.evaluate('(p)=>scrollTo({top:p*(document.querySelector("#journey").offsetHeight-innerHeight),behavior:"instant"})', fraction)

    def test_intro_once_and_scroll_cancels_hint(self):
        self.open()
        self.page.wait_for_function('document.querySelector(".wordmark").getAnimations().some(a=>a.id==="moc-intro")')
        self.page.wait_for_timeout(1050)
        self.assertEqual(self.page.locator('.wordmark').evaluate('(e)=>e.getAnimations().length'), 0)
        self.jump(1 / 3)
        self.page.wait_for_function('document.querySelector("#chapter-number").textContent==="02"')
        self.assertEqual(self.page.locator('.scroll-hint').evaluate('(e)=>e.getAnimations().length'), 0)
        self.jump(0)
        self.page.wait_for_timeout(550)
        self.assertEqual(self.page.locator('.wordmark').evaluate('(e)=>e.getAnimations().length'), 0)

    def test_reverse_and_fast_navigation_cleanup(self):
        self.open()
        self.jump(2 / 3)
        self.page.wait_for_function('document.querySelector("#chapter-number").textContent==="03"')
        self.jump(1 / 3)
        self.page.wait_for_function('document.querySelector("#title-roast .line-reveal").getAnimations().some(a=>a.id==="moc-chapter")')
        frames = self.page.locator('#title-roast .line-reveal').first.evaluate('(e)=>e.getAnimations().find(a=>a.id==="moc-chapter").effect.getKeyframes()')
        self.assertIn('-105%', frames[0]['transform'])
        for fraction in [.98, 0, .67, .33, 1]:
            self.jump(fraction)
            self.page.wait_for_timeout(40)
        self.page.wait_for_function('document.querySelector(".chapter-copy").getAnimations({subtree:true}).length===0', timeout=1500)
        self.assertEqual(self.page.locator('.copy.leaving').count(), 0)
        self.assertEqual(self.page.locator('.copy.active').get_attribute('id'), 'ritual')
        self.assertTrue(self.page.locator('.copy:not(.active)').evaluate_all('(es)=>es.every(e=>e.inert && getComputedStyle(e).visibility==="hidden")'))
        self.assertEqual(self.page.locator('.chapter-copy').evaluate('(e)=>e.getAnimations({subtree:true}).length'), 0)

    def test_static_and_reduced_motion_disable_decorations(self):
        self.page.emulate_media(reduced_motion='reduce')
        self.open()
        self.assertEqual(self.page.evaluate('document.getAnimations().length'), 0)
        self.page.emulate_media(reduced_motion='no-preference')
        self.page.wait_for_function('document.documentElement.classList.contains("motion-enabled")')
        self.page.locator('#motion').click()
        self.assertEqual(self.page.evaluate('document.getAnimations().length'), 0)
        self.jump(1)
        self.page.wait_for_function('document.querySelector("#chapter-number").textContent==="04"')
        self.page.locator('#discover').click()
        self.assertEqual(self.page.evaluate('document.getAnimations().length'), 0)
        self.page.keyboard.press('Escape')

    def test_modal_stagger_pauses_ambient_and_restores_focus(self):
        self.open()
        self.jump(1)
        self.page.wait_for_function('document.querySelector("#chapter-number").textContent==="04"')
        self.page.wait_for_timeout(600)
        self.page.locator('#discover').click()
        self.assertTrue(self.page.locator('#flavors').evaluate('(e)=>e.getAnimations().some(a=>a.id==="moc-dialog")'))
        delays = self.page.locator('.notes > span').evaluate_all('(es)=>es.map(e=>e.getAnimations()[0]?.effect.getTiming().delay)')
        self.assertEqual(delays, [120, 210, 300])
        self.assertEqual(self.page.locator('.ambient').evaluate('(e)=>getComputedStyle(e).animationPlayState'), 'paused')
        self.page.keyboard.press('Escape')
        self.page.wait_for_function('!document.documentElement.classList.contains("modal-lock")', timeout=1000)
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'discover')
        self.assertFalse(self.page.locator('#flavors').evaluate('(e)=>e.open'))
        self.assertEqual(self.page.locator('#flavors').evaluate('(e)=>e.getAnimations({subtree:true}).length'), 0)

    def test_hidden_document_pauses_and_resumes_background(self):
        self.open()
        # Simulate the visibility lifecycle deterministically in headless Chromium.
        self.page.evaluate('Object.defineProperty(document,"hidden",{configurable:true,get:()=>true});document.dispatchEvent(new Event("visibilitychange"))')
        self.assertEqual(self.page.locator('.ambient').evaluate('(e)=>getComputedStyle(e).animationPlayState'), 'paused')
        self.page.evaluate('Object.defineProperty(document,"hidden",{configurable:true,get:()=>false});document.dispatchEvent(new Event("visibilitychange"))')
        self.assertEqual(self.page.locator('.ambient').evaluate('(e)=>getComputedStyle(e).animationPlayState'), 'running')

    def test_desktop_hover_and_finite_hint_preserve_layout(self):
        self.page.set_viewport_size({'width': 1440, 'height': 900})
        self.open()
        timing = self.page.locator('.scroll-hint').evaluate('(e)=>e.getAnimations()[0].effect.getTiming()')
        self.assertEqual(timing['iterations'], 2)
        self.page.wait_for_function('document.querySelector(".scroll-hint").getAnimations().length===0', timeout=5000)
        self.assertEqual(self.page.locator('.scroll-hint').evaluate('(e)=>e.getAnimations().length'), 0)
        link = self.page.locator('.copy.active .text-link')
        before = link.bounding_box()
        link.hover()
        self.page.wait_for_timeout(240)
        self.assertEqual(link.locator('span').evaluate('(e)=>getComputedStyle(e).translate'), '3px')
        self.assertEqual(link.bounding_box(), before)
        self.assertEqual(self.page.locator('.copy.active').evaluate('(e)=>e.getAnimations({subtree:true}).length'), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
