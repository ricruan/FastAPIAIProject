import json
import copy
from typing import Type, TypeVar, Any
from urllib.parse import urlparse

T = TypeVar('T')

def is_valid_json(json_str):
    """
     校验json字符串能否正常转化成json
    :param json_str: json字符串
    :return:  布尔值
    """
    if not isinstance(json_str, str):
        return False
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False


def is_valid_url(url_str: str) -> bool:
    """
    严格校验输入的字符串是否是有效的URL

    要求:
    - 必须包含scheme(如http/https)
    - 必须包含netloc(域名或IP)
    - 可以包含path, params, query, fragment等可选部分

    :param url_str: 待校验的字符串
    :return: 如果是有效URL返回True，否则返回False
    """
    try:
        result = urlparse(url_str)
        # 严格检查: 必须有scheme和netloc
        if not all([result.scheme, result.netloc]):
            return False

        # 可选: 检查scheme是否是http或https
        # if result.scheme not in ('http', 'https'):
        #     return False

        return True
    except ValueError:
        return False


def translate_dict_keys(data_list, key_mapping):
    """
    遍历列表中的字典，将键名从英文替换为中文

    参数:
        data_list: 包含字典的列表
        key_mapping: 英文键名到中文键名的映射字典

    返回:
        转换后的列表
    """
    try:
        translated_list = []

        for item in data_list:
            if not isinstance(item, dict):
                # 如果列表中的元素不是字典，直接添加到结果中
                translated_list.append(item)
                continue

            translated_item = {}
            for key, value in item.items():
                # 如果键在映射关系中，使用中文键名，否则保留原键名
                new_key = key_mapping.get(key, key)
                translated_item[new_key] = value

            translated_list.append(translated_item)

        return translated_list
    except Exception as e:
        return data_list



