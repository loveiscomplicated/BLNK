import pickle

save_path = './tests/materials/document_object.pkl'

with open(save_path, 'rb') as f:
    document_object = pickle.load(f)


print(document_object)

# 이제 만들어야 하는 것은 
# Document AI의 document_object에서 특정 **텍스트 범위(시작 인덱스 ~ 끝 인덱스)**에 포함된 **토큰(token)**을 검색하는 함수

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
                matched_tokens.append({
                    "text": document_object.text[token_start:token_end],  # 실제 텍스트
                    "start_index": token_start,
                    "end_index": token_end,
                    "page_number": page.page_number,
                    "normalized_vertices": [
                        {"x": vertex.x, "y": vertex.y} for vertex in token.layout.bounding_poly.normalized_vertices
                    ]  # 좌표 리스트 변환
                })

    return matched_tokens



# 🔥 예제 실행
start_index = 6
end_index = 14
tokens_in_range = find_tokens_in_range(document_object, start_index, end_index)

# 결과 출력
for token in tokens_in_range:
    print(f"토큰: {token['text']}, 시작: {token['start_index']}, 끝: {token['end_index']}, 페이지: {token['page_number']}")
