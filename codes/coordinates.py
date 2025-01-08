import re
from collections import defaultdict

def merge_coordinates(coordinate_list):
    """
    겹치거나 인접한 좌표를 병합하는 함수
    """
    if not coordinate_list:
        return []

    # 좌표를 정렬 (좌상단 기준)
    coordinate_list = sorted(coordinate_list, key=lambda x: (x[0], x[1]))

    merged = [coordinate_list[0]]
    for current in coordinate_list[1:]:
        last = merged[-1]

        # 현재 좌표가 이전 좌표와 겹치거나 인접하면 병합
        if current[0] <= last[2] and current[1] <= last[3]:  # x축, y축 기준으로 병합
            merged[-1] = [
                min(last[0], current[0]),  # x1
                min(last[1], current[1]),  # y1
                max(last[2], current[2]),  # x2
                max(last[3], current[3]),  # y2
            ]
        else:
            merged.append(current)

    return merged


def find_coordinates_regex(ocr_results, important_words_list):
    matched_coordinates = defaultdict(list)
    combined_text = "".join([entry['text'].replace(" ", "") for entry in ocr_results])

    for keyword in important_words_list:
        keyword_normalized = keyword.replace(" ", "")

        # re.escape(keyword_normalized)를 사용해서 키워드 안의 특수문자도 문자 그대로 검색할 수 있도록 처리
        pattern = re.escape(keyword_normalized)

        # 문자열 안에서 해당 키워드가 등장하는 모든 인덱스를 찾음
        for match in re.finditer(pattern, combined_text):
            start_idx = match.start()
            end_idx = match.end()

            # OCR 결과를 순회하여 구간 매칭
            cumulative_length = 0  # 각 entry_text의 시작 위치를 추적
            keyword_coordinates = []  # 키워드와 매칭된 좌표 수집
            for entry in ocr_results:
                entry_text = entry['text'].replace(" ", "")
                entry_length = len(entry_text)

                # 구간 비교: 키워드 매칭 영역이 entry_text의 위치와 겹치는지 확인
                if start_idx < cumulative_length + entry_length and end_idx > cumulative_length:
                    keyword_coordinates.append(entry['coordinates'])

                # cumulative_length 업데이트
                cumulative_length += entry_length

            # 좌표 병합 후 저장
            if keyword_coordinates:
                matched_coordinates[keyword] = merge_coordinates(keyword_coordinates)

    return dict(matched_coordinates)


def sibbal(extracted_data, important_words_list):
    # OCR 텍스트와 중요 단어 리스트 정규화
    joined_text = ''.join([entry['text'].replace(' ', '').lower() for entry in extracted_data])  # 공백 제거 후 합침
    indexed_text = [entry['text'].replace(' ', '').lower() for entry in extracted_data]  # 공백 제거된 OCR 텍스트 목록
    joined_important_words_list = [word.replace(' ', '').lower() for word in important_words_list]  # 공백 제거된 중요 단어 리스트

    all_coordinates = []

    for keyword in joined_important_words_list:
        coordinates = []
        # 정규표현식으로 중요 단어의 모든 위치 찾기 (대소문자 구분 없음)
        for match in re.finditer(re.escape(keyword), joined_text, re.IGNORECASE):
            start, end = match.start(), match.end()

            # OCR 텍스트와 매칭하여 좌표 찾기
            temp = 0
            for idx in range(len(indexed_text)):
                text_length = len(indexed_text[idx])
                # 겹치는 모든 경우를 포함
                if max(start, temp) < min(end, temp + text_length):
                    coordinates.append(extracted_data[idx]['coordinates'])
                temp += text_length  # 누적 길이 업데이트

        # 좌표 병합 후 저장
        all_coordinates.append(merge_coordinates(coordinates))
    
    # 원래 중요 단어 리스트와 매칭된 좌표를 딕셔너리로 반환
    result = dict(zip(important_words_list, all_coordinates))
    return result



def cross_validate(extracted_data, important_words_list):
    # 두 함수 결과 저장
    result_1 = find_coordinates_regex(extracted_data, important_words_list)
    result_2 = sibbal(extracted_data, important_words_list)
    
    # 일관성 확인
    if result_1 == result_2:
        print("두 함수가 동일한 결과를 반환합니다!")
    else:
        print("두 함수의 결과가 다릅니다.")
        # 차이 분석
        for key in important_words_list:
            if result_1.get(key) != result_2.get(key):  # 결과가 다른 경우만 출력
                print(f"키워드: {key}")
                print(f"find_coordinates_regex 결과: {result_1.get(key, 'N/A')}")
                print(f"sibbal 결과: {result_2.get(key, 'N/A')}")
                print("-" * 50)

    return result_1, result_2












'''

# ------------------------- 길이조정까지 맨 마지막꺼 쓰면 됨 !!!-----------------------------------



from PIL import Image, ImageDraw
import re
from collections import defaultdict

def calculate_relative_coordinates(block_coordinates, text_length, start_idx, end_idx):
    """
    OCR 블록 내에서 키워드의 상대적 좌표 계산
    :param block_coordinates: OCR 블록의 네 점 좌표 [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    :param text_length: OCR 블록 내 전체 텍스트 길이
    :param start_idx: 키워드 시작 인덱스
    :param end_idx: 키워드 끝 인덱스
    :return: 키워드의 상대적 좌표 [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    """
    # 다각형 좌표에서 x1, y1, x2, y2 추출
    x1, y1 = block_coordinates[0]  # 좌상단 좌표
    x2, y2 = block_coordinates[2]  # 우하단 좌표

    block_width = x2 - x1

    # 키워드 시작/끝 인덱스 비율 계산
    start_ratio = start_idx / text_length
    end_ratio = end_idx / text_length

    # 키워드에 해당하는 상대적 좌표 계산
    keyword_x1 = x1 + int(block_width * start_ratio)
    keyword_x2 = x1 + int(block_width * end_ratio)

    # Y 좌표는 블록 전체 높이를 그대로 유지
    return [(keyword_x1, y1), (keyword_x2, y1), (keyword_x2, y2), (keyword_x1, y2)]


def find_coordinates_with_relative(ocr_results, important_words_list):
    """
    OCR 결과에서 중요한 키워드의 절대 좌표를 계산하여 반환
    :param ocr_results: OCR 결과 (텍스트와 좌표 리스트)
    :param important_words_list: 중요한 키워드 리스트
    :return: 키워드별 절대 좌표 딕셔너리
    """
    matched_coordinates = defaultdict(list)
    combined_text = "".join([entry['text'].replace(" ", "") for entry in ocr_results])

    for keyword in important_words_list:
        keyword_normalized = keyword.replace(" ", "")

        # 키워드에 대한 정규 표현식 패턴 생성
        pattern = re.escape(keyword_normalized)

        # 문자열 내 키워드 매칭
        for match in re.finditer(pattern, combined_text):
            start_idx = match.start()
            end_idx = match.end()

            # OCR 결과를 순회하여 구간 매칭
            cumulative_length = 0
            keyword_coordinates = []
            for entry in ocr_results:
                entry_text = entry['text'].replace(" ", "")
                entry_length = len(entry_text)

                # 키워드가 OCR 블록 내에 포함되는 경우
                if start_idx < cumulative_length + entry_length and end_idx > cumulative_length:
                    block_start_idx = max(0, start_idx - cumulative_length)
                    block_end_idx = min(entry_length, end_idx - cumulative_length)

                    # 절대 좌표 계산
                    relative_coordinates = calculate_relative_coordinates(
                        entry['coordinates'],
                        entry_length,
                        block_start_idx,
                        block_end_idx
                    )
                    keyword_coordinates.append({
                        "coordinates": relative_coordinates,
                        "page_number": entry.get("page_number", 1)  # 페이지 번호 추가, 기본값 1
                    })

                # 누적 길이 업데이트
                cumulative_length += entry_length

            # 결과 저장
            if keyword_coordinates:
                matched_coordinates[keyword].extend(keyword_coordinates)

    return dict(matched_coordinates)

'''


#------------------------- normalized vertices -----------------------------------

from PIL import Image, ImageDraw
import re
from collections import defaultdict

'''
def calculate_relative_coordinates(block_coordinates, text_length, start_idx, end_idx, image_list, page_number):
    """
    Calculate the relative coordinates of a keyword within an OCR block using normalized vertices.
    """
    # Get the dimensions of the specific page from the image_list
    page_image = image_list[page_number - 1]
    page_width, page_height = page_image.size

    # Convert normalized vertices to absolute coordinates
    x1, y1 = block_coordinates[0][0] * page_width, block_coordinates[0][1] * page_height
    x2, y2 = block_coordinates[2][0] * page_width, block_coordinates[2][1] * page_height
    block_width = x2 - x1

    # Calculate the start and end ratios of the keyword within the block
    start_ratio = start_idx / text_length
    end_ratio = end_idx / text_length
    end_ratio = min(1.0, end_ratio + 0.02)  # Add a small margin (2%) to the end position

    # Compute the relative coordinates of the keyword
    keyword_x1 = x1 + block_width * start_ratio
    keyword_x2 = x1 + block_width * end_ratio

    # Add padding for better coverage
    padding = 3  # Add 3 pixels of padding to the left and right
    keyword_x1 = max(0, keyword_x1 - padding)
    keyword_x2 = min(page_width, keyword_x2 + padding)

    # Keep the vertical bounds of the block unchanged
    return [(keyword_x1, y1), (keyword_x2, y1), (keyword_x2, y2), (keyword_x1, y2)]

def find_coordinates_with_relative(ocr_results, important_words_list, image_list):
    """
    Find the absolute coordinates of important keywords from OCR results.

    :param ocr_results: List of OCR results, where each entry contains text and coordinates
    :param important_words_list: List of important keywords to locate
    :param image_list: List of PIL Image objects representing the document pages
    :return: Dictionary mapping each keyword to its list of absolute coordinates
    """
    matched_coordinates = defaultdict(list)
    combined_text = "".join([entry['text'].replace(" ", "") for entry in ocr_results])

    for keyword in important_words_list:
        keyword_normalized = keyword.replace(" ", "")

        # Create a regular expression pattern for the keyword
        pattern = re.escape(keyword_normalized)

        # Match the keyword in the combined text
        for match in re.finditer(pattern, combined_text):
            start_idx = match.start()
            end_idx = match.end()

            # Iterate through OCR results to find the matching block
            cumulative_length = 0
            keyword_coordinates = []
            for entry in ocr_results:
                entry_text = entry['text'].replace(" ", "")
                entry_length = len(entry_text)

                # Check if the keyword overlaps with the current OCR block
                if start_idx < cumulative_length + entry_length and end_idx > cumulative_length:
                    block_start_idx = max(0, start_idx - cumulative_length)
                    block_end_idx = min(entry_length, end_idx - cumulative_length)

                    # Calculate relative coordinates within the block
                    relative_coordinates = calculate_relative_coordinates(
                        entry['coordinates'],
                        entry_length,
                        block_start_idx,
                        block_end_idx,
                        image_list,
                        entry.get("page_number", 1)  # Default to page 1 if not provided
                    )
                    keyword_coordinates.append({
                        "coordinates": relative_coordinates,
                        "page_number": entry.get("page_number", 1)  # Default to page 1 if not provided
                    })

                # Update the cumulative text length
                cumulative_length += entry_length

            # Store the coordinates for the keyword
            if keyword_coordinates:
                matched_coordinates[keyword].extend(keyword_coordinates)

    return dict(matched_coordinates)
'''
def calculate_relative_coordinates(block_coordinates, text_length, start_idx, end_idx, image_list, page_number):
    """
    Calculate the relative coordinates of a keyword within an OCR block using normalized vertices.
    """
    # Get the dimensions of the specific page from the image_list
    page_image = image_list[page_number - 1]
    page_width, page_height = page_image.size

    # Convert normalized vertices to absolute coordinates
    x1, y1 = block_coordinates[0][0] * page_width, block_coordinates[0][1] * page_height
    x2, y2 = block_coordinates[2][0] * page_width, block_coordinates[2][1] * page_height

    # Keep the vertical bounds of the block unchanged
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

def find_coordinates_with_relative(ocr_results, important_words_list, image_list):
    """
    Find the absolute coordinates of important keywords from OCR results.

    :param ocr_results: List of OCR results, where each entry contains text and coordinates
    :param important_words_list: List of important keywords to locate
    :param image_list: List of PIL Image objects representing the document pages
    :return: Dictionary mapping each keyword to its list of absolute coordinates
    """
    matched_coordinates = defaultdict(list)
    combined_text = "".join([entry['text'].replace(" ", "") for entry in ocr_results])

    for keyword in important_words_list:
        keyword_normalized = keyword.replace(" ", "")

        # Create a regular expression pattern for the keyword
        pattern = re.escape(keyword_normalized)

        # Match the keyword in the combined text
        for match in re.finditer(pattern, combined_text):
            start_idx = match.start()
            end_idx = match.end()

            # Iterate through OCR results to find the matching block
            cumulative_length = 0
            keyword_coordinates = []
            for entry in ocr_results:
                entry_text = entry['text'].replace(" ", "")
                entry_length = len(entry_text)

                # Check if the keyword overlaps with the current OCR block
                if start_idx < cumulative_length + entry_length and end_idx > cumulative_length:
                    block_start_idx = max(0, start_idx - cumulative_length)
                    block_end_idx = min(entry_length, end_idx - cumulative_length)

                    # Calculate relative coordinates within the block
                    relative_coordinates = calculate_relative_coordinates(
                        entry['coordinates'],
                        entry_length,
                        block_start_idx,
                        block_end_idx,
                        image_list,
                        entry.get("page_number", 1)  # Default to page 1 if not provided
                    )
                    keyword_coordinates.append({
                        "coordinates": relative_coordinates,
                        "page_number": entry.get("page_number", 1)  # Default to page 1 if not provided
                    })

                # Update the cumulative text length
                cumulative_length += entry_length

            # Store the coordinates for the keyword
            if keyword_coordinates:
                matched_coordinates[keyword].extend(keyword_coordinates)

    return dict(matched_coordinates)