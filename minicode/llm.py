from openai import OpenAI
from minicode.config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)


def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "你是 MiniCode 多 Agent 系统中的专业 AI 成员，请严格完成你的角色任务。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content