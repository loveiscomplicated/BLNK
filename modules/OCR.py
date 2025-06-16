import os
import re
import cv2
import img2pdf
import numpy as np
from PIL import Image
from io import BytesIO
from collections import defaultdict
from google.cloud import documentai
from pdf2image import convert_from_path
from google.api_core.client_options import ClientOptions
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import multiprocessing

import pickle
from . import keyword_extractor
from . import masking_processor 

# Google cloud console의 Document AI를 이용하여 OCR을 진행할 것입니다.
# 서비스 계정 JSON 파일을 만든 후, 해당 파일의 경로를 GOOGLE_APPLICATION_CREDENTIALS라는 이름의 환경 변수로 저장하세요.

def pdf_to_blanked_pdf(file_path, keyword_ratio, output_pdf_path):
    """
    전 과정을 수행하는 함수

    Args:
        file_path (str): 입력 파일 경로
        keyword_ratio: 빈칸 생성 비율
        output_pdf_path: 결과물 저장 경로

    Returns:
        output (pdf): 최종 결과물, return 안 함
    """
    PROJECT_ID = "blnk-445514"
    LOCATION = "us"  # 위치를 'us' 또는 'eu'로 설정
    PROCESSOR_ID = "f95b966bf0fb2004"  # Cloud Console에서 생성된 프로세서 ID

    # Document AI를 사용하여 텍스트와 경계 상자 좌표를 추출
    document_object = pdf(PROJECT_ID, LOCATION, PROCESSOR_ID, file_path)
    print("Document_object 추출 완료")
    
    # PDF를 OpenCV에서 사용할 수 있도록 변환하고,
    # Document AI에서 제공하는 원본 크기와 동일한 크기로 조정.
    image_list = pdf_to_images_with_docai_size(file_path, document_object)
    print("이미지 변환 완료")
    
    # GPT 사용하는 부분
    path = './gpt_api_key.json'
    gpt_api_key = keyword_extractor.load_api_key(path)
    important_words_list = keyword_extractor.gpt_api_call(gpt_api_key, document_object.text, keyword_ratio)
    print("GPT API 호출 완료")
    print(important_words_list)###################3
    
    # 빈칸 생성하는 부분
    coord_dict = masking_processor.get_bounding_bxes_by_page(document_object, important_words_list)
    masking_processor.draw_boxes(image_list, coord_dict, output_pdf_path=output_pdf_path, color=(230, 222, 171), thickness=2)
    print("빈칸 생성 완료")

def pdf(project_id, location, processor_id, file_path):
    """
    Document AI를 사용하여 텍스트와 경계 상자 좌표를 추출하는 함수

    Args:
        project_id (str): Google Cloud 프로젝트 ID
        location (str): Document AI API 위치 (us 또는 eu)
        processor_id (str): Document AI 프로세서 ID
        file_path (str): 입력 파일 경로

    Returns:
        document_object(json): Document AI의 출력물
    """

    # 환경 변수 설정 확인
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS 환경 변수가 설정되지 않았습니다.")
    
    # MIME 타입 설정
    mime_type = 'application/pdf'
    
    # Document AI 클라이언트 초기화
    docai_client = documentai.DocumentProcessorServiceClient(
        client_options=ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    )

    # 프로세서의 전체 리소스 이름 정의
    resource_name = docai_client.processor_path(project_id, location, processor_id)

    # 파일을 메모리에 읽어오기
    with open(file_path, "rb") as image:
        image_content = image.read()

    # Document AI RawDocument 객체로 바이너리 데이터 로드
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

    # 요청 구성
    request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)

    # Document AI 클라이언트를 사용하여 문서를 처리
    result = docai_client.process_document(request=request)

    document_object = result.document
    return document_object


def pdf_to_images_with_docai_size(file_path, document_object):
    """
    PDF를 OpenCV에서 사용할 수 있도록 이미지로 변환하고,
    Document AI에서 제공하는 원본 크기와 동일한 크기로 조정.

    Args:
        file_path (str): 입력 PDF 파일 경로
        document_object: Google Document AI의 분석 결과 객체

    Returns:
        list: Document AI 크기에 맞춰 변환된 OpenCV 이미지 리스트
    """
    # PDF를 이미지(PIL 형식)로 변환
    pil_images = convert_from_path(file_path, dpi=200)

    image_list = []
    for page_number, image in enumerate(pil_images):
        # PIL -> OpenCV 변환
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Document AI의 원본 크기 가져오기
        docai_width = document_object.pages[page_number].dimension.width
        docai_height = document_object.pages[page_number].dimension.height

        # OpenCV로 Document AI 크기에 맞춰 리사이징
        resized_image = cv2.resize(opencv_image, (int(docai_width), int(docai_height)))

        image_list.append(resized_image)

    return image_list    


def save_pdf_with_pages(reader, start, end, output_path):
    writer = PdfWriter()
    for i in range(start, end):
        writer.add_page(reader.pages[i])
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path

def split_pdf_by_size(file_path, output_dir):
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    queue = [(0, total_pages)]  # (start_page, end_page)
    part_files = []
    part_num = 1
    failed_pages = []

    MAX_SIZE = 20_000_000  # 20MB
    MAX_PAGES = 15

    while queue:
        start, end = queue.pop(0)
        temp_output = os.path.join(output_dir, f"part_{part_num}.pdf")
        save_pdf_with_pages(reader, start, end, temp_output)
        size = os.path.getsize(temp_output)

        if size <= MAX_SIZE and (end - start) <= MAX_PAGES:
            print(f"[✔] Saved {temp_output} ({size / 1_000_000:.2f} MB)")
            part_files.append(temp_output)
            part_num += 1
        else:
            os.remove(temp_output)
            if end - start == 1:
                # 더 이상 쪼갤 수 없는 1페이지도 너무 큰 경우
                print(f"[❌] Page {start} is too large to split or process (>{MAX_SIZE / 1_000_000:.1f} MB). Skipping.")
                failed_pages.append(start)
            else:
                print(f"[✘] {temp_output} too big ({size / 1_000_000:.2f} MB), splitting again...")
                mid = (start + end) // 2
                queue.insert(0, (mid, end))
                queue.insert(0, (start, mid))

    if failed_pages:
        print(f"[⚠️] The following pages could not be processed due to size: {failed_pages}")

    return part_files

def delete_files_in_temp_folder(directory_path):
    """temp 폴더 청소하는 함수"""
    try:
        files = os.listdir(directory_path)
        for file in files:
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("All files deleted successfully.")
    except OSError:
        print("Error occurred while deleting files.")
     

# 병렬 처리를 위해 인자를 직접 받아 처리하는 헬퍼 함수로 수정
def _process_single_pdf_part(pdf_file, keyword_ratio_val): # <-- 여기서 인자를 직접 받도록 변경
    temp_result_path = os.path.join('./temp/blanked_splited', os.path.basename(pdf_file)) 
    pdf_to_blanked_pdf(pdf_file, keyword_ratio_val, temp_result_path) 
    return temp_result_path # 처리된 파일 경로 반환

def all_in_one(input_file_path, keyword_ratio, output_file_path): 
    # temp 폴더 없으면 만들기
    os.makedirs('./temp/splited', exist_ok=True) 
    os.makedirs('./temp/blanked_splited', exist_ok=True) 

    # 이미 있는 경우 초기화
    delete_files_in_temp_folder('./temp/splited') 
    delete_files_in_temp_folder('./temp/blanked_splited') 

    # pdf 분할하기
    splited_pdf_list = split_pdf_by_size(input_file_path, './temp/splited') 

    # 병렬 처리를 위한 인자 리스트 생성
    # 각 분할된 PDF 파일과 keyword_ratio를 튜플로 묶음
    tasks = [(pdf_file, keyword_ratio) for pdf_file in splited_pdf_list] 

    # 프로세스 풀 생성 (CPU 코어 수에 맞게 설정하거나 적절한 값으로 조절)
    # 예를 들어, os.cpu_count()를 사용하거나 특정 개수로 제한
    num_processes = multiprocessing.cpu_count() # 사용 가능한 모든 코어 사용
    # num_processes = 4 # 또는 특정 개수로 제한
    print(f"Using {num_processes} processes for parallel processing.") 

    with multiprocessing.Pool(processes=num_processes) as pool: 
        # starmap을 사용하여 각 튜플 인자를 _process_single_pdf_part 함수에 전달
        # 결과로 처리된 파일 경로들의 리스트를 받음
        processed_pdf_paths = pool.starmap(_process_single_pdf_part, tasks) 

    merger = PdfMerger() 

    # 병렬 처리된 결과들을 병합
    for processed_path in processed_pdf_paths: 
        if os.path.exists(processed_path): # 파일이 실제로 존재하는지 확인
            merger.append(processed_path) 
        else: 
            print(f"Warning: Processed file not found: {processed_path}") #

    merger.write(output_file_path) 
    merger.close() 

    print('Parallel processing completed.') 

if __name__ == '__main__': 
    # 이 부분은 테스트 환경에 맞춰 수정하세요.
    all_in_one('./tests/materials/ex_history.pdf', 0.25, './tests/output.pdf') #
    print('good') 