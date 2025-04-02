import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from OCR import all_in_one
input_file_path = './tests/materials/sample1.pdf'
output_file_path = './tests/output.pdf'
keyword_ratio = 0.000000000001
all_in_one(input_file_path, output_file_path, keyword_ratio)


