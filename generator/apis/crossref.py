from dataclasses import dataclass
import requests


@dataclass
class Work:
    authors: list[str]
    journal: str
    title: str
    volume: str
    year: str
    page: str
    doi: str


def _clean_author(author: dict) -> str:
    short_given = " ".join(f"{n[0]}." for n in author["given"].split(" "))
    return f"{short_given} {author['family']}"


def _clean_work(work: dict) -> Work:
    return Work(
        authors=[_clean_author(author) for author in work["author"]],
        title=work["title"][0],
        doi=work["DOI"],
        journal=work["short-container-title"][0],
        page=work.get("page", work.get("article-number", None)),
        volume=work.get("volume", ""),
        year=work["published"]["date-parts"][0][0],
    )


def fetch_works(dois: list[str]) -> list[Work]:
    works = []
    for doi in dois:
        response = requests.get(
            f"https://api.crossref.org/works/{doi}",
            headers={
                "Accept": "application/json",
            },
        )
        works.append(_clean_work(response.json()["message"]))

    return works
