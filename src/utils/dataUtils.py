import json
import copy
from typing import Type, TypeVar, Any

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


def copy_attributes_to_new_instance(cls: Type[T], source_instance: Any) -> T:
    """
    创建类的新实例，并将源实例的所有同名属性深拷贝到新实例

    Args:
        cls: 目标类（要创建实例的类）
        source_instance: 源实例（从中复制属性的实例）

    Returns:
        目标类的新实例，包含源实例的同名属性（深拷贝）
    """
    # 创建目标类的新实例
    new_instance = cls()

    # 获取源实例的所有属性名
    source_attrs = set(dir(source_instance))

    # 遍历源实例的所有属性
    for attr_name in source_attrs:
        # 跳过特殊方法和私有属性（以__开头和结尾的）
        if attr_name.startswith('__') and attr_name.endswith('__'):
            continue

        # 获取源实例的属性值
        try:
            source_value = getattr(source_instance, attr_name)
        except AttributeError:
            continue

        # 如果目标类也有同名属性，则进行深拷贝赋值
        if hasattr(new_instance, attr_name):
            # 深拷贝属性值
            copied_value = copy.deepcopy(source_value)
            setattr(new_instance, attr_name, copied_value)

    return new_instance