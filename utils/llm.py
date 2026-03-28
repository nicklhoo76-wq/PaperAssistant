import os
from openai import OpenAI

# 从环境变量读取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

def ask_llm(prompt):
    response = client.chat.completions.create(
        model="deepseek-chat",   # DeepSeek 模型
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content