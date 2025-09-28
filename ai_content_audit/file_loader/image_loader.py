import base64
from pathlib import Path


def load_image(image_path: str | Path) -> str:
    """
    加载图像文件并转换为大模型图像输入格式

    支持格式：JPEG, PNG, BMP, TIFF, WebP, HEIC

    参数:
        image_path (str): 图片文件路径

    返回:
        str: 格式为 "data:{mime_type};base64,{base64_encoded}" 的字符串

    异常:
        FileNotFoundError: 文件不存在
        ValueError: 不支持的文件格式
    """
    path = Path(image_path)

    # 验证文件存在性和可读性
    if not path.exists():
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    if not path.is_file():
        raise ValueError(f"路径不是文件: {image_path}")

    # 支持的图像格式映射（扩展名 -> MIME类型）
    supported_formats = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".jpe": "image/jpeg",
        ".png": "image/png",
        ".bmp": "image/bmp",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
        ".webp": "image/webp",
        ".heic": "image/heic",
    }

    # 检查文件格式支持性
    ext = path.suffix.lower()
    if ext not in supported_formats:
        raise ValueError(f"不支持的图像格式: {ext}")

    # 读取图片文件并转换为base64
    with open(path, "rb") as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data).decode("utf-8")

    # 获取MIME类型
    mime_type = supported_formats.get(ext, "image/jpeg")

    # 创建大模型图像输入格式的字符串
    return f"data:{mime_type};base64,{base64_encoded}"
