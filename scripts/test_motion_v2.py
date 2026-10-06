"""Motion direction: visible introduction, camera-synced copy and interruptible idle."""
import unittest
from playwright.sync_api import sync_playwright


class MotionDirection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1440, 'height': 900})
        self.page = self.context.new_page()
        self.page.set_default_timeout(5000)
        self.errors = []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def open(self):
        self.page.goto('http://127.0.0.1:8046/', wait_until='domcontentloaded')

    def jump(self, progress):
        self.page.evaluate('(p)=>scrollTo({top:p*(document.querySelector("#journey").offsetHeight-innerHeight),behavior:"instant"})', progress)

    def test_opening_has_scene_push_and_masked_headline(self):
        self.open()
        self.page.wait_for_function('document.querySelector(".scene-camera")?.getAnimations().some(a=>a.id==="moc-camera-intro")')
        self.assertEqual(self.page.locator('#title-origin .line-mask').count(), 2)
        timing = self.page.locator('.scene-camera').evaluate('(e)=>e.getAnimations()[0].effect.getTiming()')
        self.assertGreaterEqual(timing['duration'], 1200)
        self.page.wait_for_function('document.querySelector(".scene-camera").getAnimations().length===0')
        self.assertEqual(self.page.locator('#title-origin').inner_text(), 'Bắt đầu từ\nmột hạt nhỏ.')

    def test_idle_moves_scene_not_text_and_pauses_when_scrolling(self):
        self.open()
        self.page.wait_for_timeout(1700)
        first = self.page.locator('.scene-drift').evaluate('(e)=>getComputedStyle(e).transform')
        heading = self.page.locator('#title-origin').bounding_box()
        self.page.wait_for_timeout(800)
        self.assertNotEqual(self.page.locator('.scene-drift').evaluate('(e)=>getComputedStyle(e).transform'), first)
        self.assertEqual(self.page.locator('#title-origin').bounding_box(), heading)
        self.jump(.1)
        self.page.wait_for_function('document.documentElement.classList.contains("motion-scrolling")')
        self.assertEqual(self.page.locator('.scene-drift').evaluate('(e)=>getComputedStyle(e).animationPlayState'), 'paused')

    def test_copy_recedes_during_camera_travel_returns_on_arrival(self):
        self.open()
        self.jump(1 / 6)
        self.page.wait_for_function('!document.querySelector("#film").seeking && Math.abs(document.querySelector("#film").currentTime-287/144)<.08')
        self.page.wait_for_function('Number(getComputedStyle(document.querySelector(".copy.active .copy-content")).opacity)<.2')
        self.jump(1 / 3)
        self.page.wait_for_function('Number(getComputedStyle(document.querySelector("#roast .copy-content")).opacity)>.99')
        self.assertEqual(self.page.locator('.copy.active').get_attribute('id'), 'roast')

    def test_dialog_close_has_exit_and_preserves_lock_until_end(self):
        self.open()
        self.jump(1)
        self.page.wait_for_timeout(1100)
        self.page.locator('#discover').click()
        self.page.wait_for_timeout(600)
        self.page.keyboard.press('Escape')
        self.assertTrue(self.page.locator('#flavors').evaluate('(e)=>e.open'))
        self.assertTrue(self.page.locator('#flavors').evaluate('(e)=>e.getAnimations().some(a=>a.id==="moc-dialog-exit")'))
        self.page.wait_for_function('!document.querySelector("#flavors").open')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'discover')
        self.assertEqual(self.page.locator('.copy.active').get_attribute('id'), 'ritual')

    def test_static_cancels_idle_and_reveals_copy_mid_travel(self):
        self.open()
        self.jump(1 / 6)
        self.page.wait_for_timeout(400)
        self.page.locator('#motion').click()
        self.assertEqual(self.page.evaluate('document.getAnimations().length'), 0)
        self.assertEqual(self.page.locator('.copy.active .copy-content').evaluate('(e)=>getComputedStyle(e).opacity'), '1')

    def test_rail_marker_matches_deep_link_and_resize(self):
        self.page.goto('http://127.0.0.1:8046/#brew', wait_until='networkidle')
        for width, height in [(1440, 900), (390, 844), (844, 390)]:
            self.page.set_viewport_size({'width': width, 'height': height})
            self.page.wait_for_function('''() => {
                const rail = document.querySelector('.rail');
                const active = rail.querySelector('[aria-current]');
                return parseFloat(rail.style.getPropertyValue('--rail-position')) === active.offsetTop;
            }''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
