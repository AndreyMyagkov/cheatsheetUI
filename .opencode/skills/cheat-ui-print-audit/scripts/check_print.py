"""Render an HTML cheatsheet to PDF and report A4 pagination diagnostics.

Usage:
    python check_print.py vitest_cheatsheet.html out.pdf
    python check_print.py sheet.html out.pdf --png shots --theme dark
    python check_print.py sheet.html out.pdf --expect-pages 4

Requires Chrome and PyMuPDF (import pymupdf).
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", help="local HTML file or http(s)/file URL")
    parser.add_argument("pdf", help="output PDF path")
    parser.add_argument("--chrome", default=DEFAULT_CHROME)
    parser.add_argument("--theme", choices=["paper", "vivid", "muted", "dark"],
                        help="render a temporary copy with this data-theme")
    parser.add_argument("--png", help="directory to also render page PNGs")
    parser.add_argument("--expect-pages", type=int,
                        help="fail if the PDF has a different page count")
    return parser.parse_args()


def count_sheets(source):
    """Count elements whose class list contains exactly `sheet`."""
    return sum(
        1
        for match in re.finditer(r'class="([^"]*)"', source)
        if "sheet" in match.group(1).split()
    )


def with_theme(source, theme):
    """Inject data-theme into the <html> tag of a temporary local copy."""
    def replace(match):
        tag = match.group(0)
        tag = re.sub(r'\s+data-theme="[^"]*"', "", tag)
        attr = "" if theme == "paper" else f' data-theme="{theme}"'
        return tag[:-1].rstrip() + attr + ">"

    return re.sub(r"<html\b[^>]*>", replace, source, count=1)


def to_url(value):
    if re.match(r"^(https?|file)://", value, re.I):
        return value
    return Path(value).resolve().as_uri()


def render(html_arg, pdf_path, chrome, theme):
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    if pdf_path.exists():
        pdf_path.unlink()  # never report a stale PDF as success

    source = None
    audit_copy = None
    if Path(html_arg).is_file():
        source = Path(html_arg).read_text(encoding="utf-8")

    url = to_url(html_arg)
    if theme and source is not None:
        themed = with_theme(source, theme)
        audit_copy = Path(html_arg).with_name(f"_audit-{theme}.html")
        audit_copy.write_text(themed, encoding="utf-8")
        url = to_url(str(audit_copy))

    try:
        with tempfile.TemporaryDirectory(prefix="cheat-audit-") as profile:
            cmd = [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                f"--user-data-dir={profile}",
                "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_path}",
                url,
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
    finally:
        if audit_copy is not None:
            audit_copy.unlink(missing_ok=True)

    if not pdf_path.exists():
        print("Chrome did not create the PDF.", file=sys.stderr)
        print((proc.stderr or "").strip()[-1500:], file=sys.stderr)
        sys.exit(2)

    return source


def report(doc, png_dir):
    if png_dir:
        Path(png_dir).mkdir(parents=True, exist_ok=True)

    print(f"pages: {doc.page_count}")
    problems = []

    for index, page in enumerate(doc):
        height = page.rect.height
        blocks = [b for b in page.get_text("blocks") if b[4].strip()]
        footer = [b for b in blocks if b[1] > height - 85]
        body = [b for b in blocks if b not in footer]

        left = [b[3] for b in body if (b[0] + b[2]) / 2 < page.rect.width / 2]
        right = [b[3] for b in body if (b[0] + b[2]) / 2 >= page.rect.width / 2]
        footer_top = min((b[1] for b in footer), default=None)

        print(
            f"page {index + 1}: "
            f"top={round(min((b[1] for b in blocks), default=0), 1)} "
            f"L={round(max(left), 1) if left else '-'} "
            f"R={round(max(right), 1) if right else '-'} "
            f"footer={[round(b[3], 1) for b in footer]}"
        )

        if footer_top is not None:
            below = [b for b in body if b[3] > footer_top - 2]
            if below:
                problems.append(
                    f"page {index + 1}: content overlaps the footer zone"
                )

        text = [b[4].strip().replace("\n", " ") for b in sorted(body, key=lambda b: b[1])]
        if text:
            print(f"  first: {text[0][:70]}")
            print(f"  last:  {text[-1][:70]}")

        if png_dir:
            out = Path(png_dir) / f"page-{index + 1}.png"
            page.get_pixmap(dpi=120).save(out)
            print(f"  png:   {out}")

    for problem in problems:
        print("WARN:", problem)


def main():
    args = parse_args()
    pdf_path = Path(args.pdf)
    if pymupdf is None:
        sys.exit("PyMuPDF is required: python -m pip install pymupdf")

    source = render(args.html, pdf_path, args.chrome, args.theme)
    doc = pymupdf.open(pdf_path)
    report(doc, args.png)

    if source is not None:
        sheets = count_sheets(source)
        print(f"sheets in HTML: {sheets}")
        if sheets and sheets != doc.page_count:
            print(f"WARN: expected {sheets} pages, got {doc.page_count}")
        if args.expect_pages is not None and args.expect_pages != doc.page_count:
            sys.exit(3)
        if sheets and sheets != doc.page_count:
            sys.exit(3)


if __name__ == "__main__":
    main()
