#!/usr/bin/env bash
# Render cv/cv.qmd to PDF via Typst.
# Called as a pre-render script by Quarto before the main website render.
# Output: build/cv/cv.pdf  (Quarto respects the project output-dir)
set -euo pipefail

echo "→ Rendering CV to PDF (Typst)..."
quarto render cv/cv.qmd --to typst
echo "✓ CV PDF rendered successfully."
