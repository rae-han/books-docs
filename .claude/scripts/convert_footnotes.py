#!/usr/bin/env python3
"""
Convert <sub> footnotes to inline italic format.

Handles:
1. term(English) — explanation  →  (*English — explanation*)
2. term(English) -- explanation →  (*English — explanation*)
3. term — explanation           →  (*term — explanation*)
4. term -- explanation          →  (*term — explanation*)
5. Explanatory notes (no separator) → (*explanation*)
6. Figure captions: <sub>그림 X.Y — caption</sub> → *그림 X.Y — caption*
"""
import re
import os
import glob

SUPER_CHARS = '¹²³⁴⁵⁶⁷⁸⁹⁰'
DASH_PATTERN = r'(?:—|--)'
DOCS_DIR = '/Users/raehan/Documents/personal/docs'

BOOK_DIRS = [
    'clean-code',
    'clean-architecture',
    'the-clean-coder',
    'structure-and-interpretation-of-computer-programs-javascript',
    'unit-testing',
    'test-driven-development-by-example',
]


def parse_footnote(sub_content):
    """Parse text inside a <sub> tag. Returns dict or None."""
    text = sub_content.strip()

    # Figure caption: starts with "그림" (no superscript number)
    if re.match(r'그림\s+\d+', text):
        return {'type': 'figure', 'caption': text}

    # Must start with superscript number
    num_match = re.match(r'([' + SUPER_CHARS + r']+)\s+(.+)', text)
    if not num_match:
        return None

    sup_num = num_match.group(1)
    footnote_text = num_match.group(2)

    # Pattern 1: term(English) —/-- explanation
    paren_match = re.match(r'(.+?)\(([^)]+)\)\s*' + DASH_PATTERN + r'\s*(.+)', footnote_text)
    if paren_match:
        english = paren_match.group(2).strip()
        explanation = paren_match.group(3).strip()
        inline = f'(*{english} — {explanation}*)'
        return {'type': 'footnote', 'num': sup_num, 'inline': inline}

    # Pattern 2: term —/-- explanation
    dash_match = re.match(r'(.+?)\s*' + DASH_PATTERN + r'\s*(.+)', footnote_text)
    if dash_match:
        term = dash_match.group(1).strip()
        explanation = dash_match.group(2).strip()
        inline = f'(*{term} — {explanation}*)'
        return {'type': 'footnote', 'num': sup_num, 'inline': inline}

    # Pattern 3: Just explanatory text (no separator)
    inline = f'(*{footnote_text}*)'
    return {'type': 'footnote', 'num': sup_num, 'inline': inline}


def process_file(filepath):
    """Process a single file. Returns (changed, warnings)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    lines = content.split('\n')
    warnings = []

    # Find all lines with <sub> tags and parse
    sub_line_indices = set()
    footnotes = []      # (line_idx, parsed) for numbered footnotes
    figure_lines = {}   # line_idx -> caption text for figure captions

    for i, line in enumerate(lines):
        for m in re.finditer(r'<sub>([^<]+)</sub>', line):
            parsed = parse_footnote(m.group(1))
            if parsed is None:
                warnings.append(f"Could not parse at line {i+1}: {m.group(0)[:80]}")
                continue
            sub_line_indices.add(i)
            if parsed['type'] == 'figure':
                figure_lines[i] = parsed['caption']
            else:
                footnotes.append((i, parsed))

    if not footnotes and not figure_lines:
        return False, warnings

    # Replace numbered footnotes: find body reference and insert inline
    for fn_line_idx, fn in footnotes:
        sup_num = fn['num']
        inline = fn['inline']

        found = False
        for i in range(fn_line_idx - 1, -1, -1):
            if i in sub_line_indices:
                continue
            if sup_num in lines[i]:
                pos = lines[i].rfind(sup_num)
                lines[i] = lines[i][:pos] + inline + lines[i][pos + len(sup_num):]
                found = True
                break

        if not found:
            warnings.append(f"No body reference for {sup_num} near line {fn_line_idx+1}")

    # Build new lines: remove <sub> lines or convert figure captions
    new_lines = []
    for i, line in enumerate(lines):
        if i in sub_line_indices:
            if i in figure_lines:
                # Convert figure caption to italic
                caption = figure_lines[i]
                new_lines.append(f'*{caption}*')
            else:
                # Remove footnote line (check if line has other content)
                cleaned = re.sub(r'<sub>[^<]+</sub>', '', line)
                cleaned = re.sub(r'<br\s*/?>', '', cleaned)
                cleaned = cleaned.strip()
                if not cleaned:
                    continue  # Skip line entirely
                else:
                    line = re.sub(r'\s*<sub>[^<]+</sub>(<br\s*/?>)?', '', line)
                    new_lines.append(line)
        else:
            new_lines.append(line)

    content = '\n'.join(new_lines)
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.rstrip('\n') + '\n'

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, warnings

    return False, warnings


def main():
    total_changed = 0
    all_warnings = []

    for book_dir in BOOK_DIRS:
        dir_path = os.path.join(DOCS_DIR, book_dir)
        if not os.path.isdir(dir_path):
            continue

        md_files = sorted(glob.glob(os.path.join(dir_path, '*.md')))
        dir_changed = 0

        for filepath in md_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                if '<sub>' not in f.read():
                    continue

            relpath = os.path.relpath(filepath, DOCS_DIR)
            changed, warnings = process_file(filepath)

            if changed:
                print(f"  ✓ {relpath}")
                dir_changed += 1
                total_changed += 1

            for w in warnings:
                print(f"  ⚠ {relpath}: {w}")
                all_warnings.append((relpath, w))

        if dir_changed > 0:
            print(f"  [{book_dir}] {dir_changed} files changed\n")

    print(f"Done: {total_changed} files changed, {len(all_warnings)} warnings")
    if all_warnings:
        print("\nWarnings:")
        for path, w in all_warnings:
            print(f"  {path}: {w}")


if __name__ == '__main__':
    main()
