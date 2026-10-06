"""A host returning 200 for Range requests must still support scroll scrubbing."""
import unittest
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

class VideoCDN(unittest.TestCase):
    def test_full_response_host_can_seek_and_cancel_loads(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            web = Path(__file__).resolve().parents[1] / 'web'
            page.route('**/journey-*.mp4', lambda route: route.fulfill(
                status=200, content_type='video/mp4',
                body=(web / urlparse(route.request.url).path.lstrip('/')).read_bytes()))
            page.goto('http://127.0.0.1:8046/', wait_until='domcontentloaded')
            page.wait_for_function('document.querySelector(".stage").classList.contains("video-ready")')
            page.locator('.rail a').nth(2).click()
            page.wait_for_function('Math.abs(document.querySelector("#film").currentTime-287/36)<.08 && !document.querySelector("#film").seeking', timeout=8000)
            page.locator('#motion').click()
            self.assertIsNone(page.locator('#film').get_attribute('src'))
            browser.close()

if __name__ == '__main__':
    unittest.main(verbosity=2)
