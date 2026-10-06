"""Arrival timing, media readiness and actual timeline progress (no screenshot assertions)."""
import unittest
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8046/'

class MotionTiming(unittest.TestCase):
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
        self.page.set_default_timeout(8000)

    def tearDown(self):
        self.context.close()

    def test_intro_waits_for_media_then_advances(self):
        held = []
        self.page.route('**/journey-desktop.mp4', lambda r: held.append(r))
        self.page.goto(BASE, wait_until='domcontentloaded')
        self.page.wait_for_timeout(350)
        premature = self.page.evaluate('document.getAnimations().some(a=>a.id==="moc-camera-intro")')
        held[0].continue_()
        self.assertFalse(premature)
        self.page.wait_for_function('document.getAnimations().some(a=>a.id==="moc-camera-intro" && a.currentTime>50 && !a.pending)')

    def test_reveal_waits_for_decoded_arrival_and_wheel_is_not_rushed(self):
        self.page.goto(BASE, wait_until='domcontentloaded')
        self.page.wait_for_function('document.querySelector(".stage").classList.contains("video-ready")')
        self.page.wait_for_timeout(1600)
        self.page.evaluate('''() => { window.samples=[]; const until=performance.now()+2100;
          function tick(){const film=document.querySelector('#film');const active=document.querySelector('.copy.active');
          const a=active.querySelector('.line-reveal').getAnimations().find(a=>a.id==='moc-chapter');
          samples.push({at:performance.now(),y:scrollY,time:film.currentTime,chapter:active.id,
            opacity:Number(getComputedStyle(active.querySelector('.copy-content')).opacity),reveal:!!a});
          if(performance.now()<until)requestAnimationFrame(tick);}tick(); }''')
        self.page.mouse.move(1100, 450)
        self.page.mouse.wheel(0, 140)
        self.page.wait_for_timeout(2200)
        samples = self.page.evaluate('samples')
        moving = [s for s in samples if 2 < s['y'] < 1198]
        self.assertGreater(moving[-1]['at'] - moving[0]['at'], 850)
        revealed = [s for s in samples if s['chapter']=='roast' and s['reveal']]
        self.assertTrue(revealed)
        self.assertGreaterEqual(revealed[0]['opacity'], .94)
        self.assertGreater(revealed[0]['time'], 3.45)

    def test_product_entry_has_staged_reveal_and_cancels_in_static(self):
        self.page.goto(BASE+'#collection', wait_until='domcontentloaded')
        self.page.wait_for_function('document.querySelector(".product-hero").getAnimations().some(a=>a.id==="moc-product-entry")')
        self.page.locator('#motion').click()
        self.assertFalse(self.page.evaluate('document.getAnimations().some(a=>a.id==="moc-product-entry")'))

    def test_stalled_pending_animation_recovers_without_resetting_paused(self):
        self.page.goto(BASE, wait_until='domcontentloaded')
        self.page.wait_for_function('document.documentElement.classList.contains("motion-enabled")')
        self.page.evaluate('''() => {const element=document.querySelector('.scene-drift');
          window.stall=element.animate([{opacity:.9},{opacity:1}],{duration:4000,id:'moc-test-stall'});
          Object.defineProperty(stall,'pending',{get:()=>stall.startTime===null});
          const state=Object.getOwnPropertyDescriptor(Animation.prototype,'playState').get;
          Object.defineProperty(stall,'playState',{get:()=>stall.startTime===null?'running':state.call(stall)});
          stall.startTime=null;
          window.heldAnimation=element.animate([{opacity:1},{opacity:1}],{duration:4000});heldAnimation.pause();}''')
        self.page.wait_for_function('stall.startTime!==null && stall.currentTime>20')
        self.assertEqual(self.page.evaluate('heldAnimation.playState'), 'paused')

    def test_slow_media_uses_poster_intro_without_late_replay(self):
        held=[]
        self.page.route('**/journey-desktop.mp4',lambda r:held.append(r))
        self.page.goto(BASE,wait_until='domcontentloaded')
        self.page.wait_for_function('document.getAnimations().some(a=>a.id==="moc-camera-intro")')
        self.page.wait_for_function('!document.getAnimations().some(a=>a.id==="moc-camera-intro")')
        held[0].continue_()
        self.page.wait_for_function('document.querySelector(".stage").classList.contains("video-ready")')
        self.assertFalse(self.page.evaluate('document.getAnimations().some(a=>a.id==="moc-camera-intro")'))

    def test_interaction_during_loading_does_not_replay_intro(self):
        held=[]
        self.page.route('**/journey-desktop.mp4',lambda r:held.append(r))
        self.page.goto(BASE,wait_until='domcontentloaded')
        self.page.mouse.move(1100,450);self.page.mouse.wheel(0,100)
        self.page.wait_for_timeout(1500)
        held[0].continue_()
        self.page.wait_for_function('document.querySelector(".stage").classList.contains("video-ready")')
        self.assertFalse(self.page.evaluate('document.getAnimations().some(a=>a.id==="moc-camera-intro")'))

if __name__ == '__main__':
    unittest.main(verbosity=2)
