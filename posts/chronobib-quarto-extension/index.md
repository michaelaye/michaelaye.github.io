---
title: "chronobib: Group Your Quarto Bibliography by Year"
subtitle: "A companion to highlight-author for academic publication pages"
summary: "A Quarto extension that splits your bibliography into year sections with headings, newest first. Pairs with highlight-author for a polished publication list."
author: "Michael Aye"
categories: [quarto, academic, bibliography, open-source]
date: 2026-03-02
featured: true
draft: false
---

After publishing [highlight-author](/posts/highlight-author-quarto-extension/) earlier today, I extracted the other half of my bibliography tooling into its own extension: [chronobib](https://github.com/michaelaye/chronobib).

## What it does

chronobib takes a flat bibliography and groups entries by publication year, adding section headings. The result on [my bibliography page](/bibliography.html) looks like this:

> ## 2024
>
> Brown, Sierra, et al. 2024. "PDR: The Planetary Data Reader." *JOSS* 9 (102).
>
> Walter, S. H. G., et al. 2024. "Mars Reconnaissance Orbiter Context Camera Updated In-Flight Calibration." *Earth and Space Science* 11 (2).
>
> ## 2023
>
> Mc Keown, L. E., et al. 2023. "Martian Araneiforms: A Review." *JGR Planets* 128 (4).
>
> ## 2022
>
> Portyankina, Ganna, et al. 2022. "Planet Four: Derived South Polar Martian Winds ..." *PSJ* 3 (2).

Instead of scrolling through a wall of references, readers can jump to a specific year via the table of contents.

## Installation and usage

```bash
quarto add michaelaye/chronobib
```

```yaml
bibliography: references.bib
citeproc: false
filters:
  - michaelaye/chronobib

nocite: |
  @*
```

That's it. Entries are sorted newest-first by default.

### Options

```yaml
chronobib:
  heading-level: 3      # H3 instead of default H2
  sort: ascending        # oldest first
```

## Pairing with highlight-author

The two extensions are designed to work together. Put highlight-author first (it runs citeproc), and chronobib detects the existing bibliography and skips the redundant citeproc call:

```yaml
citeproc: false
filters:
  - michaelaye/highlight-author
  - michaelaye/chronobib

highlight-author: "Aye"
```

This is exactly what powers [my bibliography page](/bibliography.html) — names highlighted in bold, entries grouped by year.

## How it works

Like highlight-author, chronobib needs `citeproc: false` because Pandoc runs citeproc *after* all Lua filters. The filter calls `pandoc.utils.citeproc()` internally (or skips it if another filter already did), then walks the `#refs` div, reads each entry's year from the bibliography metadata, groups them, and inserts heading elements between the year groups.

## Links

- GitHub: [michaelaye/chronobib](https://github.com/michaelaye/chronobib)
- Install: `quarto add michaelaye/chronobib`
- Companion: [michaelaye/highlight-author](https://github.com/michaelaye/highlight-author)
- Live example: [my bibliography page](/bibliography.html)
- Quarto discussion: [Feature: group bibliography entries by year](https://github.com/orgs/quarto-dev/discussions/14139)
