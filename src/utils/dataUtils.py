import json

def is_valid_json(json_str):
    if not isinstance(json_str, str):
        return False
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False