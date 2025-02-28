import json
import openai
import re
from collections import Counter



# GPT API key 읽어들이는 함수
def load_api_key(api_key_path):
    with open(api_key_path, 'r') as f:
        api_key = json.load(f)['api_key']
    return api_key



# 너무 자주 등장하는 단어 필터링 함수
def filter_frequent_words(input_text: str, threshold: float = 0.05):
    """
    Remove words that appear too frequently in the text.
    
    Parameters:
    - input_text (str): The input text.
    - threshold (float): The frequency threshold (default: 5% of the text).
    
    Returns:
    - list: Words that should be excluded.
    """
    words = input_text.lower().split()
    total_words = len(words)
    word_counts = Counter(words)

    # 특정 비율(예: 5%) 이상 등장하는 단어 필터링
    frequent_words = {word for word, count in word_counts.items() if count / total_words > threshold}
    
    return list(frequent_words)


# GPT API 호출 함수
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

    # 빈칸 개수 계산
    min_keywords, max_keywords = calculate_keyword_range_from_text(input_text, keyword_ratio)
    
    # 너무 자주 등장하는 단어 필터링
    frequent_words = filter_frequent_words(input_text)

    # GPT 프롬프트
    prompt = f"""
    You are an expert in educational assessment design. Your task is to analyze the given text and identify the most important words that should be converted into blanks to assess the learner’s memorization. The words should be selected based on their significance to the key concepts in the text.

    ### Input Text:
    {input_text}

    ### Instructions:

    1. Identify the most important **keywords** or **phrases** that are essential for understanding the main concepts.
    2. Exclude:
       - Common function words (e.g., articles, prepositions, conjunctions).
       - Words that appear **more than 5% of the total words** in the given text, unless they are essential for understanding the topic.
       - Avoid words that are **too obvious or trivial** for learners based on common background knowledge. 
         - Do not select words that are universally known or predictable in context.
    3. The selected words should **maximize learning effectiveness**—choosing words that, when masked, reinforce key concepts and enhance memory retention.
    4. Use the provided `{min_keywords}` and `{max_keywords}` values, which have been precomputed externally, to determine the number of blanks.
    5. Exclude these frequently appearing words from selection: {frequent_words}
    6. Return a structured JSON format with only the list of selected words.

    ### Output Format:
    ```json
    {{
      "blanks": ["word1", "word2", "word3"]
    }}
    ```
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
            return blanks_dict.get("blanks", [])  # 리스트 반환
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

    


