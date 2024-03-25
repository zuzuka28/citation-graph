from dataclasses import dataclass


@dataclass
class PublicationReference:
    title: str
    url: str | None


@dataclass
class Publication:
    references: list[PublicationReference]
    cites: list[PublicationReference]

    bib: str
