---
title: "Building an Academic Homepage with Quarto"
subtitle: "Auto-updating bibliography, custom extensions, and GitHub Actions — the full stack"
summary: "A walkthrough of how I built my academic homepage with Quarto, including automated bibliography updates from NASA ADS, custom Lua extensions for year-grouped refereed/non-refereed display, and GitHub Actions for hands-off publishing."
author: "Michael Aye"
categories: [quarto, academic, open-source, github-actions, bibliography]
date: 2026-03-04
---

Most academic homepages are either a bare-bones departmental page that hasn't been updated since 2018, or an overengineered React app that took a month to build.
I wanted something in between: a site that looks professional, is easy to update, and keeps my publication list current without me lifting a finger.

Here's how I built it with [Quarto](https://quarto.org), a few custom extensions, and two GitHub Actions workflows.

## Why Quarto?

Quarto is a scientific publishing system built on Pandoc.
It understands YAML front matter, BibTeX, LaTeX math, cross-references, and multiple output formats — all things academics need and generic static site generators don't handle well out of the box.

My site uses `project: type: website` with the `trestles` about-page template for the homepage.
Blog posts, talks (as reveal.js slides), and project pages each live in their own directories and are auto-discovered by Quarto's listing mechanism.
I write content in `.qmd` or `.md`, and Quarto renders everything to a static site.
The [Quarto documentation](https://quarto.org/docs/guide/) is excellent — one of the best I've seen for any static site tool — and covers everything from basics to advanced customization.

The dual light/dark theme uses `sandstone` (light) and `superhero` (dark) from Bootswatch, configured in `_quarto.yml`:

```yaml
format:
  html:
    theme:
      light: sandstone
      dark: superhero
    css: styles.css
```

## The bibliography pipeline

My [bibliography page](/bibliography.html) shows every publication I have on NASA ADS, grouped by year, split into refereed and non-refereed tabs, with my name highlighted.
And it updates itself every week.

The pipeline has three pieces:

### 1. ads-bib-tools — fetch and clean

[ads-bib-tools](https://github.com/michaelaye/ads-bib-tools) is a Python script that queries the NASA ADS API using my ORCID, fetches all linked publications as BibTeX, and cleans them up:

- Strips bulky `abstract` and `file` fields
- Converts MathML markup (from publishers like Elsevier) to LaTeX
- Tags each entry with `refereed` or `non-refereed` in the BibTeX `keywords` field

One command produces a website-ready `.bib` file.
I wrote a [dedicated blog post](/posts/ads-bib-tools/) about this tool.

### 2. highlight-author — bold your name

The [highlight-author](https://github.com/michaelaye/highlight-author) Quarto extension is a Lua filter that bolds a specified author name in the rendered bibliography.
Configuration is one line in the document front matter:

```yaml
highlight-author: "Aye"
```

### 3. chronobib — year groups and tabs

The [chronobib](https://github.com/michaelaye/chronobib) extension groups bibliography entries by year and optionally splits them by a keyword.
Combined with Quarto's panel-tabset, this gives me refereed and non-refereed tabs, each with year headers:

```yaml
filters:
  - michaelaye/highlight-author
  - michaelaye/chronobib
chronobib:
  split-keyword: refereed
```

```markdown
::: {.panel-tabset}
## Refereed

::: {#refs-refereed}
:::

## Non-Refereed

::: {#refs-nonrefereed}
:::
:::
```

Three tools, each independent, but designed to work together.

## Automation with GitHub Actions

Two workflows handle everything:

### Publishing

Every push to `main` triggers the publish workflow.
It sets up Quarto, renders the site, and deploys to the `gh-pages` branch:

```yaml
on:
  push:
    branches: main

steps:
  - uses: actions/checkout@v4
  - uses: quarto-dev/quarto-actions/setup@v2
  - uses: quarto-dev/quarto-actions/publish@v2
    with:
      target: gh-pages
```

No manual deploys.
Push a new post, and it's live in a couple of minutes.

### Bibliography updates

A scheduled workflow runs every Sunday at 6 AM UTC.
It checks out the repo, runs `update_bib.py` to fetch the latest publications from ADS, and commits the updated `.bib` file if anything changed:

```yaml
on:
  schedule:
    - cron: '0 6 * * 0'
  workflow_dispatch:

steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
  - run: pip install requests
  - run: python scripts/update_bib.py
    env:
      ADS_API_TOKEN: ${{ secrets.ADS_API_TOKEN }}
  - run: |
      git diff --quiet MyPublications.bib && exit 0
      git config user.name "github-actions[bot]"
      git add MyPublications.bib
      git commit -m "Update bibliography from NASA ADS"
      git push
```

Because the push to `main` triggers the publish workflow, the bibliography commit automatically rebuilds and deploys the site.
The result: new publications appear on my homepage without any manual intervention.

## Will new papers show up automatically?

Mostly yes, but it depends on how the paper gets linked to your ORCID in ADS.

ADS tracks ORCID associations from three sources:

- **`orcid_pub`** — the publisher sends your ORCID to ADS. This happens automatically when you provide your ORCID during manuscript submission, which most major journals now support. New papers published this way will appear without any action on your part.
- **`orcid_user`** — you manually claim a paper through the ADS interface. Required for older papers or publications where you didn't provide your ORCID.
- **`orcid_other`** — claims made through ORCID's own search-and-link tools or third-party services.

The script queries all three sources, so anything claimed through any channel gets picked up.
In practice: if you consistently provide your ORCID when submitting papers, new publications will flow through automatically.
Conference abstracts, older papers, and publications from smaller journals that don't support ORCID integration will still need a manual claim in ADS.

My recommendation: check your ADS ORCID query once or twice a year and claim anything that's missing.
The weekly cron job handles the rest.

## Talks as live presentations

Quarto has native support for [reveal.js](https://revealjs.com/) presentations.
Each talk lives in its own subdirectory under `talks/` as an `index.qmd` with `format: revealjs` in the front matter.

The nice thing: when you click a talk from the [talks listing](/talks.html), it opens directly as a full-screen presentation in the browser — no PDF download, no extra clicks.
Visitors can navigate slides with arrow keys, and the talk is a live HTML document with working links, embedded media, and speaker notes.

```yaml
format:
  revealjs:
    theme: default
    slide-number: true
    logo: fu-logo.svg
    footer: "Conference info"
```

Because Quarto renders each talk as its own `index.html`, the listing page links straight to the presentation.
This makes conference talks permanently accessible at a stable URL you can put on your CV or share with colleagues.

## Other extensions

Two more extensions round out the setup:

- **[sellorm/quarto-social-embeds](https://github.com/sellorm/quarto-social-embeds)** — shortcodes for embedding YouTube, Mastodon, and other social media in posts
- **[quarto-ext/fontawesome](https://github.com/quarto-ext/fontawesome)** — Font Awesome icons, used for the Bluesky icon in the navbar

## The result

A professional academic homepage that:

- Renders from simple Markdown/YAML files
- Supports blog posts, reveal.js talks, and project pages
- Maintains a complete, auto-updating bibliography
- Deploys automatically on every push
- Costs nothing to host (GitHub Pages)

All the tools are open source.
The [source code for this site](https://github.com/michaelaye/michaelaye.github.io) is public if you want to see how it all fits together.

## Links

- Site source: [michaelaye/michaelaye.github.io](https://github.com/michaelaye/michaelaye.github.io)
- ads-bib-tools: [michaelaye/ads-bib-tools](https://github.com/michaelaye/ads-bib-tools)
- highlight-author: [michaelaye/highlight-author](https://github.com/michaelaye/highlight-author)
- chronobib: [michaelaye/chronobib](https://github.com/michaelaye/chronobib)
- Quarto: [quarto.org](https://quarto.org)
