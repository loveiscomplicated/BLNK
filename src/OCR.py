import os
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from pdf2image import convert_from_path

# Google cloud console의 Document AI를 이용하여 OCR을 진행할 것입니다.
# 서비스 계정 JSON 파일을 만든 후, 해당 파일의 경로를 GOOGLE_APPLICATION_CREDENTIALS라는 이름으로 저장하세요.

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