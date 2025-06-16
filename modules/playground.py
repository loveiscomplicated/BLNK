import json
import openai
import re
from collections import Counter
from pdf2image import convert_from_path
import time

print("start")
file_path_1 = './tests/materials/CH16-Node.pdf'
start_time = time.time()
pil_images = convert_from_path(file_path_1, dpi=200)
end_time = time.time()
execution_time = end_time - start_time
print(f"코드 실행 시간: {execution_time:.2f} 초")