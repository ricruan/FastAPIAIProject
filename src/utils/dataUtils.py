import json
import copy
from typing import Type, TypeVar, Any, Dict, List
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
        jstr_to_dict(json_str)
        return True
    except json.JSONDecodeError:
        return False

def jstr_to_dict(json_str):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return json.loads(json_str.replace('\t', '\\t').replace('\n', '\\n'))


def dict_2_json(data: Dict[str, Any], ensure_ascii: bool = False, indent: int = None) -> str:
    """
    将单个字典转换为 JSON 字符串

    参数:
        data: 要转换的字典
        ensure_ascii: 是否确保 ASCII 编码 (默认 False，允许非 ASCII 字符如中文)
        indent: 缩进空格数 (None 表示不缩进)

    返回:
        JSON 格式的字符串

    异常:
        如果输入不是字典或 JSON 序列化失败，抛出 ValueError
    """
    if not isinstance(data, dict):
        raise ValueError("输入必须是字典类型")

    try:
        return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)
    except (TypeError, ValueError) as e:
        raise ValueError(f"JSON 序列化失败: {str(e)}")


def dict_list_2_json(data_list: List[Dict[str, Any]], ensure_ascii: bool = False, indent: int = None) -> str:
    """
    将字典列表转换为 JSON 字符串

    参数:
        data_list: 要转换的字典列表
        ensure_ascii: 是否确保 ASCII 编码 (默认 False，允许非 ASCII 字符如中文)
        indent: 缩进空格数 (None 表示不缩进)

    返回:
        JSON 格式的字符串

    异常:
        如果输入不是列表或包含非字典元素，或 JSON 序列化失败，抛出 ValueError
    """
    if not isinstance(data_list, list):
        raise ValueError("输入必须是列表类型")

    if not all(isinstance(item, dict) for item in data_list):
        raise ValueError("列表中的所有元素必须是字典类型")

    try:
        return json.dumps(data_list, ensure_ascii=ensure_ascii, indent=indent)
    except (TypeError, ValueError) as e:
        raise ValueError(f"JSON 序列化失败: {str(e)}")


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


def translate_dict_keys_4_list(data_list, key_mapping):
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

            translated_item = translate_dict_keys_4_dict(item, key_mapping)
            translated_list.append(translated_item)

        return translated_list
    except Exception as e:
        return data_list

def translate_dict_keys_4_dict(data_dict, key_mapping):
    """
    遍历字典，将键名从英文替换为中文

    参数:
        data_dict: 包含字典的字典
        key_mapping: 英文键名到中文键名的映射字典

    返回:
        转换后的字典
    """
    try:
        translated_item = {}
        for key, value in data_dict.items():
            # 如果键在映射关系中，使用中文键名，否则保留原键名
            new_key = key_mapping.get(key, key)
            translated_item[new_key] = value
        return translated_item
    except Exception as e:
        return data_dict

def nvl(value, default):
    """
    类似于SQL中的NVL函数
    :param value:
    :param default:
    :return:
    """
    return default if not value else value


