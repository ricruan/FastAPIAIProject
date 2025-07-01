import json


def get_value_from_stream_response_by_key(response: str, key: str) -> str:
    """
    从SSE流式响应中提取指定key的值
    :param response: 原始SSE响应字符串
    :param key: 需要提取的key
    :return:
    """
    # 1. 提取JSON部分（去掉"data: "前缀，如果存在）
    json_str = response[6:].strip() if response.startswith("data: ") else response.strip()
    # 2. 验证并解析JSON
    try:
        json_data = json.loads(json_str)
    except json.JSONDecodeError:
        return ""  # 无效JSON直接返回空

    # 3. 提取answer字段（如果存在）
    return json_data.get(key, "")


def dify_stream_response_handler(response: str) -> str:
    """
    处理Dify的SSE流式响应，提取有效的answer字段内容。

    Args:
        response: 原始SSE响应字符串（可能以"data: "开头，或直接是JSON字符串）

    Returns:
        提取到的answer内容（如果存在），否则返回空字符串
    """
    return get_value_from_stream_response_by_key(response, "answer")


def dify_get_conversation_id_from_stream(response: str) -> str:
    """
    从SSE流式响应中提取conversation_id字段
    :param response: 原始SSE响应字符串
    :return:
    """
    return get_value_from_stream_response_by_key(response, "conversation_id")