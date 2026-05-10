#!/usr/bin/env python3
"""check_unicode_gremlins.py

Check source files for problematic non-ASCII typographic characters that
should be written as ASCII equivalents (per the Unicode / Gremlins policy
documented in AGENTS.md).

Proper nouns with diacritics (e.g. Goettingen) are intentionally allowed --
only "gremlin" typographic substitutions are flagged.

Usage (called automatically by pre-commit):
    python scripts/check_unicode_gremlins.py <file> [<file> ...]

Inline suppression: add  # unicode-ok  at the end of a line to skip it.

Exit codes: 0 = clean, 1 = gremlins found.
"""

import sys

# Maps Unicode code point -> (character name, suggested ASCII replacement).
GREMLINS: dict[int, tuple[str, str]] = {
    0x2013: ("en dash", "--"),
    0x2014: ("em dash", "---"),
    0x2026: ("ellipsis", "..."),
    0x201C: ("left double quote", '"'),
    0x201D: ("right double quote", '"'),
    0x2018: ("left single quote", "'"),
    0x2019: ("right single quote", "'"),
    0x00B7: ("middle dot", "| or -"),
    0x00A0: ("non-breaking space", "<regular space>"),
    0x200B: ("zero-width space", "<delete>"),
    0xFEFF: ("BOM", "<delete>"),
}

# Box-drawing characters U+2500 -- U+257F
for _cp in range(0x2500, 0x2580):
    GREMLINS[_cp] = ("box-drawing char", "-")


def check_file(path: str) -> list[tuple[int, int, str, str, str]]:
    """Return list of (line, col, char, name, suggestion) for each gremlin."""
    issues: list[tuple[int, int, str, str, str]] = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except (OSError, IsADirectoryError):
        return issues

    for line_num, line in enumerate(text.splitlines(), start=1):
        if line.rstrip().endswith("# unicode-ok"):
            continue
        for col_num, ch in enumerate(line, start=1):
            cp = ord(ch)
            if cp in GREMLINS:
                name, suggestion = GREMLINS[cp]
                issues.append((line_num, col_num, ch, name, suggestion))

    return issues


def main() -> int:
    files = sys.argv[1:]
    found_any = False

    for path in files:
        issues = check_file(path)
        if not issues:
            continue
        found_any = True
        print(f"\n{path}:")
        for line_num, col_num, ch, name, suggestion in issues:
            print(
                f"  line {line_num:>4}, col {col_num:>3}: "
                f"U+{ord(ch):04X} {name!r:<26} -> use {suggestion!r}"
            )

    if found_any:
        print(
            "\nUnicode gremlins found in source files.\n"
            "Replace them with their ASCII equivalents (listed above).\n"
            "See the 'Unicode / Gremlins' section in AGENTS.md for guidance.\n"
            "To suppress a single line, append  # unicode-ok  to it."
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
