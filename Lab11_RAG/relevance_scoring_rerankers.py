import pdfplumber
from itertools import groupby

from lab11_functions import *

pdf_path = "Lab11/test_pdf.pdf"

sections = extract_structure(pdf_path)

print(sections)