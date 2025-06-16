import pickle


'''
Document AI의 결과물인 document_object의 구조를 확인할 수 있는 코드
'''

# 예시 파일 불러오기
save_path = './tests/materials/document_object.pkl'

with open(save_path, 'rb') as f:
    document_object = pickle.load(f)

# 전체 구조 파악하기
print(document_object)

# 페이지 당 구조 파악하기
print(document_object.pages[3])

# 전체 텍스트 파악하기
print(document_object.text)

# 페이지 내에서 토큰 별로 확인하기
print(document_object.pages[3].tokens)


# --------------------------------------------------------
# 토큰 스타트, 엔드 인덱스 찾으려면 text_segments[0]으로 접근하기
print(document_object.pages[3].tokens[9].layout.text_anchor)

print(document_object.pages[3].tokens[9].layout.text_anchor.text_segments[0].start_index)
print(document_object.pages[3].tokens[9].layout.text_anchor.text_segments[0].end_index)

# 스타트, 엔드 인덱스를 가지고 해당 토큰을 text에서 뽑아 쓰는 구조
print(document_object.text[886:889])

# 페이지 별 스타트, 엔드 인덱스
for page in document_object.pages:
    print(page.layout.text_anchor.text_segments[0]) # 항상 맨 처음은 start_index가 없다는 거 주의 !

# --------------------------------------------------------

# bounding poly 
print(document_object.pages[3].tokens[0].layout.bounding_poly)

# 절대좌표
print(document_object.pages[3].tokens[0].layout.bounding_poly.vertices)

# bounding poly - normalized vertices는 다음과 같이 찾는다
print(document_object.pages[3].tokens[0].layout.bounding_poly.normalized_vertices)


# 페이지 크기 -> 실제 이미지 사이즈랑 안 맞으면 이거 기준으로 resize해야 함
print(document_object.pages[3].dimension.width)
print(document_object.pages[3].dimension.height)



for page in document_object.pages:
    print('페이지 번호 : ', page.page_number)
    print('페이지 크키 : ', page.dimension)

for page in document_object.pages:
    for token in page.tokens:
        token.layout.text_anchor.text_segments[0].start_index
        token.layout.text_anchor.text_segments[0].end_index