```markdown
# 📚 BLNK: Blank Learning with NLP and Knowledge

> 학습 자료에서 중요한 단어나 구절을 자동으로 추출하고, 해당 부분을 빈칸으로 마스킹하여 학습용 PDF로 변환해주는 AI 기반 자동화 도구

---

## ✨ 프로젝트 소개

BLNK는 GPT와 OCR 기술을 기반으로, 기존 학습 자료(PDF)에서 중요한 정보를 자동 식별하고 빈칸 처리하여 새로운 복습용 자료를 생성하는 파이썬 기반 프로그램입니다.

- ✅ 수작업으로 빈칸 문제 만들기 NO
- ✅ GPT가 핵심 단어를 자동 추출
- ✅ 시각적 PDF 마스킹 적용
- ✅ 빈칸 비율로 난이도 조절 가능
- ✅ 최종 PDF 파일로 저장 및 출력 가능

---

## 🛠️ 주요 기능

| 기능 | 설명 |
|------|------|
| 📄 PDF 텍스트/위치 추출 | Google Document AI 사용, 단어별 좌표까지 포함 |
| 🧠 중요 단어 추출 | GPT-4o-mini를 통해 문맥 기반 핵심 단어 선정 |
| 🎚️ 난이도 조절 | 빈칸 비율을 사용자가 직접 설정 가능 |
| 🖍️ 마스킹 처리 | OpenCV로 지정 위치에 불투명 박스 덮기 |
| 🗂️ PDF 변환 | 이미지 → PDF로 병합 저장 (img2pdf 사용) |

---

## 🔧 기술 스택

- Python 3.10
- Google Document AI (OCR)
- OpenAI GPT-4o-mini (Keyword Extraction)
- OpenCV (Image Processing)
- img2pdf (PDF 저장)
- 기타: `requests`, `json`, `PIL`, `pdf2image` 등

---

## 📁 폴더 구조

```

BLNK/
├── main.py
├── src/
│   ├── ocr.py
│   ├── GPT_important_words.py
│   └── draw_blank.py
├── tests/materials
│         └── example.pdf
├── output/
│   └── masked\_output.pdf
|
├── environment.yml
└── README.md

````

---

## 🚀 사용 방법

1. **Google Document AI 설정**
   - 서비스 계정 키 생성 후 환경변수 등록

2. **OpenAI API 키 설정**
   ```bash
   export OPENAI_API_KEY=your_key_here
````

3. **의존 패키지 설치**

   ```bash
   pip install -r requirements.txt
   ```

4. **실행**

   ```bash
   python main.py --input samples/example.pdf --output output/masked_output.pdf --blank_ratio 0.3
   ```

---

## 🧩 시스템 흐름도

```text
[PDF 업로드]
     ↓
[OCR → 텍스트 & 좌표 추출]
     ↓
[GPT로 중요 단어 추출]
     ↓
[위치 기반 마스킹 (OpenCV)]
     ↓
[PDF 저장 (img2pdf)]
```

---

## 💡 차별성

| 기존 방식         | BLNK                   |
| ------------- | ---------------------- |
| 사용자가 직접 빈칸 생성 | 자동 추출 및 마스킹            |
| 단순 키워드 추출기    | GPT 기반 문맥 중심 분석        |
| 텍스트 기반 결과     | 실제 PDF에 시각적 마스킹        |
| 재사용 어려움       | 전체 파이프라인 자동화로 반복 사용 가능 |

---

## 📌 향후 확장 계획

* ✅ 사용자 지정 키워드 입력 기능
* ✅ 하이라이트 방식 마스킹 추가
* ✅ 웹 인터페이스 구축 (Flask/Streamlit)
* ✅ 다국어 지원 (영어/한국어)

---

## 📮 문의 및 기여

기능 제안 또는 버그 제보는 [Issue](https://github.com/loveiscomplicated/BLNK/issues) 탭에 남겨주세요!
기여를 원하시면 Fork 후 Pull Request 부탁드립니다.

---

© 2025. lovesicomplicated. All rights reserved.

```

