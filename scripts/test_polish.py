"""User-facing advisor navigation and small-screen reading regressions."""
import unittest
from playwright.sync_api import sync_playwright


class Polish(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 320, 'height': 568}, reduced_motion='reduce')
        self.page = self.context.new_page()
        self.page.set_default_timeout(4000)

    def tearDown(self):
        self.context.close()

    def begin(self):
        self.page.goto('about:blank')
        self.page.goto('http://127.0.0.1:8046/#advisor', wait_until='networkidle')
        self.page.locator('#advisor-start').click()

    def answer(self, method='Máy espresso'):
        for value in ['Thơm và chua nhẹ', method, 'Với sữa']:
            self.page.get_by_label(value, exact=True).check()
            self.page.locator('#advisor-next').click()

    def assert_readable(self, selector):
        self.page.wait_for_function('''selector => {
            const r=document.querySelector(selector).getBoundingClientRect();
            const h=document.querySelector('.header').getBoundingClientRect().bottom;
            return r.top>=h+7 && r.bottom<=innerHeight-7;
        }''', arg=selector)

    def test_questions_and_result_are_visible_after_each_step(self):
        for width, height in [(320, 568), (360, 640), (390, 844)]:
            with self.subTest(width=width):
                self.page.set_viewport_size({'width': width, 'height': height})
                self.begin()
                self.assert_readable('#advisor-question legend')
                for value in ['Thơm và chua nhẹ', 'Máy espresso', 'Với sữa']:
                    self.page.get_by_label(value, exact=True).check()
                    self.page.locator('#advisor-next').click()
                    self.assert_readable('#advisor-result h3' if value == 'Với sữa' else '#advisor-question legend')
                self.assertEqual(self.page.evaluate('document.activeElement.tagName'), 'H3')

    def test_recipe_link_targets_selected_method_and_focus(self):
        for method, label, anchor in [('Phin', 'Phin', 'brew-phin'), ('Pour-over', 'Pour-over', 'brew-pour-over'), ('Máy espresso', 'Espresso', 'brew-espresso')]:
            with self.subTest(method=method):
                self.begin(); self.answer(method)
                link = self.page.get_by_role('link', name='Xem cách pha ' + label, exact=True)
                self.assertEqual(link.get_attribute('href'), '#' + anchor)
                link.click()
                self.assert_readable('#' + anchor + ' h3')
                self.assertEqual(self.page.evaluate('document.activeElement.textContent'), label)
                self.assertEqual(self.page.locator('#' + anchor).evaluate('(e)=>e.getAnimations().length'), 0)

    def test_small_text_and_secondary_link_are_readable_and_tappable(self):
        self.page.goto('http://127.0.0.1:8046/#collection', wait_until='networkidle')
        for selector in ['#spin-help', '#spin-status', '#product-detail', '.advisor-privacy', '#spin-reset', '.product-hotspots button']:
            self.assertGreaterEqual(self.page.locator(selector).first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)'), 12, selector)
        for selector in ['.product-hero figcaption', '.material-story figcaption']:
            self.assertGreaterEqual(self.page.locator(selector).evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)'), 11, selector)
        box = self.page.locator('.product-links a[href="#advisor"]').bounding_box()
        self.assertGreaterEqual(box['height'], 44)

    def test_recipe_highlight_stops_when_reduced_motion_is_enabled(self):
        self.page.emulate_media(reduced_motion='no-preference')
        self.begin(); self.answer()
        self.page.get_by_role('link', name='Xem cách pha Espresso', exact=True).click()
        self.page.wait_for_function("document.querySelector('#brew-espresso').getAnimations().length===1")
        self.page.emulate_media(reduced_motion='reduce')
        self.page.wait_for_function("document.querySelector('#brew-espresso').getAnimations().length===0", timeout=500)

    def test_detail_height_stays_stable_across_options_and_resize(self):
        self.page.goto('http://127.0.0.1:8046/#product-viewer', wait_until='networkidle')
        for width, height in [(320, 568), (390, 844), (1440, 900)]:
            self.page.set_viewport_size({'width': width, 'height': height})
            self.page.wait_for_timeout(100)
            heights=[]
            for key in ['origin', 'roast', 'pack', 'origin']:
                self.page.locator('[data-detail="' + key + '"]').click()
                heights.append(self.page.locator('#product-detail').bounding_box()['height'])
            self.assertLessEqual(max(heights)-min(heights), 1, (width, heights))


if __name__ == '__main__':
    unittest.main(verbosity=2)
