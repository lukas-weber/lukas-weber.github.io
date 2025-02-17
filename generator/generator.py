#!/usr/bin/env python3
import apis.orcid
import apis.crossref

import backends.website
import backends.cv

import argparse
import os

import markdown

md = markdown.Markdown()

parser = argparse.ArgumentParser(
    description="Generate a personal site based on an ORCID record and some metadata from the Crossref database."
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
parser.add_argument(
    "--backend",
    choices=["website", "cv", "publist"],
    required=True,
    help="Output backend",
)
parser.add_argument(
    "--cv-file",
    type=str,
    help="YAML file containing additional CV data for the tex backends",
)
args = parser.parse_args()

orcid_id = "0000-0003-4949-5529"
orcid_record = apis.orcid.fetch_record(
    access_token=args.orcid_access_token, orcid=orcid_id
)

crossref_works = apis.crossref.fetch_works([work["doi"] for work in orcid_record.works if work["type"] != "preprint"])


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
            "handle": "@lukas-weber",
        },
    ],
    "name": orcid_record.name + " – Physics",
    "biography": md.convert(orcid_record.biography),
    "employments": [format_activity(act) for act in orcid_record.employments],
    "educations": [format_activity(act) for act in orcid_record.educations],
    "works": [format_work(work) for work in crossref_works],
    "fundings": [format_funding(funding) for funding in orcid_record.fundings],
}

output_file = os.path.abspath(args.output_file)

os.chdir(os.path.dirname(os.path.realpath(__file__)))

if args.backend == "website":
    backends.website.generate(site_data=site_data, output_file=output_file)
elif args.backend == "cv" or args.backend == "publist":
    backends.cv.generate(
        site_data=site_data,
        template_file=f"templates/{args.backend}.tex",
        cv_file=args.cv_file,
        output_file=output_file,
    )
