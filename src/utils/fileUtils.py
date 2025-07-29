import os


def generate_unique_filename(directory: str, base_filename: str, extension: str) -> str:
    """
    生成唯一的文件名，如果存在同名文件则添加(1)、(2)等后缀

    Args:
        directory: 文件存储目录
        base_filename: 文件基本名称（不含扩展名）
        extension: 文件扩展名（包含点号，如".jpg"）

    Returns:
        唯一的文件名
    """
    # 初始文件名
    filename = f"{base_filename}{extension}"
    counter = 1

    # 检查文件是否存在，如果存在则添加数字后缀
    while os.path.exists(os.path.join(directory, filename)):
        filename = f"{base_filename}({counter}){extension}"
        counter += 1

    return filename