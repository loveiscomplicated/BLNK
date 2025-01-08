from PIL import Image, ImageDraw, ImageSequence
import os
import pandas as pd

# blank_image 모듈 사용법:
# 1. 좌표 데이터(딕셔너리)를 데이터프레임으로 변환
# 2. add_blanks_to_image 함수를 사용하여 이미지에 빈칸을 추가
# 3. save_images_as_pdf 함수를 사용하여 이미지 리스트를 PDF로 저장

# ---------------------------------------------------------------

def dict_to_dataframe(data):
    """
    주어진 딕셔너리를 데이터프레임으로 변환하는 함수
    :param data: 딕셔너리 형태의 데이터 (키워드와 관련된 좌표 및 페이지 번호 포함)
    :return: 변환된 데이터프레임
    """
    # 데이터를 저장할 리스트 생성
    rows = []

    # 딕셔너리의 각 항목(key: keyword, value: details)을 반복
    for keyword, details in data.items():
        for detail in details:
            # 데이터프레임에 추가할 행 생성
            row = {
                'keyword': keyword,  # 키워드
                'coordinates': detail['coordinates'],  # 좌표 리스트
                'page_number': detail['page_number']  # 페이지 번호
            }
            rows.append(row)  # 행을 리스트에 추가

    # 리스트를 데이터프레임으로 변환
    df = pd.DataFrame(rows)
    return df

# ---------------------------------------------------------------

def add_blanks_to_image(image_list, df_data):
    modified_images = [image.copy() for image in image_list]  # 원본 유지
    for i in range(1, max(df_data['page_number']) + 1):
        image = modified_images[i - 1]
        image = image.convert('RGB')
        draw = ImageDraw.Draw(image)
        boxes = df_data[df_data['page_number'] == i]['coordinates'].tolist()
        # boxes는 'df_data' 데이터프레임에서 'coordinates' 열의 값으로부터 가져온 리스트
        
        # boxes는 [[(x1, y1), (x2, y1), (x2, y2), (x1, y2)],
        #            [(x1, y1), (x2, y1), (x2, y2), (x1, y2)],...] 형태
        
        # box는 [(x1, y1), (x2, y1), (x2, y2), (x1, y2)] 형태
        for box in boxes:
            xs = [pt[0] for pt in box]
            ys = [pt[1] for pt in box]
            x_min, x_max = round(min(xs)), round(max(xs))
            y_min, y_max = round(min(ys)), round(max(ys))
            draw.rectangle([x_min, y_min, x_max, y_max], fill=(97, 191, 173))
        modified_images[i - 1] = image
    return modified_images

# ---------------------------------------------------------------

def save_images_as_pdf(image_list, output_path):
    """
    PIL 이미지 객체 리스트를 PDF로 저장하는 함수.

    Args:
        image_list (list): PIL 이미지 객체 리스트.
        output_path (str): 저장할 PDF 파일 경로.

    Returns:
        None
    """
    if not image_list:
        raise ValueError("이미지 리스트가 비어 있습니다.")

    # 모든 이미지를 RGB로 변환 (PDF는 RGBA를 지원하지 않음)
    rgb_images = [img.convert("RGB") for img in image_list]

    # 첫 번째 이미지는 메인으로 사용하고 나머지는 append
    rgb_images[0].save(output_path, save_all=True, append_images=rgb_images[1:])

    print(f"PDF가 {output_path}에 저장되었습니다.")

# ---------------------------------------------------------------

if __name__ == '__main__':
    import pickle
    import tempfile

    path = 'C:/Users/LG/miniconda3/envs/BLNK/codes/check/output/coordinates_과연과연.pkl'
    with open(path, 'rb') as f:
        coordinate = pickle.load(f)
    
    image_list_path = 'C:/Users/LG/miniconda3/envs/BLNK/codes/check/output/image_list_과연과연.pkl'
    with open(image_list_path, 'rb') as f:
        image_list = pickle.load(f)

    print(coordinate)
    print(image_list)

    result_image_list = []
    for image in image_list:
        image = ensure_single_frame(image)  # 단일 프레임 보장
        result_image = add_blanks_to_image(image, coordinate)
        
        result_image_list.append(result_image)
        
        # 결과를 임시 파일로 저장 후 열기
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            result_image.save(temp_file.name)
            os.startfile(temp_file.name)  # 기본 뷰어로 열기
        
    save_path = 'C:/Users/LG/miniconda3/envs/BLNK/codes/check/output/result.pdf'
    save_images_as_pdf(result_image_list, save_path)
