import logging

from bs4 import BeautifulSoup

from src.model.publication import Publication, PublicationReference

from .browser import Browser, Page


class Parser:
    api_url = "https://www.sciencedirect.com"

    def __init__(
        self,
        browser: Browser,
        ddir: str,
        dclean: bool = False,
    ):
        self.browser = browser
        self._ddir = ddir
        self._dclean = dclean

    async def parse_record_by_id(self, id: str) -> Publication:
        return await self.parse_record(
            f"{self.api_url}/science/article/abs/pii/{id}",
        )

    async def parse_record(self, url: str) -> Publication:
        page = await self.browser.new_page(url)

        # content = await page.content()

        refs = await self._extract_refs(page)
        bibliography = await self._fetch_bibliography(page)

        await page.close()

        return Publication(**{
            "references": refs,
            "cites": [],
            "bib": bibliography,
        })

    async def _fetch_bibliography(self, page: Page) -> str:
        logging.info(f"extracting bibliography from {page.url}")

        async with page.expect_download() as download_info:
            cite = page.locator(
                '#export-citation',
            )
            await cite.click()

            cite_download_bib = cite.locator(
                '#popover-content-export-citation-popover',
            ).locator(
                'button[aria-label="bibtex"]'
            )
            await cite_download_bib.click()

        download = await download_info.value

        filename = self._ddir + "/" + download.suggested_filename

        await download.save_as(filename)

        with open(filename, "r") as f:
            content = f.read()

        if self._dclean:
            await download.delete()

        return content

    async def _extract_refs(self, page: Page) -> list[PublicationReference]:
        logging.info(f"extracting refs from {page.url}")

        html = await page.content()
        soup = BeautifulSoup(html, features="html.parser")

        refs = []
        for el in soup.find_all("li", {"class": "bib-reference"}):
            ref = el.find("a", href=True)

            data = {
                "title": el.text,
                "url": None,
            }

            if ref is not None:
                data["url"] = self.api_url + ref["href"]

            refs.append(PublicationReference(**data))

        logging.info(f"extracted {len(refs)} refs from {page.url}")

        return refs
