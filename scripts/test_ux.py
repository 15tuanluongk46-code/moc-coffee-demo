"""Regression cases from the user-flow audit; real Chromium, no app mocks."""
import unittest
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8046/'


class UserJourney(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(
            viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
        self.page = self.context.new_page()
        self.page.set_default_timeout(4000)

    def tearDown(self):
        self.context.close()

    def open(self):
        self.page.goto(BASE, wait_until='networkidle')

    def chapter(self, i):
        self.page.locator('.rail a').nth(i).click()
        self.page.wait_for_function('(i)=>document.querySelector("#chapter-number").textContent===String(i+1).padStart(2,"0")', arg=i)

    def test_landscape_controls_are_clickable(self):
        for w, h in [(844, 390), (667, 375)]:
            with self.subTest(viewport=(w, h)):
                self.page.set_viewport_size({'width': w, 'height': h})
                self.open()
                self.page.locator('.copy.active .text-link').click()
                self.chapter(3)
                self.page.locator('#discover').click()
                self.assertTrue(self.page.locator('dialog').evaluate('(d)=>d.open'))
                self.page.keyboard.press('Escape')

    def test_rotation_preserves_progress(self):
        self.open()
        self.chapter(2)
        for w, h in [(844, 390), (390, 844), (768, 1024)]:
            self.page.set_viewport_size({'width': w, 'height': h})
            self.page.wait_for_timeout(250)
            self.assertEqual(self.page.locator('#chapter-number').inner_text(), '03')
            fraction = self.page.evaluate('scrollY/(document.querySelector("#journey").offsetHeight-innerHeight)')
            self.assertAlmostEqual(fraction, 2/3, delta=.005)

    def test_wheel_over_copy_advances_journey(self):
        self.open()
        self.page.locator('.copy.active .description').hover()
        self.page.mouse.wheel(0, 900)
        self.page.wait_for_function('scrollY > 500')
        self.assertNotEqual(self.page.locator('#chapter-number').inner_text(), '01')

    def test_dialog_locks_background_and_restores_focus(self):
        self.open()
        self.chapter(3)
        before = self.page.evaluate('scrollY')
        self.page.locator('#discover').click()
        self.page.mouse.move(10, 100)
        self.page.mouse.wheel(0, -1000)
        self.page.wait_for_timeout(300)
        self.page.keyboard.press('Escape')
        self.page.wait_for_function('!document.documentElement.classList.contains("modal-lock")', timeout=1000)
        self.assertEqual(self.page.locator('#chapter-number').inner_text(), '04')
        self.assertAlmostEqual(self.page.evaluate('scrollY'), before, delta=2)
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'discover')

    def test_history_and_heading_focus(self):
        self.open()
        self.chapter(1)
        self.chapter(2)
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'title-brew')
        self.page.go_back()
        self.page.wait_for_function('location.hash==="#roast"')
        self.assertEqual(self.page.locator('#chapter-number').inner_text(), '02')
        self.page.go_forward()
        self.page.wait_for_function('location.hash==="#brew"')
        self.assertEqual(self.page.locator('#chapter-number').inner_text(), '03')

    def test_touch_targets_and_feedback(self):
        self.open()
        for box in self.page.locator('.rail a, #motion').evaluate_all('(els)=>els.map(e=>{const r=e.getBoundingClientRect();return {w:r.width,h:r.height}})'):
            self.assertGreaterEqual(box['w'], 44)
            self.assertGreaterEqual(box['h'], 44)
        self.assertTrue(self.page.locator('#status').is_visible())
        self.assertIn('video', self.page.locator('#motion').get_attribute('aria-label').lower())
        self.chapter(3)
        self.assertNotIn('CUỘN ĐỂ KHÁM PHÁ', self.page.locator('.scroll-hint').inner_text())

    def test_responsive_poster_avoids_desktop_download(self):
        requests = []
        self.page.on('request', lambda r: requests.append(r.url))
        self.open()
        self.assertFalse(any('/desktop-01.webp' in url for url in requests), requests)

    def test_video_timeout_has_visible_retry(self):
        self.page.emulate_media(reduced_motion='no-preference')
        held = []
        self.page.route('**/*.mp4', lambda route: held.append(route))
        self.page.goto(BASE, wait_until='domcontentloaded')
        self.page.wait_for_function('document.querySelector("#status").textContent.includes("chưa tải được")', timeout=15000)
        self.assertTrue(self.page.locator('#status').is_visible())
        self.assertEqual(self.page.locator('#motion').get_attribute('aria-pressed'), 'true')
        self.assertTrue(self.page.locator('#poster').evaluate('(img)=>img.complete && img.naturalWidth > 0'))
        for route in held:
            route.abort()
        self.page.unroute('**/*.mp4')
        self.page.locator('#motion').click()
        self.page.wait_for_function('document.querySelector(".stage").classList.contains("video-ready")')
        self.assertEqual(self.page.locator('#motion').get_attribute('aria-pressed'), 'false')

    def test_motion_rotation_and_modal_preserve_position(self):
        self.page.emulate_media(reduced_motion='no-preference')
        self.open()
        self.chapter(2)
        self.page.wait_for_function('Math.abs(scrollY/(document.querySelector("#journey").offsetHeight-innerHeight)-2/3)<.001')
        self.page.set_viewport_size({'width': 844, 'height': 390})
        self.page.wait_for_function('document.querySelector("#film").dataset.view==="desktop" && document.querySelector(".stage").classList.contains("video-ready")')
        self.assertEqual(self.page.locator('#chapter-number').inner_text(), '03')
        self.chapter(3)
        self.page.wait_for_function('Math.abs(scrollY/(document.querySelector("#journey").offsetHeight-innerHeight)-1)<.001')
        self.page.locator('#discover').click()
        self.page.mouse.move(5, 100)
        self.page.mouse.wheel(0, -1000)
        self.page.wait_for_timeout(300)
        self.page.keyboard.press('Escape')
        self.page.wait_for_function('!document.documentElement.classList.contains("modal-lock")', timeout=1000)
        self.assertEqual(self.page.locator('#chapter-number').inner_text(), '04')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'discover')

    def test_no_javascript_reads_all_chapters(self):
        with self.browser.new_context(java_script_enabled=False, viewport={'width':390,'height':844}) as ctx:
            page = ctx.new_page()
            page.goto(BASE, wait_until='networkidle')
            for title in ['#title-origin', '#title-roast', '#title-brew', '#title-ritual']:
                self.assertTrue(page.locator(title).is_visible(), title)
            self.assertEqual(page.locator('.copy[inert]').count(), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
