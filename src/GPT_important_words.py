import json
import openai
from openai import OpenAI
import re


# GPT API key 읽어들이는 함수
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
    path = './tests/materials/gpt_api_key.json'
    gpt_api_key = load_api_key(path)

