import pdfplumber
from itertools import groupby

def is_bold(fontname: str) -> bool:
    return "Bold" in fontname or fontname.endswith("-BoldMT")

def is_ital(fontname: str) -> bool:
    return "Italic" in fontname or fontname.endswith("-ItalicMT")

def normalize_color(color): # Normalize PDF color representation so grouping is consistent.
    if color is None:
        return "unknown"
    if isinstance(color, (int, float)):
        return "k" if color < 0.1 else "b"
    if isinstance(color, (list, tuple)):
        return "b" if any(c >= 0.1 for c in color) else "k"
    return "unknown"

def identify_level(size, bold, ital, color):
    if size == 12.0:
        return "part"
    elif size == 11.0:
        return "chapter"
    elif size == 10.0:
        if bold and (not ital) and color == "b":
            return "section"
        else:
            return "body"
    else:
        return "ignore"

def extract_structure(pdf_path: str):
    sections = []
    current: dict | None = None

    with pdfplumber.open(pdf_path) as pdf:

        for page_num, page in enumerate(pdf.pages):

            words = page.extract_words(extra_attrs=["fontname", "size", "non_stroking_color"])

            # Group consecutive words sharing same style signature
            for (size, bold, ital, color), group in groupby(
                words,
                key=lambda w: (
                    round(w["size"], 1),
                    is_bold(w["fontname"]), is_ital(w["fontname"]),
                    normalize_color(w.get("non_stroking_color")),
                ),
            ):

                text = " ".join(w["text"] for w in group).strip()
                level = identify_level(size, bold, ital, color)

                if level == "part":          # top-level heading
                    if current:
                        sections.append(current)
                    current = {"level": "part", "heading": text, "body": "", "page": page_num + 1}

                elif level == "chapter":     # mid-level heading
                    if current:
                        sections.append(current)
                    current = {"level": "chapter", "heading": text, "body": "", "page": page_num + 1}

                elif level == "section":     # low-level heading
                    if current:
                        sections.append(current)
                    current = {"level": "section", "heading": text, "body": "", "page": page_num + 1}
                
                elif level == "ignore":      # citations etc (skip)
                    continue

                else:                        # body text
                    if current is None:
                        current = {"level": "body", "heading": "", "body": "", "page": page_num + 1}
                    current["body"] += text + " "

    if current:
        sections.append(current)
    return sections