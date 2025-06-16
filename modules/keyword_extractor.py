import json
import openai
import re
from collections import Counter

# GPT API key 읽어들이는 함수
def load_api_key(api_key_path):
    with open(api_key_path, 'r') as f:
        api_key = json.load(f)['api_key']
    return api_key

def get_keyword_bounds(text: str, 
                        keyword_ratio: float, 
                        variation_factor: float = 0.1):
    """
    Calculate the minimum and maximum number of keywords for blank masking based on input text.
    """
    words = re.findall(r'[가-힣a-zA-Z0-9]+', text.lower())
    total_words = len(set(words))
    num_keywords = max(1, int(total_words * keyword_ratio))
    a = max(1, int(num_keywords * variation_factor))

    min_keywords = max(1, num_keywords - a)
    max_keywords = num_keywords + a

    return min_keywords, max_keywords

def get_frequent_words(text: str, threshold: float = 0.05):
    """
    Remove words that appear too frequently in the text.
    
    Parameters:
    - input_text (str): The input text.
    - threshold (float): The frequency threshold (default: 5% of the text).
    
    Returns:
    - list: Words that should be excluded.
    """
    words = re.findall(r'[가-힣a-zA-Z0-9]+', text.lower())
    total_words = len(words)
    word_counts = Counter(words)

    # 특정 비율(예: 5%) 이상 등장하는 단어 필터링
    frequent_words = {word for word, count in word_counts.items() if count / total_words > threshold}
    
    return list(frequent_words)

def filter_word_list(blanks: list, frequent_words: list, max_keywords: int):
    '''
    Parameters:
    - blanks: List of keywords to be blanked.
    - frequent_words: Words that should be excluded.
    - max_keywords: maximum number of keywords for blank masking based on input text
    '''
    blanks_copy = blanks
    to_remove = []
    for word in blanks_copy:
        if word in frequent_words:
            to_remove.append(word)
    
    blanks_copy = [i for i in blanks_copy if i not in to_remove]
    
    if len(blanks_copy) > max_keywords:
        blanks_copy = blanks_copy[:max_keywords]
    
    return blanks_copy
    
            

def gpt_api_call(gpt_api_key, input_text, keyword_ratio):
    """
    Calls OpenAI API to generate blanked-out keywords based on the given text.
    
    Parameters:
    - gpt_api_key (str): OpenAI API key.
    - input_text (str): The full text to analyze.
    - keyword_ratio (float): The ratio of words to be masked as blanks.
    
    Returns:
    - list: List of keywords to be blanked.
    """

    min_keywords, max_keywords = get_keyword_bounds(input_text, keyword_ratio, variation_factor=0.1)
    frequent_words = get_frequent_words(input_text, threshold=0.01)

    # GPT 프롬프트 (보완 버전)
    prompt = f"""
        당신은 교육 평가 전문가입니다. 제공된 텍스트에서 학습자의 핵심 개념 이해도를 평가할 빈칸 문제를 위한 **중요 단어(개념어)**를 선별하세요.

        ### 입력 텍스트:
        {input_text}

        ### 작업 지침:

        1.  텍스트의 **핵심 내용을 이해하는 데 필수적인 명사, 전문 용어** 위주로 단어를 선별하세요.
        2.  다음 단어는 **절대 선택하지 마세요**:
            * 기능어 (관사, 전치사, 접속사 등)
            * 문맥상 쉽게 유추 가능한 **자명한 단어** (예: "태양" from "___은 동쪽에서 뜬다")
            * 제외 목록: {frequent_words}
        3.  선택된 단어 수는 **{min_keywords}개 이상, {max_keywords}개 이하**로 하세요.
        4.  단어는 **원문에 등장한 형태 그대로** 추출하되, JSON 출력 시 **모두 소문자로 변환**하세요. 단, 고유명사는 원형을 유지할 수 있습니다.

        ### 출력 형식:
        ```json
        {{
        "blanks": ["word1", "word2", "word3"]
        }}
    """
    # OpenAI 클라이언트 생성
    client = openai.OpenAI(api_key=gpt_api_key)

    # GPT API 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    # 응답 내용 가져오기
    try:
        response_content = response.choices[0].message.content.strip()
        
        # JSON 형식이므로 올바르게 파싱
        blanks_json = re.search(r'\{.*\}', response_content, re.DOTALL)  # JSON 추출
        if blanks_json:
            blanks_dict = json.loads(blanks_json.group())  # JSON 변환
            blanks_list = blanks_dict.get("blanks", []) # 리스트 반환
            blanks_list = filter_word_list(blanks_list, frequent_words, max_keywords)
            return blanks_list
        else:
            return []  # JSON이 없으면 빈 리스트 반환

    except Exception as e:
        print(f"Error processing GPT response: {e}")
        return []


if __name__ == '__main__':
    path = './tests/materials/gpt_api_key.json'
    gpt_api_key = load_api_key(path)

    # 예제 파일 로드
    import pickle

    save_path = './tests/materials/document_object.pkl'

    with open(save_path, 'rb') as f:
        document_object = pickle.load(f)

    # print(document_object.text)

    def calculate_keyword_range_from_text(input_text: str, keyword_ratio: float, variation_factor: float = 0.1):
        """
        Calculate the minimum and maximum number of keywords for blank masking based on input text.
        """
        total_words = len(input_text.split())
        num_keywords = max(1, int(total_words * keyword_ratio))
        a = max(1, int(num_keywords * variation_factor))

        min_keywords = max(1, num_keywords - a)
        max_keywords = num_keywords + a

        return min_keywords, max_keywords
    # 테스트용 예제 텍스트
    input_text = document_object.text
    keyword_ratio = 0.15  # 15%의 단어를 빈칸으로 변환

    blanks = gpt_api_call(gpt_api_key, input_text, keyword_ratio)
    print(blanks)
    blank_save_path = './tests/materials/ex_history_blank.pkl'

    with open(blank_save_path, 'wb') as f:
        pickle.dump(blanks, f) 

    


