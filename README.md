# BLNK

BLNK - blankit 빈칸 마스킹 프로그램

본 프로그램은 학습 자료를 넣으면 
자동으로 중요한 부분에 빈칸을 생성해주는 프로그램입니다.

!중요!
Open Ai api와 Google Document AI api를 사용하기 위한 키가 필요합니다

# 사용법
1. main.py 실행
2. 학습 자료의 디렉토리 경로를 ''절대경로'' 형식으로 입력해주세요
3. 결과물을 저장할 ''절대경로'' 형식으로 입력해주세요

# 중요 사항
1. 지원 파일 형식
    - pdf
    - 이미지 (png, jpg, jpeg, bmp, tiff)
    - ppt (ppt, pptx)
    - txt
    - 워드 (doc, docx)
    - 아래아한글 (hwp, hwpx)

2. 결과물 형식
    - pdf
    - 중요 부분이 박스로 마스킹됩니다.

3. 난이도 설정
    - 난이도는 main.py의 keyword_ratio 변수에 0~1 사이의 값을 입력하여 설정할 수 있습니다.
    - 0에 가까울수록 난이도가 낮고, 1에 가까울수록 난이도가 높아집니다.

# FLOW CHART

![스크린샷 2025-01-08 135352](https://github.com/user-attachments/assets/72afb351-8757-408c-b1fc-b52b9b6e4f42)


# 향후 계획
1. 웹사이트 구현 후 배포
  2. Figma 사용하여 웹사이트 디자인 구성
  3. Figma 프로젝트 파일 -> 프론트엔드 템플릿(HTML, CSS, JAVASCRIPT)으로 변환
  4. Shared WebHosting으로 서버 대여
  5. 도메인 구입

2. 구글 애드센스 도입 후 수익 실현
