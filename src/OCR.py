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

import GPT_important_words
import draw_blank

# Google cloud console의 Document AI를 이용하여 OCR을 진행할 것입니다.
# 서비스 계정 JSON 파일을 만든 후, 해당 파일의 경로를 GOOGLE_APPLICATION_CREDENTIALS라는 이름으로 저장하세요.

def pdf_to_blanked_pdf(file_path, keyword_ratio):
    """
    OCR 전 과정을 수행하는 함수

    Args:
        project_id (str): Google Cloud 프로젝트 ID
        location (str): Document AI API 위치 (us 또는 eu)
        processor_id (str): Document AI 프로세서 ID
        file_path (str): 입력 파일 경로

    Returns:
        output (pdf): 최종 결과물
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
    path = './tests/materials/gpt_api_key.json'
    gpt_api_key = GPT_important_words.load_api_key(path)
    important_words_list = GPT_important_words.gpt_api_call(gpt_api_key, document_object.text, keyword_ratio)
    print("GPT API 호출 완료")
    
    # 빈칸 생성하는 부분
    coord_dict = draw_blank.get_bounding_bxes_by_page(document_object, important_words_list)
    draw_blank.draw_boxes(image_list, coord_dict, output_pdf_path="./tests/materials/output.pdf", color=(0, 255, 0), thickness=2)
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
    PDF를 OpenCV에서 사용할 수 있도록 변환하고,
    Document AI에서 제공하는 원본 크기와 동일한 크기로 조정.

    Args:
        file_path (str): 입력 PDF 파일 경로
        document_object: Google Document AI의 분석 결과 객체

    Returns:
        list: Document AI 크기에 맞춰 변환된 OpenCV 이미지 리스트
    """
    # PDF를 이미지(PIL 형식)로 변환
    pil_images = convert_from_path(file_path, dpi=300)

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



if __name__ == '__main__':
    pdf_to_blanked_pdf('./tests/materials/engmath.pdf', 0.25)
    print('good')
