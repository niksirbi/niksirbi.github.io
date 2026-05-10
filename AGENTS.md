# AGENTS.md

This file provides guidance to AI coding assistants when working with code in this repository.

## Overview

This is a personal academic website built with [Quarto](https://quarto.org/), deployed to GitHub Pages at https://www.nikosirmpilatze.com/. The site showcases research publications, projects, blog posts, and talks by Niko Sirmpilatze — a neuroscientist and research software engineer at UCL.

## Key Commands

### Build and Preview
```bash
quarto preview        # Start local development server
quarto render         # Build site to build/ directory
```

### Publication Management
```bash
# Fetch and update publications from OpenAlex API (no venv needed; uses inline PEP 723 deps)
uv run scripts/fetch_my_publications.py
```

### Linting
```bash
pre-commit run --all-files    # Run codespell linting
```

## Architecture

### Content Structure
- `index.qmd` — Homepage with bio, current role, and social links (uses Quarto `trestles` about template)
- `publications/` — Publication listings
  - `featured.yml` — Manually curated highlights (default listing, grid-style with images)
  - `publications.yml` — Full auto-fetched list (table listing)
  - `index.qmd` — Renders both listings
- `projects/` — Active and past projects
  - `active.yml` — Currently active projects (grid layout with images)
  - `past.yml` — Past contributions (table layout)
  - `index.qmd` — Renders both listings
- `blog/` — Blog posts
  - `professional.yml` — External blog posts authored in a professional capacity (links out)
  - `index.qmd` — Table listing with RSS feed enabled
- `talks/` — Conference and seminar presentations
  - `talks.yml` — Talk entries with date, title, venue (subtitle), and format (categories)
  - `index.qmd` — Table listing
- `scripts/` — Utility scripts
  - `fetch_my_publications.py` — Fetches publications from the OpenAlex API
- `static/` — Images, fonts, and other static assets
  - `static/img/` — Images used across listings and the homepage
  - `static/fonts/` — Self-hosted `.woff2` font files for Barlow and JetBrains Mono
- `templates/` — (Currently empty; reserved for future Quarto templates)

### Configuration
- `_quarto.yml` — Main Quarto configuration
  - Output directory: `build/` (gitignored; deployed via the `gh-pages` branch)
  - `AGENTS.md` is explicitly excluded from rendering (`render: ["*.qmd", "!AGENTS.md"]`)
  - `CNAME` and `static/fonts/` are declared as resources so they land in the build output
  - **Navbar (left):** Home, Projects, Blogposts, Publications, Talks
  - **Navbar (right):** GitHub, Mastodon, Bluesky, ORCID (via iconify), RSS feed
  - **Favicon:** `static/img/favicon-32.png`; **OG image:** `static/img/headshot.jpg`
  - **Fonts:** Barlow (body), JetBrains Mono (code)
  - **Themes:** `flatly` (light) + `styles.scss` / `darkly` (dark) + `styles-dark.scss`
  - **Layout:** `page-layout: full`, `toc: true` by default

### Styling
- `fonts.scss` — `@font-face` declarations for Barlow and JetBrains Mono (loaded from `static/fonts/`)
- `styles.scss` — Light-theme overrides: imports fonts, sets `$primary: #18bc9c` (teal), styles navbar padding
- `styles-dark.scss` — Dark-theme overrides: imports fonts, sets `$primary: #2c2c2c`, styles navbar padding and `kbd` background

### Extensions (`_extensions/`)
- `mcanouil/iconify/` — Custom Quarto shortcode for iconify icons; used for Bluesky and ORCID icons (`{{< iconify simple-icons bluesky >}}`, `{{< iconify simple-icons orcid >}}`)
- `kazuyanagimoto/awesomecv/` — AwesomeCV extension (for CV/résumé generation if needed)
- `quarto-ext/fontawesome/` — FontAwesome icon shortcodes

### Publications System

The publications workflow has two components:

1. **Automated Fetching** (`scripts/fetch_my_publications.py`):
   - Uses PEP 723 inline script dependencies (`pyalex`, `pyyaml`); run with `uv run` (no venv needed)
   - Fetches from the OpenAlex API for author ID `A5086452643` (Niko Sirmpilatze), filtered to work types: `article`, `review`, `preprint`
   - **Edge cases:**
     - `EXTRA_PUB_IDS` — manually includes publications where the author appears past position 100 (truncated OpenAlex responses)
     - `EXCLUDE_PUB_IDS` — hard-coded list of OpenAlex work IDs to exclude
   - **Author formatting:** includes first 3 authors if the user is among them; otherwise shows "First Author et al."
   - **Deduplication:** removes preprint entries when a journal version of the same title exists
   - **Sorting:** by author position (ascending), then publication date (descending)
   - Updates `publications/publications.yml`, preserving existing entries and manual `author` overrides

2. **Display** (`publications/index.qmd`):
   - **Featured listing** (`featured.yml`): default Quarto listing type with images; fields: image, date, title, subtitle, author, description
   - **All publications listing** (`publications.yml`): table listing; fields: date, title, Journal (subtitle), Authors (author), Cited by (description)
   - Publications link to DOIs; citation counts come from OpenAlex

### Blog System (`blog/`)
- Currently one listing source: `professional.yml` — posts authored in a professional capacity
- Each entry links to an **external** website (e.g., neuroinformatics.dev, brainglobe.info, software.ac.uk)
- Table listing with fields: date, author, title, categories (displayed as "Website"), description
- RSS feed is generated at `/blog/index.xml` and linked in the navbar

### Talks System (`talks/`)
- `talks.yml` entries include: path (video/slides URL), date, title, subtitle (venue), description, image, categories (format: Video, Slides, etc.)
- Table listing; `subtitle` displayed as "Venue", `categories` displayed as "Format"

### Projects System (`projects/`)
- `active.yml` — grid layout with images; fields: image, title, categories, description
- `past.yml` — table layout; fields: title, categories, description
- Categories used: Software, Teaching, Standards, Dataset, Community, Conference

### Deployment
- **CI/CD** (`.github/workflows/render_and_deploy.yaml`):
  - Triggers: push to `main`, pull requests, tags, or manual `workflow_dispatch`
  - **Linting job:** runs `neuroinformatics-unit/actions/lint@v2` (codespell) on all events
  - **Build & publish job:** renders and deploys to the `gh-pages` branch via `quarto-dev/quarto-actions/publish@v2` — **only on push to `main`**
  - Uses `GITHUB_TOKEN` for pushing to `gh-pages`

- **Scheduled Publication Updates** (`.github/workflows/update_publications.yaml`):
  - Triggers: monthly cron (`0 8 1 * *` — 1st of each month at 08:00 UTC) or manual `workflow_dispatch`
  - Steps: checkout → install `uv` (`astral-sh/setup-uv@v6`) → run fetch script → open PR via `peter-evans/create-pull-request@v6` if `publications.yml` changed
  - PR is created on branch `update-publications` and auto-deleted after merge

### Linting / Pre-commit
- `.pre-commit-config.yaml` — runs `codespell` (v2.4.1) via pre-commit.ci (monthly autoupdate)
- `.codespellrc`:
  - Skips: `.git`, `*.js`
  - Checks hidden files
  - Ignores regex: `.*# codespell-ignore$`
  - Ignored words list: `Domin`

## Important Notes

- The `build/` directory is gitignored; it is deployed automatically to the `gh-pages` branch via CI
- `publications/publications.yml` is auto-updated by the fetch script; `publications/featured.yml` is **manually curated**
- Blog posts in `blog/professional.yml` link to external websites — they are not hosted on this site
- The `CNAME` file contains `nikosirmpilatze.com` (without `www`); the canonical site URL in `_quarto.yml` uses `https://www.nikosirmpilatze.com/`
- A `.venv` directory exists at the repo root (created by `uv`), but the publication script uses PEP 723 inline deps and does not require it to be activated
- The `templates/` directory is currently empty
