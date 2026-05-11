import pdfplumber
from itertools import groupby

# Font size → hierarchy level (no regex, purely from PDF metadata)
SIZE_TO_LEVEL = {
    12.0: "rule",     # Arial-BoldMT  e.g. "RULE 1 THE FIELD"
    10.0: "section",  # Arial-BoldMT  e.g. "SECTION 1 DIMENSIONS"
    9.0:  None,       # Bold → article heading; regular → body text
}

def is_bold(fontname: str) -> bool:
    return "Bold" in fontname or fontname.endswith("-BoldMT")

def extract_structure(pdf_path: str):
    sections = []
    current: dict | None = None

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            
            words = page.extract_words(extra_attrs=["fontname", "size"])
            # Group consecutive words that share the same (size, bold) signature
            
            for (size, bold), group in groupby(
                words, key=lambda w: (round(w["size"], 1), is_bold(w["fontname"]))
            ):
                text = " ".join(w["text"] for w in group).strip()
                if not text:
                    continue

                level = SIZE_TO_LEVEL.get(size)

                if level == "rule":          # top-level heading
                    if current:
                        sections.append(current)
                    current = {"level": "rule", "heading": text, "body": [], "page": page_num + 1}

                elif level == "section":     # mid-level heading
                    if current:
                        sections.append(current)
                    current = {"level": "section", "heading": text, "body": [], "page": page_num + 1}

                elif level is None and bold: # article heading (size 9, bold)
                    if current:
                        sections.append(current)
                    current = {"level": "article", "heading": text, "body": [], "page": page_num + 1}

                else:                        # body text
                    if current is None:
                        current = {"level": "body", "heading": "", "body": [], "page": page_num + 1}
                    current["body"].append(text)

    if current:
        sections.append(current)
    return sections
