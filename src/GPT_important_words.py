import json
import openai
from openai import OpenAI
import re


def load_api_key(api_key_path):
    with open(api_key_path, 'r') as f:
        api_key = json.load(f)['api_key']
    return api_key

# GPT API 호출 함수
def gpt_api_call(gpt_api_key, input_text, keyword_ratio):
    num_keywords = max(1, int(len(input_text.split()) * keyword_ratio))
    prompt = f"""
    Analyze the following text and extract the most important keywords that the student must know. 
    The keywords must be exactly as they appear in the text. 
    Use the following step-by-step process internally to determine the keywords:

    Step 1: Identify all potential keywords in the text that summarize the key concepts and are critical for understanding the main ideas.
    Step 2: Filter out keywords that do not align with the rules, such as excluding numeric information unless it represents a year (e.g., 2023).
    Step 3: Rank the remaining keywords based on their importance to the overall text.
    Step 4: Select exactly {num_keywords} keywords from the ranked list, ensuring the final selection captures the main ideas succinctly.

    The final output must:
    - Be a simple, comma-separated string of exactly {num_keywords} keywords.
    - Not include any additional formatting or text.

    Examples:
    - English: Artificial Intelligence, GPT models, NLP, 2023
    - Korean: 인공지능, GPT 모델, NLP, 2023

    Text:
    {input_text}

    Return exactly {num_keywords} keywords without modifying or translating them from the original text.
"""





    client = OpenAI(api_key = gpt_api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    string = response.choices[0].message.content

    result = [keyword.strip() for keyword in string.split(',') if keyword.strip()]

    return result


if __name__ == '__main__':
    path = 'C:/Users/LG/miniconda3/envs/BLNK/codes/gpt_api_key.json'
    gpt_api_key = load_api_key(path)
    input_text = (
        "인공지능은 현대 기술의 중요한 부분이며, GPT 모델은 NLP에서 뛰어난 성능을 보여줍니다. "
        "자율 주행, 의료 진단, 고객 서비스 등의 분야에서 인공지능 기술은 빠르게 발전하고 있습니다. "
        "특히, 대규모 언어 모델은 인간 수준의 언어 이해와 생성 능력을 통해 다양한 애플리케이션에서 활용되고 있습니다. "
        "이와 함께, 윤리적 문제와 데이터 프라이버시와 같은 도전 과제도 부각되고 있으며, 이를 해결하기 위한 다양한 연구가 진행 중입니다. "
        "결과적으로, 인공지능은 우리의 삶을 변화시키고 있으며, 지속적인 발전과 적절한 활용이 중요한 시대적 과제로 떠오르고 있습니다."
    )
    keyword_ratio = 0.1  # 키워드 비율 설정
    a = gpt_api_call(gpt_api_key, input_text, keyword_ratio)
    print(a)
    print(type(a))
    print(len(a))




# /로 구분된 글에서 중요한 단어 찾기 (근데 이거 잘 안 됨)
'''prompt = f"""
    Analyze the following text and extract the most important keywords exactly as they appear in the text. 
    The keywords should:
    1. Summarize the key concepts of the material.
    2. Be critical for understanding the main ideas presented in the text.
    3. Do not Include numeric information only if it represents a year (e.g., 2023).

    The output must be a simple, comma-separated string with no additional formatting or text. 
    Ensure the number of keywords matches exactly {num_keywords}.

    Examples:
    - English: Artificial Intelligence, GPT models, NLP, 2023
    - Korean: 인공지능, GPT 모델, NLP, 2023

    Text:
    {input_text}

    Return exactly {num_keywords} keywords without modifying or translating them from the original text.
    """
'''

