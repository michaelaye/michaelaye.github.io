---
title: "highlight-author: A Quarto Extension to Highlight Your Name in Bibliographies"
subtitle: "Because every CV, grant proposal, and publication page needs it"
summary: "I built a Quarto extension that highlights a specific author's name in bibliography entries. It handles all common citation formats and supports bold, italic, underline, or custom CSS styling."
author: "Michael Aye"
categories: [quarto, academic, bibliography, open-source]
date: 2026-03-02
featured: true
draft: false
---

If you've ever built an academic homepage, a CV, or a grant proposal in Quarto, you've probably wanted one simple thing: **make your own name stand out** in the bibliography.

CSL (Citation Style Language) doesn't support this. Pandoc's citeproc doesn't support it. There's no built-in Quarto option for it. So I built [highlight-author](https://github.com/michaelaye/highlight-author), a small Quarto extension that does exactly this.

## Installation

```bash
quarto add michaelaye/highlight-author
```

## Usage

Add three lines to your YAML front matter:

```yaml
citeproc: false
filters:
  - michaelaye/highlight-author
highlight-author: "Aye"
```

That's it. Every occurrence of "Aye" and its surrounding name parts gets wrapped in `<strong>` tags. Here's what it looks like on [my bibliography page](/bibliography.html):

> Walter, S. H. G., **K.-M. Aye**, R. Jaumann, and F. Postberg. 2024. "Mars Reconnaissance Orbiter Context Camera Updated In-Flight Calibration." *Earth and Space Science* 11 (2).

> Brown, Sierra, Michael St. Clair, Chase Million, Sabrina Curtis, **K. -Michael Aye**, and Zack Weinberg. 2024. "PDR: The Planetary Data Reader." *The Journal of Open Source Software* 9 (102).

> **Aye, K.-M.**, B. T. Greenhagen, and J. P. Williams. 2020. "Investigating the Possibility of Super-Resolution Reconstruction of LRO Diviner Data." In *51st Annual Lunar and Planetary Science Conference*.

Notice it handles all the ways a name appears in citations:

- **Surname-first:** **Aye, K.-M.** or **Aye, Klaus Michael**
- **Given-name-first:** **K.-M. Aye** or **Klaus-Michael Aye**
- **Initials only:** **K. M. Aye**

The entire name span (surname + given names) gets highlighted together, not just the surname in isolation.

## Choosing a style

Bold is the default, but you can pick other styles:

```yaml
# Italic
highlight-author:
  name: "Aye"
  style: italic

# Underline
highlight-author:
  name: "Aye"
  style: underline

# Custom CSS class
highlight-author:
  name: "Aye"
  style: "my-highlight"
```

The CSS class option is the most flexible. For example, bold + blue:

```css
.my-highlight {
  font-weight: bold;
  color: #2563eb;
}
```

## Why `citeproc: false`?

Pandoc runs citeproc *after* all Lua filters, which means a normal filter never sees the rendered bibliography. The workaround is to set `citeproc: false` in YAML and have the filter call `pandoc.utils.citeproc()` internally. This is the same approach used by other bibliography-processing extensions like [citetools](https://github.com/bcdavasconcelos/citetools).

If you use other bibliography filters alongside this one (e.g., for year grouping), put `highlight-author` first in the filter list.

## Who is this for?

Anyone with a Quarto document and a bibliography where one name should stand out:

- Academic homepages and publication lists
- CVs and resumes
- Grant proposals (NSF, NASA, and others expect the PI's name highlighted)
- Tenure and promotion packets
- Lab group pages
- Theses and dissertations

The extension works with any Quarto output format: HTML, PDF, Word.

## Links

- GitHub: [michaelaye/highlight-author](https://github.com/michaelaye/highlight-author)
- Install: `quarto add michaelaye/highlight-author`
- Live example: [my bibliography page](/bibliography.html)
- Quarto discussion: [Feature: highlight/bold specific author name in bibliography](https://github.com/orgs/quarto-dev/discussions/14140)
- Upstream proposal: [citetools #4](https://github.com/bcdavasconcelos/citetools/issues/4) — proposed as a feature for the citetools extension
