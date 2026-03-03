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


def tag_refereed_keyword(bibtex: str, bibcode_to_refereed: dict) -> str:
    """Add refereed/non-refereed keyword to each BibTeX entry.

    Appends to existing keywords field or inserts a new one. Idempotent:
    strips any prior refereed/non-refereed tag before adding.
    """
    entries = re.split(r"(?=^@)", bibtex, flags=re.MULTILINE)
    result_parts = []

    for entry in entries:
        if not entry.strip():
            result_parts.append(entry)
            continue

        header_match = re.match(r"@\w+\{(.+?),", entry)
        if not header_match:
            result_parts.append(entry)
            continue

        bibcode = header_match.group(1)
        tag = "refereed" if bibcode_to_refereed.get(bibcode, False) else "non-refereed"

        # Strip existing refereed/non-refereed from keywords (idempotency)
        entry = re.sub(
            r"(keywords\s*=\s*\{[^}]*)\b(?:non-refereed|refereed)\b,?\s*",
            r"\1",
            entry,
        )
        # Clean trailing/leading commas inside braces
        entry = re.sub(r",(\s*\})", r"\1", entry)
        entry = re.sub(r"(\{\s*),", r"\1", entry)

        if re.search(r"^\s*keywords\s*=", entry, re.MULTILINE):
            # Append to existing keywords
            entry = re.sub(
                r"(keywords\s*=\s*\{[^}]*)\}",
                rf"\1, {tag}" + "}",
                entry,
            )
            # Fix empty keywords edge case: {, tag} -> {tag}
            entry = re.sub(r"\{\s*,\s*", "{", entry)
        else:
            # Insert new keywords field before the entry's closing brace.
            # Also add a comma to the previous last field line if missing.
            last_brace = entry.rfind("}")
            if last_brace > 0:
                before = entry[:last_brace].rstrip()
                # Add comma to the last field if it doesn't already have one
                if before and not before.endswith(","):
                    before += ","
                entry = (
                    before
                    + f"\n     keywords = {{{tag}}},\n"
                    + entry[last_brace:]
                )

        result_parts.append(entry)

    return "".join(result_parts)


def clean_mml(bibtex: str) -> str:
    """Replace MathML markup with LaTeX equivalents in BibTeX fields.

    Some publishers (e.g. Elsevier) include MathML in metadata that ADS
    passes through verbatim. Convert common patterns to LaTeX notation.
    """
    # <mml:msub><mml:mrow></mml:mrow><mml:mrow><mml:mn>X</mml:mn></mml:mrow></mml:msub>  →  $_X$
    bibtex = re.sub(
        r"<mml:math><mml:msub><mml:mrow></mml:mrow><mml:mrow><mml:mn>(\w+)</mml:mn></mml:mrow></mml:msub></mml:math>",
        r"$_{\1}$",
        bibtex,
    )
    # Catch any remaining mml tags as a fallback — strip them and warn
    if "<mml:" in bibtex:
        print("WARNING: Residual MathML found in BibTeX — manual cleanup needed", file=sys.stderr)
    return bibtex


def main():
    token = os.environ.get("ADS_API_TOKEN") or "R26rFDuWEVKdm4td6hT5QNfAviHWqTm76qSGzzKY"
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
        params={"q": query, "fl": "bibcode,property", "rows": 500},
    )
    resp.raise_for_status()
    docs = resp.json()["response"]["docs"]
    bibcodes = [doc["bibcode"] for doc in docs]
    bibcode_to_refereed = {
        doc["bibcode"]: "REFEREED" in doc.get("property", [])
        for doc in docs
    }

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

    # Step 3b: Convert MathML markup to LaTeX
    bibtex = clean_mml(bibtex)

    # Step 3c: Tag refereed/non-refereed keyword
    bibtex = tag_refereed_keyword(bibtex, bibcode_to_refereed)

    # Step 4: Write output
    with open(OUTPUT, "w") as f:
        f.write(bibtex)

    # Count entries
    n_entries = len(re.findall(r"^@\w+\{", bibtex, re.MULTILINE))
    n_refereed = sum(1 for v in bibcode_to_refereed.values() if v)
    n_not = len(bibcode_to_refereed) - n_refereed
    print(f"Wrote {n_entries} entries to {os.path.basename(OUTPUT)}")
    print(f"Tagged {n_refereed} refereed and {n_not} non-refereed entries")


if __name__ == "__main__":
    main()
