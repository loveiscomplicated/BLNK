from google.api_core.client_options import ClientOptions
from google.cloud import documentai
import os
from pdf2image import convert_from_path
from PIL import Image



value = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
print(value)