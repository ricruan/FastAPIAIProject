from openai import OpenAI
from typing import List, Dict, Any, Optional, Union, Literal

def get_deepseek_completion(
    messages: List[Dict[str, str]], 
    stream: bool = False,
    model: str = "deepseek-chat",
    api_key: str = "sk-646171ae9662439cbc8d41da59188e2a",
    base_url: str = "https://api.deepseek.com"
) -> Any:
    """
    调用 Deepseek API 获取聊天完成结果
    
    Args:
        messages: 消息列表，每个消息是一个包含 'role' 和 'content' 的字典
        stream: 是否使用流式响应，默认为 False
        model: 使用的模型名称，默认为 "deepseek-chat"
        api_key: Deepseek API 密钥
        base_url: Deepseek API 基础 URL
        
    Returns:
        OpenAI API 的响应对象
    """
    # 创建 OpenAI 客户端
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 调用 API 获取完成结果
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream
    )
    
    return response

# 示例用法
if __name__ == "__main__":
    # 示例消息
    example_messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "你好，你是谁"},
    ]
    
    # 调用函数获取响应
    response = get_deepseek_completion(example_messages)
    print(response)