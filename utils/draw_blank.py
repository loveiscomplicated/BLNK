import os
import re
import cv2
import img2pdf
import numpy as np
from PIL import Image
from io import BytesIO
from collections import defaultdict



def find_tokens_in_range(document_object, start_index, end_index):
    """
    특정 시작~끝 인덱스에 포함되는 모든 토큰을 검색하는 함수.

    Args:
        document_object: Google Document AI의 OCR 결과 객체
        start_index (int): 검색할 시작 인덱스
        end_index (int): 검색할 끝 인덱스

    Returns:
        list: 조건을 만족하는 토큰 목록 (딕셔너리 형태로 반환)
    """
    matched_tokens = []

    for page in document_object.pages:
        for token in page.tokens:
            # 토큰이 text_anchor.text_segments를 가지고 있는지 확인
            if not token.layout.text_anchor.text_segments:
                continue  # text_segments가 없는 경우 건너뜀

            # 현재 토큰의 시작/끝 인덱스 가져오기
            token_start = token.layout.text_anchor.text_segments[0].start_index
            token_end = token.layout.text_anchor.text_segments[0].end_index

            # ✅ 토큰이 범위 내에 포함되는지 확인
            if token_start < end_index and token_end > start_index:
                # OpenCV 호환 가능한 bounding_box 좌표 변환
                bounding_box = [(vertex.x, vertex.y) for vertex in token.layout.bounding_poly.vertices]

                matched_tokens.append({
                    "text": document_object.text[token_start:token_end],  # 실제 텍스트
                    "start_index": token_start,
                    "end_indoex": token_end,
                    "page_number": page.page_number,
                    "bounding_box": bounding_box  # ✅ OpenCV 호환 좌표 저장
                })

    return matched_tokens

def find_word_indices(full_text, words):
    """
    주어진 full_text에서 특정 단어 리스트에 포함된 단어들의 시작 및 끝 인덱스를 찾는 함수.

    Args:
        full_text (str): 검색할 전체 텍스트
        words (list of str): 검색할 단어 리스트

    Returns:
        list of dict: 단어와 해당 위치 정보 리스트
            - {"word": 단어, "start_index": 시작 인덱스, "end_index": 끝 인덱스}
    """
    matched_indices = []

    for word in words:
        # 단어가 full_text에서 여러 번 등장할 수 있으므로 finditer 사용
        for match in re.finditer(re.escape(word), full_text):
            matched_indices.append({
                "word": word,
                "start_index": match.start(),
                "end_index": match.end()
            })

    return matched_indices


def get_bounding_bxes_by_page(document_object, words):
    """
    Google Document AI OCR 결과에서 특정 단어들의 바운딩 박스를 페이지별로 그룹화하여 반환하는 함수.

    Args:
        document_object: Google Document AI OCR 결과 객체
        words (list of str): 검색할 단어 리스트

    Returns:
        dict: 페이지별 바운딩 박스 list
            - {
                page_number: [
                    [(좌표), (좌표), ...]
                ]
            }
    """
    # 전체 텍스트 document_object에서 가져오기
    full_text = document_object.text

    # 1️⃣ OCR 전체 텍스트에서 단어 위치 찾기
    word_indices = find_word_indices(full_text, words)

    # 2️⃣ 페이지별 바운딩 박스 저장할 딕셔너리
    page_bounding_boxes = defaultdict(list)

    # 3️⃣ 찾은 단어 위치에 대해 바운딩 박스 검색
    for word_info in word_indices:
        word = word_info["word"]
        start_index = word_info["start_index"]
        end_index = word_info["end_index"]

        # 해당 범위 내 OCR 토큰 찾기
        matched_tokens = find_tokens_in_range(document_object, start_index, end_index)

        # 바운딩 박스를 페이지별로 저장
        for token in matched_tokens:
            page_number = token["page_number"]
            bounding_box = token["bounding_box"]

            page_bounding_boxes[page_number].append(bounding_box)

    return dict(page_bounding_boxes) # coord_dict


def draw_boxes(image_list, coord_dict, output_pdf_path="./tests/materials/output.pdf", color=(0, 255, 0), thickness=2):
    """
    바운딩 박스를 이미지에 그린 후, 고품질로 PDF 저장하는 함수.
    - `coord_dict`의 키(페이지 번호)를 정렬하여 PDF 페이지 순서 유지.

    Args:
        image_list (list of np.array): 원본 이미지 리스트 (페이지별 이미지)
        coord_dict (dict): 페이지별 바운딩 박스 좌표 딕셔너리 (정렬되지 않은 상태)
            - {page_number: [[(x1, y1), (x2, y2), (x3, y3), (x4, y4)], ...]}
        output_pdf_path (str): 저장할 PDF 파일 경로 (기본값: "./tests/materials/output.pdf")
        color (tuple): 바운딩 박스 색상 (기본값 초록색 - BGR기준)
        thickness (int): 바운딩 박스 두께 (기본값: 2)
    
    Returns:
        None (PDF 파일이 저장됨)
    """
    processed_images = []  # 바운딩 박스를 그린 이미지 저장 리스트

    # 🔹 페이지 번호를 정렬하여 올바른 순서 유지
    for page_number in sorted(coord_dict.keys()):  # ✅ 페이지 정렬 추가
        bounding_boxes = coord_dict[page_number]
        image = image_list[page_number - 1].copy()  # 원본 이미지 복사

        # 바운딩 박스 그리기
        for box in bounding_boxes:
            pts = np.array(box, dtype=np.int32)
            # 이 부분을 조정하여 바운딩 박스의 색과 채우기를 바꿀 수 있음
            cv2.fillPoly(image, [pts], color = color)
            #cv2.polylines(image, [pts], isClosed=True, color=color, thickness=thickness)

        # OpenCV 이미지를 PIL로 변환 (RGB 모드)
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # PNG (무손실) 포맷으로 저장
        img_bytes = BytesIO()
        image_pil.save(img_bytes, format="PNG", dpi=(300, 300))  # 🔹 300 DPI 설정
        processed_images.append(img_bytes.getvalue())

    # PDF로 저장 (고품질 유지, 페이지 순서 정렬 완료)
    save_images_as_pdf(processed_images, output_pdf_path)


def save_images_as_pdf(image_list, output_pdf_path):
    """
    이미지 리스트를 PDF로 변환하여 저장하는 함수 (고해상도 유지).

    Args:
        image_list (list of bytes): PNG 이미지 바이너리 리스트
        output_pdf_path (str): 저장할 PDF 파일 경로
    
    Returns:
        None (PDF 파일이 저장됨)
    """
    pdf_bytes = img2pdf.convert(image_list)  # 🔹 무손실 PDF 변환

    # PDF 파일 저장
    with open(output_pdf_path, "wb") as f:
        f.write(pdf_bytes)


