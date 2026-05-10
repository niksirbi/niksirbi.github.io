# AGENTS.md

Personal academic website for Niko Sirmpilatze, built with
[Quarto](https://quarto.org/) and deployed to GitHub Pages at
https://www.nikosirmpilatze.com/.

## Key Commands

```bash
quarto preview                  # local dev server
quarto render                   # build to build/ (gitignored)
uv run scripts/fetch_my_publications.py  # update publications from OpenAlex
pre-commit run --all-files      # lint (codespell + Unicode gremlins)
quarto render cv/cv.qmd --to typst  # rebuild CV PDF manually
```

## Fonts & Styling

**Barlow** (body) and **JetBrains Mono** (code) throughout -- including the
Typst CV PDF. TTF files live in `static/fonts/`; web fonts in `.woff2` format
are declared in `fonts.scss`. The primary colour is `#18bc9c` (teal, light
theme). Read `_quarto.yml`, `styles.scss`, and `fonts.scss` before touching
any styling.

## Content Structure

Each section of the site follows the same pattern: a `.yml` data file (or
files) + an `index.qmd` that renders it as a Quarto listing. Read the existing
`.yml` files and `index.qmd` for a section before editing it.

| Section | Key files | Notes |
|---------|-----------|-------|
| Home | `index.qmd` | `trestles` about template |
| Publications | `publications/featured.yml`, `publications/publications.yml` | `featured.yml` is manually curated; `publications.yml` is auto-fetched -- do not hand-edit |
| Projects | `projects/active.yml`, `projects/past.yml` | grid + table listings |
| Blog | `blog/professional.yml` | links to external posts only |
| Talks | `talks/talks.yml` | |
| CV | `cv/cv.qmd` | Typst source; compiled to `build/cv/cv.pdf` by pre-render script; navbar links directly to the PDF |

## Gotchas

- `build/` is gitignored; deployed automatically to `gh-pages` via CI.
- `cv/cv.qmd` is excluded from the HTML render pass (see `_quarto.yml`);
  `cv/cv.pdf` and `cv/.quarto/` are gitignored.
- The CV pre-render script skips Typst compilation if `cv/cv.pdf` is already
  newer than `cv/cv.qmd`. If you change fonts, styling, or other project config
  that affects the PDF, force a rebuild with `quarto render cv/cv.qmd --to typst`.
- `publications/publications.yml` is auto-generated -- edit
  `publications/featured.yml` for manual curation instead.
- The `.venv/` at the repo root uses Python 3.13; activate with
  `source .venv/bin/activate` before running Python tooling.
