import requests
import json


def _clean_date(date: dict) -> dict | None:
    if date == None:
        return None
    return {key: val["value"] if val else None for key, val in date.items()}


def _clean_affiliation(affiliation: dict) -> dict:
    return {
        "start-date": _clean_date(affiliation["start-date"]),
        "end-date": _clean_date(affiliation["end-date"]),
        "organization": {
            "name": affiliation["organization"]["name"],
            "address": affiliation["organization"]["address"],
        },
        "role-title": affiliation["role-title"],
        "department-name": affiliation["department-name"],
    }


def _clean_work(work: dict) -> dict:
    return {
        "title": work["title"]["title"]["value"],
        "doi": work["external-ids"]["external-id"][0]["external-id-value"],
        "type": work["type"],
        "publication_date": work["publication-date"],
        "journal-title": work["journal-title"]["value"],
    }


def _clean_funding(funding: dict) -> dict:
    return {
        "title": funding["title"]["title"]["value"],
        "url": funding["url"]["value"],
        "type": funding["type"],
        "start-date": _clean_date(funding["start-date"]),
        "end-date": _clean_date(funding["end-date"]),
        "organization": funding["organization"],
    }


class OrcidData:
    name: str
    biography: str
    educations: list
    employments: list
    fundings: list
    works: list

    def __init__(self, orcid_response):
        name = orcid_response["person"]["name"]
        self.name = f"{name['given-names']['value']} {name['family-name']['value']}"
        self.biography = orcid_response["person"]["biography"]["content"]
        activities = orcid_response["activities-summary"]
        self.educations = []
        for education in activities["educations"]["affiliation-group"]:
            self.educations.append(
                _clean_affiliation(education["summaries"][0]["education-summary"])
            )

        self.employments = []
        for employment in activities["employments"]["affiliation-group"]:
            self.employments.append(
                _clean_affiliation(employment["summaries"][0]["employment-summary"])
            )

        self.works = []
        for work_group in activities["works"]["group"]:
            for work in work_group["work-summary"]:
                self.works.append(_clean_work(work))

        self.fundings = []
        for funding in activities["fundings"]["group"]:
            self.fundings.append(_clean_funding(funding["funding-summary"][0]))


def fetch_record(access_token: str, orcid: str) -> OrcidData:
    api_url = f"https://pub.orcid.org/v3.0/{orcid}/record"
    response = requests.get(
        api_url,
        headers={
            "Accept": "application/vnd.orcid+json",
            "Authorization": f"Bearer {access_token}",
        },
    )

    return OrcidData(response.json())
