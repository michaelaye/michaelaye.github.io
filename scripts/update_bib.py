#!/usr/bin/env python3
"""Fetch bibliography from NASA ADS by ORCID and write MyPublications.bib."""

import os
import re
import sys

import requests

ADS_BASE = "https://api.adsabs.harvard.edu/v1"
ORCID = "0000-0002-4088-1928"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "MyPublications.bib")


def strip_bibtex_field(bibtex: str, field: str) -> str:
    """Remove a BibTeX field that may span multiple lines with nested braces."""
    result = []
    lines = bibtex.split("\n")
    i = 0
    while i < len(lines):
        # Match field start: e.g. "  abstract = {"
        if re.match(rf"^\s*{field}\s*=\s*\{{", lines[i]):
            # Count braces to find the end of the field value
            depth = 0
            for ch in lines[i][lines[i].index("=") + 1 :]:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
            # If braces aren't balanced, consume subsequent lines
            while depth > 0 and i + 1 < len(lines):
                i += 1
                for ch in lines[i]:
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
            i += 1
        else:
            result.append(lines[i])
            i += 1
    return "\n".join(result)


def main():
    token = os.environ.get("ADS_API_TOKEN")
    if not token:
        print("ERROR: ADS_API_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Search for all papers by ORCID (all claim sources)
    # ADS stores ORCID claims in three fields:
    #   orcid_pub  — from publisher metadata
    #   orcid_user — from ADS-linked ORCID profile
    #   orcid_other — from ADS claiming interface
    # The generic "orcid:" may not cover all three, so we OR them explicitly.
    query = (
        f"orcid_pub:{ORCID} OR orcid_user:{ORCID} OR orcid_other:{ORCID}"
    )
    resp = requests.get(
        f"{ADS_BASE}/search/query",
        headers=headers,
        params={"q": query, "fl": "bibcode", "rows": 500},
    )
    resp.raise_for_status()
    docs = resp.json()["response"]["docs"]
    bibcodes = [doc["bibcode"] for doc in docs]

    if not bibcodes:
        print("WARNING: No papers found for ORCID", ORCID, file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(bibcodes)} papers on ADS")

    # Step 2: Export BibTeX for all bibcodes
    resp = requests.post(
        f"{ADS_BASE}/export/bibtex",
        headers=headers,
        json={"bibcode": bibcodes},
    )
    resp.raise_for_status()
    bibtex = resp.json()["export"]

    # Step 3: Clean up — strip file and abstract fields (may span multiple lines)
    bibtex = strip_bibtex_field(bibtex, "file")
    bibtex = strip_bibtex_field(bibtex, "abstract")

    # Step 4: Write output
    with open(OUTPUT, "w") as f:
        f.write(bibtex)

    # Count entries
    n_entries = len(re.findall(r"^@\w+\{", bibtex, re.MULTILINE))
    print(f"Wrote {n_entries} entries to {os.path.basename(OUTPUT)}")


if __name__ == "__main__":
    main()
