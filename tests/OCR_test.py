import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from OCR import pdf_to_blanked_pdf


pdf_to_blanked_pdf('./tests/materials/engmath.pdf', 0.25)
print('good')
