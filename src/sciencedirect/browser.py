import logging

from playwright.async_api import Page, async_playwright


class Browser:
    def __init__(self):
        self._browser = NotImplemented

    async def setup(self):
        playwright = await async_playwright().start()

        browser = await playwright.chromium.launch(
            headless=False,
            timeout=20_000,
            slow_mo=20_00,
        )

        # self._browser = browser
        self._browser = await browser.new_context()

    async def new_page(self, url: str) -> Page:
        logging.info(f"open {url} page")

        page = await self._browser.new_page()

        await page.goto(url, wait_until="load", timeout=20000)

        return page
