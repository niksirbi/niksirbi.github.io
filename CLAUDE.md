# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a personal academic website built with [Quarto](https://quarto.org/), deployed to GitHub Pages at https://www.nikosirmpilatze.com/. The site showcases research publications, projects, blog posts, and talks.

## Key Commands

### Build and Preview
```bash
quarto preview        # Start local development server
quarto render         # Build site to build/ directory
```

### Publication Management
```bash
# Fetch and update publications from OpenAlex API
uv run scripts/fetch_my_publications.py
```

### Linting
```bash
pre-commit run --all-files    # Run codespell linting
```

## Architecture

### Content Structure
- `index.qmd` - Homepage with bio and current role
- `publications/` - Publication listings (featured and full list)
- `projects/` - Active and past projects
- `blog/` - Blog posts
- `talks/` - Conference and seminar presentations
- `static/` - Images, fonts, and other static assets

### Configuration
- `_quarto.yml` - Main Quarto configuration
  - Sets output directory to `build/` (deployed to gh-pages)
  - Defines navbar with social media links (GitHub, Mastodon, Bluesky, ORCID)
  - Uses custom fonts (Barlow for body, JetBrains Mono for code)
  - Supports light/dark themes via `styles.scss` and `styles-dark.scss`

### Publications System
The publications workflow has two key components:

1. **Automated Fetching** (`scripts/fetch_my_publications.py`):
   - Uses PEP 723 inline script dependencies (pyalex, pyyaml)
   - Run with `uv run` (no venv needed)
   - Fetches publications from OpenAlex API for author ID `A5086452643`
   - Filters by work type (article, review, preprint)
   - Handles edge cases: manually includes publications where author is past 100th position, excludes certain IDs
   - Formats author strings intelligently (includes first 3 authors if user is among them, otherwise shows "First Author et al.")
   - Removes duplicate preprints when journal version exists
   - Sorts by author position and publication date
   - Updates `publications/publications.yml` preserving existing entries

2. **Display** (`publications/index.qmd`):
   - Two Quarto listings: `featured.yml` (curated highlights) and `publications.yml` (complete list)
   - Shows DOI links, journal names, author lists, and citation counts

### Deployment
- **CI/CD**: `.github/workflows/render_and_deploy.yaml`
  - Runs on push to main, PRs, or manual dispatch
  - Linting via `neuroinformatics-unit/actions/lint@v2`
  - Renders and deploys to gh-pages branch using `quarto-dev/quarto-actions/publish@v2`

- **Scheduled Updates**: `.github/workflows/update_publications.yaml`
  - Runs monthly (1st of each month at 8:00 UTC) or on manual trigger
  - Fetches latest publications via script
  - Opens PR if publications.yml changes

### Styling
- `fonts.scss` - Font-face declarations for Barlow and JetBrains Mono
- `styles.scss` - Light theme customizations
- `styles-dark.scss` - Dark theme customizations
- Custom domain via `CNAME` file (included in resources)

## Important Notes

- The `build/` directory is the output directory and is gitignored (deployed via gh-pages branch)
- Publications are semi-automated: script updates `publications.yml`, but `featured.yml` is manually curated
- The site uses the iconify extension (`_extensions/mcanouil/iconify/`) for custom icons (Bluesky, ORCID)
- Pre-commit hooks run codespell with config in `.codespellrc`
