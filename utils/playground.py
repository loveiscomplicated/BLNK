import pickle

# ---------------- 파일 로드 ------------------------
save_path = './tests/materials/document_object.pkl'

with open(save_path, 'rb') as f:
    document_object = pickle.load(f)

blank_save_path = './tests/materials/ex_history_blank.pkl'

with open(blank_save_path, 'rb') as f:
    important_words_list = pickle.load(f) 

save_path_get_bounding_bxes_by_page = './tests/materials/get_bounding_bxes_by_page.pkl'

with open(save_path_get_bounding_bxes_by_page, 'rb') as f:
    coord_dict = pickle.load(f)

print(coord_dict)
# -------------------------------------------------------
from pdf2image import convert_from_path
import cv2
import numpy as np
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


file_path = './tests/materials/ex_history.pdf'

image_list = pdf_to_images_with_docai_size(file_path, document_object)
print(document_object.pages[3].dimension.width, document_object.pages[3].dimension.height)
for image in image_list:
    print(image.shape[1], image.shape[0])



import cv2
import numpy as np
import img2pdf
from PIL import Image
from io import BytesIO

def draw_boxes(image_list, coord_dict, output_pdf_path="output.pdf", color=(0, 255, 0), thickness=2):
    """
    바운딩 박스를 이미지에 그린 후, 고품질로 PDF 저장하는 함수.
    - `coord_dict`의 키(페이지 번호)를 정렬하여 PDF 페이지 순서 유지.

    Args:
        image_list (list of np.array): 원본 이미지 리스트 (페이지별 이미지)
        coord_dict (dict): 페이지별 바운딩 박스 좌표 딕셔너리 (정렬되지 않은 상태)
            - {page_number: [[(x1, y1), (x2, y2), (x3, y3), (x4, y4)], ...]}
        output_pdf_path (str): 저장할 PDF 파일 경로 (기본값: "output.pdf")
        color (tuple): 바운딩 박스 색상 (기본값: 초록색)
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
            cv2.polylines(image, [pts], isClosed=True, color=color, thickness=thickness)

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



draw_boxes(image_list, coord_dict, output_pdf_path="./tests/materials/output.pdf")

