
from openai import OpenAI
# sk-10dcce94da9c4c33b9dd6f709678c65e
#
client = OpenAI(api_key="sk-646171ae9662439cbc8d41da59188e2a", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "你好，你是谁"},
    ],
    stream=True
)

for chunk in response:
    # chunk 是一个 `ChatCompletionChunk` 对象
    if chunk.choices[0].delta.content is not None:
        print(chunk, end="\n", flush=True)  # 实时打印内容