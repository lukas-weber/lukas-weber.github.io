#!/usr/bin/env python3
import apis.orcid
import apis.crossref

import jinja2
import markdown

import argparse

md = markdown.Markdown()

parser = argparse.ArgumentParser(
    description="Generate a personal site based on an ORCID record and some metadata from the Crossref database."
)
parser.add_argument(
    "--template-file",
    type=str,
    required=True,
    help="The jinja2 template file that should be filled with information",
)
parser.add_argument(
    "--output-file", type=str, required=True, help="Destination for the filled template"
)
parser.add_argument(
    "--orcid-access-token",
    type=str,
    required=True,
    help="Public access token for the ORCID api",
)
args = parser.parse_args()

orcid_id = "0000-0003-4949-5529"
orcid_record = apis.orcid.fetch_record(
    access_token=args.orcid_access_token, orcid=orcid_id
)

crossref_works = apis.crossref.fetch_works([work["doi"] for work in orcid_record.works])


def format_date(date: dict, month=False) -> str:
    if not date:
        return "present"

    return f"{date['year']}/{date['month']}" if month else f"{date['year']}"


def format_activity(act: dict) -> dict:
    return {
        **act,
        "start-date": format_date(act["start-date"]),
        "end-date": format_date(act["end-date"]),
    }


def format_funding(funding: dict) -> dict:
    return {
        **funding,
        "start-date": format_date(funding["start-date"]),
        "end-date": format_date(funding["end-date"]),
    }


def comma_list(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return ", ".join(items[:-1]) + f", and {items[-1]}"


def format_work(work: apis.crossref.Work) -> dict:

    return {
        "authors": comma_list(work.authors),
        "journal": work.journal,
        "title": work.title,
        "volume": work.volume,
        "year": work.year,
        "page": work.page,
        "doi": work.doi,
    }


site_data = {
    "title": "Lukas Weber – Physics",
    "orcid_id": orcid_id,
    "contacts": [
        {
            "type": "email",
            "icon": "images/icons/email.svg",
            "handle": "lweber at flatironinstitute.org",
            "link": "mailto://lweber at flatironinstitute.org",
        },
        {
            "type": "ORCID",
            "icon": "images/icons/orcid.svg",
            "link": "https://orcid.org/0000-0003-4949-5529",
            "handle": "0000-0003-4949-5529",
        },
        {
            "type": "Google Scholar",
            "icon": "images/icons/google_scholar.svg",
            "link": "https://scholar.google.com/citations?user=erKPhQ8AAAAJ",
            "handle": "Google Scholar",
        },
        {
            "type": "Github",
            "icon": "images/icons/github.svg",
            "link": "https://github.com/lukas-weber",
            "handle": "Github",
        },
    ],
    "name": orcid_record.name,
    "biography": md.convert(orcid_record.biography),
    "employments": [format_activity(act) for act in orcid_record.employments],
    "educations": [format_activity(act) for act in orcid_record.educations],
    "works": [format_work(work) for work in crossref_works],
    "fundings": [format_funding(funding) for funding in orcid_record.fundings],
}

subs = (
    jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
    .get_template(args.template_file)
    .render(**site_data)
)

with open(args.output_file, "w") as f:
    f.write(subs)
