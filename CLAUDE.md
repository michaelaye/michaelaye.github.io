# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Quarto-based personal academic homepage for Michael Aye (planetary scientist). Published at https://michaelaye.github.io via GitHub Pages. Remote: `git@github.com:michaelaye/michaelaye.github.io.git`.

## Build & Development Commands

```bash
quarto preview          # Local dev server with live reload
quarto render           # Build full site to _site/
```

Deployment is automatic: pushing to `main` triggers the GitHub Actions workflow (`.github/workflows/publish.yml`) which renders and publishes to the `gh-pages` branch.

## Architecture

**Static site generator:** Quarto with `project: type: website` configuration in `_quarto.yml`.

**Content types and their listing pages:**

| Content | Directory | Listing page | Listing type | Format |
|---------|-----------|-------------|--------------|--------|
| Blog posts | `posts/` | `posts.qmd` | `default` | `.qmd` or `.md` |
| Talks | `talks/` | `talks.qmd` | `default` | `.qmd` (reveal.js) |
| Projects | `projects/` | `projects.qmd` | `grid` | `.md` |

Each content item lives in its own subdirectory with an `index.qmd` or `index.md` file and co-located assets (images, PDFs).

**Listing behavior:** Quarto auto-discovers content via `listing: contents: <directory>` in each listing `.qmd` file, sorted by `date desc`. Metadata defaults for posts and talks are in `posts/_metadata.yml` and `talks/_metadata.yml`.

**Theming:** Dual light/dark theme (Flatly/Darkly). Homepage uses the `trestles` about template.

**Code execution:** `freeze: auto` in `_quarto.yml` — computational outputs are cached in `_freeze/`. Posts default to `freeze: true`.

**Extension:** `sellorm/quarto-social-embeds` provides shortcodes for embedding YouTube, Twitter, Mastodon, Vimeo, Loom, and GitHub Gists.

## Adding Content

**New blog post:** Create `posts/<slug>/index.qmd` (or `.md`):
```yaml
---
title: "Post Title"
subtitle: "Optional subtitle"
summary: "Brief summary for listing"
author: "Michael Aye"
categories: [python, topic]
date: YYYY-MM-DD
---
```

**New talk (reveal.js):** Create `talks/<date-slug>/index.qmd`:
```yaml
---
title: "Talk Title"
author: "Michael Aye"
format:
  revealjs:
    theme: default
    slide-number: true
    logo: logo.svg
    footer: "Conference info"
date: YYYY-MM-DD
categories: [online-presentation]
---
```

**New project:** Create `projects/<slug>/index.md`:
```yaml
---
title: "Project Name"
summary: "One-line description"
author: ["Michael Aye"]
categories: [python]
date: YYYY-MM-DD
image: featured.png
---
```

## Key Files

- `_quarto.yml` — Site-wide config (navbar, theme, execution settings)
- `index.qmd` — Homepage (about page with bio, education, experience)
- `bibliography.qmd` — Bibliography page using BibTeX files
- `MyPublications.bib` — Publication bibliography data
- `styles.css` — Custom CSS overrides (minimal)
