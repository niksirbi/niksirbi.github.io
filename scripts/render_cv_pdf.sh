#!/usr/bin/env bash
# Render cv/cv.qmd to PDF via Typst.
# Called as a pre-render script by Quarto before the main website render.
# Output: build/cv/cv.pdf  (Quarto respects the project output-dir)
#
# Skips compilation if cv/cv.pdf is already newer than cv/cv.qmd, so that
# quarto preview does not re-render the PDF on every unrelated file change.
set -euo pipefail

SOURCE="cv/cv.qmd"
OUTPUT="cv/cv.pdf"

if [ -f "$OUTPUT" ] && [ "$OUTPUT" -nt "$SOURCE" ]; then
    echo "-- CV PDF is up to date, skipping Typst render."
    exit 0
fi

echo "-- Rendering CV to PDF (Typst)..."
quarto render "$SOURCE" --to typst
echo "-- CV PDF rendered successfully."
