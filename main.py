import os
import time

import modules
import modules.OCR

def run_project_BLNK():
    print("----프로그램 시작----")
    google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if google_credentials:
        print(f"GOOGLE_APPLICATION_CREDENTIALS가 설정되어 있습니다: {google_credentials}")
    else:
        print("GOOGLE_APPLICATION_CREDENTIALS가 설정되어 있지 않습니다.")
        
    print("난이도를 0부터 1 사이의 소수로 입력하세요. 1에 가까울 수록 난이도는 더 어려워집니다.")
    keyWordRatio = float(input("난이도: "))
    print("빈칸 문제 생성을 위한 학습 자료의 원본 경로를 입력해주세요.")
    input_dir = input("학습 자료 경로: ")
    print("결과 파일은 어디에 저장할까요?")
    output_dir = input("저장 경로: ")
    modules.OCR.all_in_one(input_dir, keyWordRatio, output_dir)

if __name__ == "__main__":
    start_time = time.time() 
    run_project_BLNK()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"코드 실행 시간: {execution_time:.2f} 초")


"""
./tests/materials/25-1 알고리즘.pdf
./output.pdf
"""