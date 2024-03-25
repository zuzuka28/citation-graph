
import csv

import bibtexparser

from src.model import Publication


class SciencedirectProcessor:
    def __init__(self, save_filename: str):
        self._filename = save_filename

    def process(self, page: Publication) -> bool:
        row = self._page_to_row(page)
        if row is None:
            return True

        self._save_row(row)

        return True

    def _page_to_row(self, page: Publication) -> list[str] | None:
        bib = bibtexparser.parse_string(page.bib)
        entry = bib.entries[0]

        title_field = entry.get("title")
        title = title_field.value if title_field is not None else ""

        linked_titles = []
        for link in page.references:
            linked_titles.append(link.title)

        return [
            title,
            "-::-".join(linked_titles),
        ]

    def _save_row(self, row: list[str]):
        with open(self._filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)
