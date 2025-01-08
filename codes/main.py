import OCR
import ppt_hwp2
import GPT_important_words
import NON_OCR
import os
import coordinates
import pickle
import blank_image
import blank_text

# 파일 경로    
file_path = "C:/Users/LG/miniconda3/envs/BLNK/codes/check/just/qqq.hwp"



# ----------------------------- 텍스트 추출 ------------------------------------

# 파일 확장자에 따라 적절한 함수 호출
_, file_extension = os.path.splitext(file_path)

# OCR
if file_extension.lower() == '.pdf':
    # 기본 정보
    project_id = "입력 필요"
    location = "입력 필요"
    processor_id = "입력 필요"
    
    
    # document ai 최대 처리 용량이 20MB이므로 20MB 초과 시 분할하여 처리
    total_size_mb = os.path.getsize(file_path) / (1024 * 1024) 
    if total_size_mb > 20:
        print("파일 크기가 20MB를 초과하므로 분할하여 처리합니다.")
        split_files = OCR.dynamic_split_pdf(file_path, 20)
        
        extracted_text = ""
        extracted_data = []
        image_list = []
        for split_file in split_files:
            print(f"파일 분할: {split_file}")
            print("OCR 진행 중.")
            extracted_text_part, extracted_data_part, image_list_part = OCR.pdf(project_id,
                                                                                location,
                                                                                processor_id,
                                                                                split_file)
            extracted_text += extracted_text_part
            extracted_data.extend(extracted_data_part)
            image_list.extend(image_list_part)
        # 임시 파일 삭제
        for split_file in split_files:
            os.remove(split_file)
            print(f"임시 파일 삭제: {split_file}")
    
    # 20MB 이하일 경우 한 번에 처리
    else: 
        print("OCR 진행 중.")
        extracted_text, extracted_data, image_list = OCR.pdf(project_id,
                                                            location,
                                                            processor_id,
                                                            file_path) 
# OCR        
elif file_extension.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
    print("OCR 진행 중.")
    project_id = "입력 필요"
    location = "입력 필요"
    processor_id = "입력 필요"
    extracted_text, extracted_data, image_list = OCR.image(project_id, 
                                                           location, 
                                                           processor_id, 
                                                           file_path)
# OCR
elif file_extension.lower() in ['.ppt', '.pptx']:
    print('ppt 파일을 처리 중.')
    # ppt, pptx를 pdf로 변환한 후 pdf 처리 과정을 그대로 따라감
    # ppt_hwp2.pdf(file_path)는 변환된 파일의 경로를 return
    file_path_1 = ppt_hwp2.pdf(file_path) 

    
    # 기본 정보
    project_id = "입력 필요"
    location = "입력 필요"
    processor_id = "입력 필요"
    
    
    # document ai 최대 처리 용량이 20MB이므로 20MB 초과 시 분할하여 처리
    total_size_mb = os.path.getsize(file_path_1) / (1024 * 1024) 
    if total_size_mb > 20:
        print("파일 크기가 20MB를 초과하므로 분할하여 처리합니다.")
        split_files = OCR.dynamic_split_pdf(file_path, 20)
        
        extracted_text = ""
        extracted_data = []
        image_list = []
        for split_file in split_files:
            print(f"파일 분할: {split_file}")
            print("OCR 진행 중.")
            extracted_text_part, extracted_data_part, image_list_part = OCR.pdf(project_id,
                                                                                location,
                                                                                processor_id,
                                                                                split_file)
            extracted_text += extracted_text_part
            extracted_data.extend(extracted_data_part)
            image_list.extend(image_list_part)
        # 임시 파일 삭제
        for split_file in split_files:
            os.remove(split_file)
            print(f"임시 파일 삭제: {split_file}")
    
    # 20MB 이하일 경우 한 번에 처리
    else: 
        print("OCR 진행 중.")
        extracted_text, extracted_data, image_list = OCR.pdf(project_id,
                                                            location,
                                                            processor_id,
                                                            file_path_1) 
# OCR
elif file_extension.lower() in ['.hwpx', '.hwp']:
    print('한글 파일을 처리 중.')
    # ppt, pptx를 pdf로 변환한 후 pdf 처리 과정을 그대로 따라감
    # ppt_hwp2.pdf(file_path)는 변환된 파일의 경로를 return
    file_path_1 = ppt_hwp2.hwp_to_pdf(file_path, delay=3) 
    print(file_path_1)
    
    # 기본 정보
    project_id = "입력 필요"
    location = "입력 필요"
    processor_id = "입력 필요"
    
    
    # document ai 최대 처리 용량이 20MB이므로 20MB 초과 시 분할하여 처리
    total_size_mb = os.path.getsize(file_path_1) / (1024 * 1024) 
    if total_size_mb > 20:
        print("파일 크기가 20MB를 초과하므로 분할하여 처리합니다.")
        split_files = OCR.dynamic_split_pdf(file_path, 20)
        
        extracted_text = ""
        extracted_data = []
        image_list = []
        for split_file in split_files:
            print(f"파일 분할: {split_file}")
            print("OCR 진행 중.")
            extracted_text_part, extracted_data_part, image_list_part = OCR.pdf(project_id,
                                                                                location,
                                                                                processor_id,
                                                                                split_file)
            extracted_text += extracted_text_part
            extracted_data.extend(extracted_data_part)
            image_list.extend(image_list_part)
        # 임시 파일 삭제
        for split_file in split_files:
            os.remove(split_file)
            print(f"임시 파일 삭제: {split_file}")
    
    # 20MB 이하일 경우 한 번에 처리
    else: 
        print("OCR 진행 중.")
        extracted_text, extracted_data, image_list = OCR.pdf(project_id,
                                                            location,
                                                            processor_id,
                                                            file_path_1)       
# NON_OCR
elif file_extension.lower() == '.txt':
    print("텍스트 파일을 처리 중.")
    extracted_text = NON_OCR.read_file_with_detected_encoding(file_path)
    status = '.txt'
# NON_OCR
elif file_extension.lower() == '.docx':
    print("DOCX 파일을 처리 중.")
    extracted_text = NON_OCR.docx2text(file_path)
    status = '.docx'
# NON_OCR   
elif file_extension.lower() == '.doc':
    print("DOC 파일을 처리 중.")
    extracted_text = NON_OCR.read_doc(file_path)
    status = '.doc'


else:
    print("지원되지 않는 파일 형식입니다.") # 나중에 배포할 때 바꾸기 !!!!! @@@@@@@@@@@@@@@@@@@@@@@@@@222



# -------------------------------- 중요한 키워드 추출 ----------------------------------


# 중요한 키워드 추출
path = '입력 필요' # API 키 경로, json 형식으로 저장 후 해당 경로 입력
gpt_api_key = GPT_important_words.load_api_key(path)

keyword_ratio = 0.01  # 키워드 비율 설정

important_words_list = GPT_important_words.gpt_api_call(gpt_api_key, extracted_text, keyword_ratio)
print(important_words_list)
print(len(important_words_list))  # 리스트 형식임




# 빈칸을 덮어씌워야 하는 경우
try:
    image_list  # 변수가 존재하는지 확인

    # ------------------------- 중요한 키워드와 좌표 매칭(PDF, 이미지) -----------------------------------
    coordinates = coordinates.find_coordinates_with_relative(extracted_data, important_words_list, image_list)

    # ------------------------- 빈칸 덮어씌우기 -----------------------------------
    df_data = blank_image.dict_to_dataframe(coordinates)
    modified_images = blank_image.add_blanks_to_image(image_list, df_data)
    output_path = '입력 필요'
    blank_image.save_images_as_pdf(modified_images, output_path)
    
# 빈칸을 덮어씌울 필요가 없는 경우
except NameError:
    output_path = '입력 필요'
    blank_text.main(status, important_words_list, file_path, output_path)


