import pickle

save_path = './tests/materials/document_object.pkl'

with open(save_path, 'rb') as f:
    document_object = pickle.load(f)


#print(document_object)



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


FILE_PATH = "./tests/materials/ex_history.pdf"
pil_images = convert_from_path(FILE_PATH, dpi=300)
print(pil_images)


image_list = pdf_to_images_with_docai_size(FILE_PATH, document_object)
print(image_list[0].shape[0], image_list[0].shape[1])