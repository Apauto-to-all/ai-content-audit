from __future__ import annotations
import base64
from pathlib import Path
from typing import List, Union
import filetype
from ai_content_audit.models import AuditContent
import mimetypes
from collections import namedtuple


class SupportedTypes:
    text = {"txt", "md"}
    image = {"bmp", "jpe", "jpeg", "jpg", "png", "tif", "tiff", "webp", "heic"}


FileType = namedtuple("FileType", ["extension", "mime_type"])


def get_file_type(path: Union[str, Path]) -> FileType:
    """
    根据文件路径自动获取文件类型。返回 FileType(extension, mime_type) 结构。
    """
    p = Path(path)
    kind = filetype.guess(str(p))
    if kind:
        return FileType(extension=kind.extension, mime_type=kind.mime)
    else:
        suffix = p.suffix.lower().lstrip(".")
        mime_type, _ = mimetypes.guess_type(str(p))
        return FileType(extension=suffix or "unknown", mime_type=mime_type or "unknown")


class MediaLoader:
    """
    多媒体数据加载器：支持文本、图像
    """

    @staticmethod
    def from_file(path: Union[str, Path], encoding: str = "utf-8") -> AuditContent:
        p = Path(path)
        # 检测文件是否存在
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(f"文件未找到: {p}")

        # 获取文件类型信息
        file_type_info = get_file_type(p)
        if not file_type_info or file_type_info.extension == "unknown":
            raise ValueError(f"无法识别的文件: {file_type_info}")
        elif file_type_info.extension in SupportedTypes.text:
            return TextLoader.from_file(p, encoding=encoding)
        elif file_type_info.extension in SupportedTypes.image:
            return ImageLoader.from_file(
                p, mime_type=file_type_info.mime_type, encoding=encoding
            )
        else:
            raise ValueError(f"不支持的文件类型: {file_type_info.extension}")


class TextLoader:
    """
    文本文件加载器
    """

    @staticmethod
    def from_file(path: Path, encoding: str = "utf-8") -> AuditContent:
        content = path.read_text(encoding=encoding)
        return AuditContent(content=content, source=str(path), file_type="text")


class ImageLoader:
    """
    图像文件加载器
    """

    @staticmethod
    def from_file(path: Path, mime_type: str, encoding: str = "utf-8") -> AuditContent:
        with open(path, "rb") as f:
            img_data = f.read()
            img_base64 = base64.b64encode(img_data).decode(encoding)
        content = f"data:{mime_type};base64,{img_base64}"
        return AuditContent(content=content, source=str(path), file_type="image")
