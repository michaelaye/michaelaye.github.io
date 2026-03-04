---
title: "ads-bib-tools: Fetch Your Full Publication List from NASA ADS"
subtitle: "ORCID-based bibliography management for Quarto and static sites"
summary: "A script that fetches your complete publication list from NASA ADS by ORCID, cleans up publisher artifacts, and tags entries as refereed or non-refereed — ready for a Quarto bibliography page."
author: "Michael Aye"
categories: [python, quarto, academic, bibliography, open-source, nasa-ads]
date: 2026-03-03
featured: true
draft: false
---

Existing ADS bibliography tools like [adstex](https://github.com/yymao/adstex), [filltex](https://github.com/dgerosa/filltex), and [bibslurp](https://github.com/mkmcc/bibslurp) are all designed for LaTeX workflows: you have a `.tex` file with `\cite{}` commands, and they resolve the citation keys against ADS.

But if you maintain an academic homepage with [Quarto](https://quarto.org) (or any static site generator), you need the opposite workflow: start from **your identity** (ORCID), fetch **everything**, and produce a clean `.bib` file ready for the web.

That's what [ads-bib-tools](https://github.com/michaelaye/ads-bib-tools) does.

## What it does

One command:

```bash
python update_bib.py --orcid 0000-0002-4088-1928
```

This:

1. **Fetches** all papers linked to your ORCID from NASA ADS, querying all three claim sources (`orcid_pub`, `orcid_user`, `orcid_other`) so nothing gets missed
2. **Strips** bulky fields like `abstract` and `file` that bloat the `.bib` and aren't needed for rendering
3. **Cleans** MathML markup that some publishers (notably Elsevier) embed in titles — converts it to proper LaTeX notation so your titles render correctly
4. **Tags** each entry with `refereed` or `non-refereed` in the BibTeX `keywords` field, based on the ADS `property` metadata

The output is a website-ready `.bib` file. The script is idempotent — run it again and it updates cleanly without duplicating tags.

## The MathML problem

This is one of those things you don't notice until it ruins a title on your homepage. Some publishers store formulas as MathML in their metadata, and ADS faithfully passes it through. So instead of seeing:

> CO₂ ice sublimation on Mars

you get a mess of `<mml:msub>` tags in your BibTeX title field. The script detects and converts these to LaTeX notation automatically.

## Refereed vs. non-refereed

The ADS API exposes a `property` field on each paper that includes `REFEREED` for peer-reviewed publications. The script reads this and adds a `refereed` or `non-refereed` keyword to each BibTeX entry.

Why bother? Because you can then split your bibliography page into tabs. This is exactly what I do on [my bibliography page](/bibliography.html) using the [chronobib](https://github.com/michaelaye/chronobib) Quarto extension:

```yaml
---
bibliography: MyPublications.bib
citeproc: false
filters:
  - michaelaye/highlight-author
  - michaelaye/chronobib
highlight-author: "Aye"
chronobib:
  split-keyword: refereed
---

::: {.panel-tabset}
## Refereed

::: {#refs-refereed}
:::

## Non-Refereed

::: {#refs-nonrefereed}
:::
:::
```

This gives you two tabs, each with year-grouped entries, and your name highlighted in bold. Three tools, one clean result.

## Installation

```bash
git clone https://github.com/michaelaye/ads-bib-tools.git
pip install requests
```

Or grab just the script:

```bash
curl -O https://raw.githubusercontent.com/michaelaye/ads-bib-tools/main/update_bib.py
pip install requests
```

You'll need an [ADS API token](https://ui.adsabs.harvard.edu/user/settings/token) exported as `ADS_API_TOKEN`.

## Prerequisites: complete your ORCID claims in ADS

The script can only fetch papers that ADS has linked to your ORCID. If your claims are incomplete, papers will be silently missing from the output. It's worth checking this before your first run.

1. **Link your ORCID to ADS.** In [ADS user settings](https://ui.adsabs.harvard.edu/user/settings/orcid), connect your ORCID account if you haven't already.

2. **Claim missing papers.** Search for your publications in ADS. On any paper that isn't yet linked to your ORCID, click the ORCID icon to claim it. ADS supports three claim sources:
   - `orcid_pub` — claimed by the publisher (automatic for some journals)
   - `orcid_user` — claimed by you through the ADS interface
   - `orcid_other` — claimed through other ORCID-connected services

   The script queries all three sources, so a paper claimed through any of these channels will be included.

3. **Check for completeness.** Run this ADS query to see everything currently linked to your ORCID:

   ```
   orcid:0000-0002-4088-1928
   ```

   Compare the result count against what you expect. Conference abstracts, instrument papers, and older publications are the most common gaps.

Once your claims are complete, the script will pick up everything automatically on every subsequent run.

## The full pipeline

Here's how all the pieces fit together for an academic Quarto homepage:

1. **ads-bib-tools** fetches and cleans your `.bib` file from ADS
2. **[highlight-author](https://github.com/michaelaye/highlight-author)** highlights your name in the rendered bibliography
3. **[chronobib](https://github.com/michaelaye/chronobib)** groups entries by year and optionally splits them into refereed/non-refereed tabs

Each tool works independently, but they're designed to complement each other.

## Links

- GitHub: [michaelaye/ads-bib-tools](https://github.com/michaelaye/ads-bib-tools)
- DOI: [![DOI](https://zenodo.org/badge/1171942580.svg)](https://doi.org/10.5281/zenodo.18853606)
- Companion extensions: [highlight-author](https://github.com/michaelaye/highlight-author), [chronobib](https://github.com/michaelaye/chronobib)
- Live example: [my bibliography page](/bibliography.html)
