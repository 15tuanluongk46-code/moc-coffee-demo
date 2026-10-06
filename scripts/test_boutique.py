"""Boutique acceptance: actual DOM, network and user interactions."""
import unittest
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8046/'


class Boutique(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width':390,'height':844}, reduced_motion='reduce')
        self.page = self.context.new_page()
        self.page.set_default_timeout(4000)

    def tearDown(self):
        self.context.close()

    def test_journey_remains_bounded_and_connects_to_boutique(self):
        self.page.goto(BASE)
        self.page.locator('.rail a').nth(3).click()
        self.assertEqual(self.page.locator('#chapter-number').inner_text(), '04')
        self.assertAlmostEqual(self.page.evaluate('scrollY'), self.page.evaluate('document.querySelector("#journey").offsetHeight-innerHeight'), delta=3)
        self.page.locator('#explore-products').click()
        self.page.wait_for_function('document.documentElement.classList.contains("browsing")')
        self.assertTrue(self.page.locator('#product-title').is_visible())
        self.page.locator('.wordmark').click()
        self.page.wait_for_function('scrollY < 5')
        self.assertEqual(self.page.locator('#chapter-number').inner_text(), '01')

    def test_turntable_keyboard_hotspots_and_reset(self):
        self.page.goto(BASE+'#product-viewer', wait_until='networkidle')
        image = self.page.locator('#spin-image')
        self.page.wait_for_function('document.querySelector("#spin-image").naturalWidth>0')
        self.page.locator('#spin-next').click()
        self.page.wait_for_function('document.querySelector("#spin-image").dataset.frame==="1"')
        self.page.locator('#spin-surface').focus()
        self.page.keyboard.press('ArrowRight')
        self.page.wait_for_function('document.querySelector("#spin-image").dataset.frame==="2"')
        self.page.locator('#spin-reset').click()
        self.page.wait_for_function('document.querySelector("#spin-image").dataset.frame==="0"')
        self.page.get_by_role('button', name='Mức rang', exact=True).click()
        self.assertIn('vừa', self.page.locator('#product-detail').inner_text())
        self.assertTrue(image.evaluate('(img)=>img.complete && img.naturalWidth>0'))

    def test_advisor_back_edit_result_and_restart(self):
        self.page.goto(BASE+'#advisor', wait_until='networkidle')
        self.page.get_by_role('button', name='Bắt đầu chọn gu', exact=True).click()
        self.page.get_by_label('Đậm và đắng').check()
        self.page.get_by_role('button', name='Tiếp tục', exact=True).click()
        self.page.get_by_label('Phin', exact=True).check()
        self.page.get_by_role('button', name='Quay lại', exact=True).click()
        self.assertTrue(self.page.get_by_label('Đậm và đắng').is_checked())
        self.page.get_by_label('Thơm và chua nhẹ').check()
        self.page.get_by_role('button', name='Tiếp tục', exact=True).click()
        self.assertTrue(self.page.get_by_label('Phin', exact=True).is_checked())
        self.page.get_by_role('button', name='Tiếp tục', exact=True).click()
        self.page.get_by_label('Với sữa', exact=True).check()
        self.page.get_by_role('button', name='Xem gợi ý', exact=True).click()
        self.assertTrue(self.page.locator('#advisor-result').is_visible())
        self.assertIn('phin', self.page.locator('#advisor-result').inner_text().lower())
        self.assertIn('sữa', self.page.locator('#advisor-result').inner_text().lower())
        self.page.get_by_role('button', name='Chỉnh câu trả lời', exact=True).click()
        self.assertTrue(self.page.get_by_label('Thơm và chua nhẹ').is_checked())
        self.page.get_by_role('button', name='Làm lại', exact=True).click()
        self.assertTrue(self.page.get_by_role('button', name='Bắt đầu chọn gu', exact=True).is_visible())

    def test_viewer_lazy_and_no_javascript_content(self):
        urls=[]
        self.page.on('request',lambda r:urls.append(r.url))
        self.page.goto(BASE,wait_until='networkidle')
        self.assertLessEqual(len([u for u in urls if '/spin/' in u]),1)
        with self.browser.new_context(java_script_enabled=False) as ctx:
            page=ctx.new_page();page.goto(BASE,wait_until='networkidle')
            self.assertTrue(page.locator('#product-title').is_visible())
            self.assertTrue(page.locator('#brew-guide').is_visible())
            self.assertIn('JavaScript',page.locator('#advisor').inner_text())

    def test_journey_exit_keeps_scene_until_boutique_covers_it(self):
        self.page.goto(BASE,wait_until='networkidle')
        self.page.evaluate('scrollTo(0,document.querySelector("#journey").offsetHeight-innerHeight+100)')
        self.page.wait_for_function('document.documentElement.classList.contains("browsing")')
        self.assertEqual(self.page.locator('.stage').evaluate('(e)=>getComputedStyle(e).visibility'),'visible')

    def test_drag_failed_frame_and_retry(self):
        self.page.route('**/spin/01.webp',lambda route:route.abort())
        self.page.goto(BASE+'#product-viewer',wait_until='networkidle')
        self.page.locator('#spin-next').click()
        self.page.wait_for_function('document.querySelector("#spin-status").textContent.includes("chưa tải được")')
        self.assertEqual(self.page.locator('#spin-image').get_attribute('data-frame'),'0')
        self.assertTrue(self.page.locator('#spin-image').evaluate('(e)=>e.naturalWidth>0'))
        self.page.unroute('**/spin/01.webp')
        self.page.locator('#spin-reset').click();self.page.locator('#spin-next').click()
        self.page.wait_for_function('document.querySelector("#spin-image").dataset.frame==="1"')
        self.page.locator('#spin-reset').click()
        self.page.wait_for_function('document.querySelector("#spin-image").dataset.frame==="0"')
        box=self.page.locator('#spin-surface').bounding_box()
        x,y=box['x']+box['width']/2,box['y']+box['height']/2
        self.page.mouse.move(x,y);self.page.mouse.down();self.page.mouse.move(x+56,y,steps=8);self.page.mouse.up()
        self.page.wait_for_function('document.querySelector("#spin-image").dataset.frame==="4"')

    def test_boutique_history_and_responsive_layout(self):
        errors=[];self.page.on('pageerror',lambda error:errors.append(str(error)))
        self.page.goto(BASE+'#collection',wait_until='networkidle')
        self.page.get_by_role('link',name='Ngắm từng chi tiết',exact=True).click()
        self.page.go_back();self.page.wait_for_url('**/#collection')
        self.page.go_forward();self.page.wait_for_url('**/#product-viewer')
        for width,height in [(320,568),(390,844),(768,1024),(844,390),(1440,900)]:
            self.page.set_viewport_size({'width':width,'height':height})
            self.page.wait_for_timeout(80)
            self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),width)
            self.assertTrue(self.page.locator('#spin-surface').is_visible())
        self.assertEqual(errors,[])

    def test_touch_rotation_preserves_vertical_scrolling(self):
        with self.browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce') as ctx:
            page=ctx.new_page();page.goto(BASE+'#product-viewer',wait_until='networkidle')
            page.locator('#spin-surface').scroll_into_view_if_needed()
            page.wait_for_function('document.querySelector("#spin-image").naturalWidth>0')
            box=page.locator('#spin-surface').bounding_box()
            x,y=box['x']+box['width']/2,box['y']+box['height']/2
            cdp=ctx.new_cdp_session(page)
            def gesture(dx,dy):
                cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
                for i in range(1,9):
                    cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+dx*i/8,'y':y+dy*i/8}]})
                    page.wait_for_timeout(25)
                cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
            gesture(56,0)
            page.wait_for_function('document.querySelector("#spin-image").dataset.frame==="4"')
            before=page.evaluate('scrollY')
            gesture(0,-130)
            page.wait_for_function('(before)=>scrollY>before+25',arg=before)
            self.assertEqual(page.locator('#spin-image').get_attribute('data-frame'),'4')


if __name__=='__main__': unittest.main(verbosity=2)
