from google.api_core.client_options import ClientOptions
from google.cloud import documentai
import os
from pdf2image import convert_from_path
from PIL import Image



def get_mime_type(file_path):
    """
    파일 확장자를 기반으로 MIME 타입 반환

    Args:
        file_path (str): 입력 파일 경로

    Returns:
        str: MIME 타입
    """
    file_path = file_path.lower()
    if file_path.endswith('.pdf'):
        return "application/pdf"
    elif file_path.endswith(('.jpeg', '.jpg')):
        return "image/jpeg"
    elif file_path.endswith('.png'):
        return "image/png"
    elif file_path.endswith(('.tiff', '.tif')):
        return "image/tiff"
    elif file_path.endswith('.bmp'):
        return "image/bmp"
    elif file_path.endswith('.gif'):
        return "image/gif"
    elif file_path.endswith('.webp'):
        return "image/webp"
    else:
        raise ValueError(f"지원되지 않는 파일 형식입니다: {file_path}")

def image(project_id, location, processor_id, file_path):
    """
    Document AI를 사용하여 텍스트와 경계 상자 좌표를 추출하는 함수

    Args:
        project_id (str): Google Cloud 프로젝트 ID
        location (str): Document AI API 위치 (us 또는 eu)
        processor_id (str): Document AI 프로세서 ID
        file_path (str): 입력 파일 경로
        mime_type (str): 파일의 MIME 타입 (예: application/pdf)

    Returns:
        tuple: 추출된 전체 텍스트(str)와 텍스트와 좌표 데이터를 포함한 리스트(list)
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/LG/miniconda3/envs/BLNK/codes/blnk-445514-ac4be237a9a9.json"
    # MIME 타입 가져오기
    mime_type = get_mime_type(file_path)
    
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
    print("문서 처리가 완료되었습니다.")

    # 텍스트와 경계 상자 좌표 추출 (단어 기준)
    extracted_text = document_object.text
    extracted_data = []
    for page in document_object.pages:
        for token in page.tokens:  # 단어(token) 단위로 접근
            # text_anchor를 사용하여 텍스트 추출
            text_segments = token.layout.text_anchor.text_segments
            if text_segments:
                text_start = text_segments[0].start_index
                text_end = text_segments[0].end_index
                text = document_object.text[text_start:text_end]  # 텍스트 추출

                # 경계 상자 추출
                bounding_poly = token.layout.bounding_poly  # 경계 상자
                coordinates = [(vertex.x, vertex.y) for vertex in bounding_poly.normalized_vertices]  # 좌표 계산

                extracted_data.append({
                    "text": text,
                    "coordinates": coordinates,
                    "page_number": page.page_number  # 페이지 번호 추가
                })

    image_list = convert_from_path(file_path, dpi=300)
    return extracted_text, extracted_data, image_list

def pdf(project_id, location, processor_id, file_path):
    """
    Document AI를 사용하여 텍스트와 경계 상자 좌표를 추출하는 함수

    Args:
        project_id (str): Google Cloud 프로젝트 ID
        location (str): Document AI API 위치 (us 또는 eu)
        processor_id (str): Document AI 프로세서 ID
        file_path (str): 입력 파일 경로

    Returns:
        tuple: 추출된 전체 텍스트(str)와 텍스트와 좌표 데이터를 포함한 리스트(list)
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/LG/miniconda3/envs/BLNK/codes/blnk-445514-ac4be237a9a9.json"
    # MIME 타입 가져오기
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
    print("문서 처리가 완료되었습니다.")

    # 텍스트와 경계 상자 좌표 추출 (단어 기준)
    extracted_text = document_object.text
    extracted_data = []
    for page in document_object.pages:
        for token in page.tokens:  # 단어(token) 단위로 접근
            # text_anchor를 사용하여 텍스트 추출
            text_segments = token.layout.text_anchor.text_segments
            if text_segments:
                text_start = text_segments[0].start_index
                text_end = text_segments[0].end_index
                text = document_object.text[text_start:text_end]  # 텍스트 추출

                # 경계 상자 추출
                bounding_poly = token.layout.bounding_poly  # 경계 상자
                coordinates = [(vertex.x, vertex.y) for vertex in bounding_poly.normalized_vertices]  # 좌표 계산

                extracted_data.append({
                    "text": text,
                    "coordinates": coordinates,
                    "page_number": page.page_number  # 페이지 번호 추가
                })

    image_list = convert_from_path(file_path, dpi=300)
    return extracted_text, extracted_data, image_list

def dynamic_split_pdf(file_path, max_size_mb=20):
    """
    PDF 파일을 동적으로 분할하여 최대 용량에 근접하도록 조정.
    초과된 배치는 재분할.

    Args:
        file_path (str): 입력 PDF 파일 경로
        max_size_mb (int): 최대 허용 파일 크기 (MB)

    Returns:
        list: 분할된 PDF 파일 경로 리스트
    """
    from PyPDF2 import PdfReader, PdfWriter
    import os

    def split_batch(file_path, start_page, end_page, batch_number):
        """
        지정된 페이지 범위를 새로운 PDF 파일로 저장.

        Args:
            file_path (str): 원본 PDF 파일 경로
            start_page (int): 시작 페이지
            end_page (int): 종료 페이지
            batch_number (int): 배치 번호

        Returns:
            str: 저장된 파일 경로
        """
        reader = PdfReader(file_path)
        writer = PdfWriter()

        for page_index in range(start_page, end_page):
            writer.add_page(reader.pages[page_index])

        part_file_path = f"{file_path}_part{batch_number}.pdf"
        with open(part_file_path, "wb") as output_pdf:
            writer.write(output_pdf)

        return part_file_path

    # 파일 크기 및 페이지 수 확인
    total_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)

    # 평균 페이지 크기 추정
    avg_page_size_mb = total_size_mb / total_pages
    pages_per_split = min(int(max_size_mb / avg_page_size_mb), 15)


    # 초기 분할 및 저장
    output_files = []
    batch_number = 1
    for start_page in range(0, total_pages, pages_per_split):
        end_page = min(start_page + pages_per_split, total_pages)
        part_file_path = split_batch(file_path, start_page, end_page, batch_number)
        output_files.append(part_file_path)
        batch_number += 1

    # 초과된 배치 확인 및 재분할
    final_output_files = []
    for file in output_files:
        while True:
            part_size_mb = os.path.getsize(file) / (1024 * 1024)
            if part_size_mb <= max_size_mb:
                final_output_files.append(file)
                break  # 크기가 적합하면 종료

            # 배치를 다시 둘로 나눔
            print(f"파일 크기 초과: {file} ({part_size_mb:.2f}MB). 재분할 진행 중...")
            temp_reader = PdfReader(file)
            total_batch_pages = len(temp_reader.pages)
            mid_page = total_batch_pages // 2

            # 앞쪽 분할
            file_1 = split_batch(file, 0, mid_page, batch_number)
            batch_number += 1

            # 뒤쪽 분할
            file_2 = split_batch(file, mid_page, total_batch_pages, batch_number)
            batch_number += 1

            # 기존 파일 삭제 후 새로운 분할 파일로 교체
            os.remove(file)
            output_files.extend([file_1, file_2])
            break  # 처리 완료 후 루프 종료

    return final_output_files



if __name__ == '__main__':
    # 함수 호출 예시
    PROJECT_ID = "blnk-445514"
    LOCATION = "us"  # 위치를 'us' 또는 'eu'로 설정
    PROCESSOR_ID = "f95b966bf0fb2004"  # Cloud Console에서 생성된 프로세서 ID
    FILE_PATH = "C:/Users/LG/miniconda3/envs/BLNK/codes/check/ocr_removed.pdf"


    extracted_text, extracted_data, image_list = process_document_and_extract_data(PROJECT_ID, LOCATION, PROCESSOR_ID, FILE_PATH)

    # 추출된 데이터 출력
    #for data in extracted_data:
    #    print(f"텍스트: {data['text']}")
    #    print(f"좌표: {data['coordinates']}")
    #    print("-" * 50)
    
    print(extracted_data)
    print(extracted_text)
    
    import GPT_important_words
    path = 'C:/Users/LG/miniconda3/envs/BLNK/codes/gpt_api_key.json'
    gpt_api_key = GPT_important_words.load_api_key(path)
    keyword_ratio = 0.2  # 키워드 비율 설정
    important_words_list = GPT_important_words.gpt_api_call(gpt_api_key, extracted_text, keyword_ratio)
    
    print(important_words_list)
    
    import coordinates
    coordinates = coordinates.find_coordinates_with_relative(extracted_data, important_words_list, image_list)
    print(coordinates)
    
    import pickle
    coordinates_path = 'C:/Users/LG/miniconda3/envs/BLNK/codes/check/output/ocr_removed_coordinates.pkl'
    extracted_data_path = 'C:/Users/LG/miniconda3/envs/BLNK/codes/check/output/ocr_removed_extracted_data.pkl'
    important_words_list_path = 'C:/Users/LG/miniconda3/envs/BLNK/codes/check/output/ocr_removed_important_words_list.pkl'
    image_list_path = 'C:/Users/LG/miniconda3/envs/BLNK/codes/check/output/ocr_removed_image_list.pkl'
    
    with open(extracted_data_path, 'wb') as f:
        pickle.dump(extracted_data, f)
        print('저장 완료')
        
    with open(important_words_list_path, 'wb') as f:
        pickle.dump(important_words_list, f)
        print('저장 완료')
    
    with open(image_list_path, 'wb') as f:
        pickle.dump(image_list, f)
        print('저장 완료')
    
    with open(coordinates_path, 'wb') as f:
        pickle.dump(coordinates, f)
        print('저장 완료')
    
