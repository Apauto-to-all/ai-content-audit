from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Literal, Mapping, Optional, Sequence, Union
from pydantic import ValidationError
from ai_content_audit.loader.media_loader import MediaLoader
from ai_content_audit.models import AuditContent


class AuditContentLoader:
    """
    待审核内容数据加载器：用于加载待审核的内容。

    功能
    - 支持从字符串直接创建。
    - 支持从目录批量加载待审核文件。
    - 可自定义读取编码，默认 utf-8。

    支持的文件类型：
    - 文本文件：{"txt", "md"}
    - 图像文件：{"bmp", "jpe", "jpeg", "jpg", "png", "tif", "tiff", "webp", "heic"}

    使用方法：
    - 创建内容：使用 create() 方法直接创建。
    - 从字典加载：使用 from_dict() 方法从字典数据加载。
    - 从文件加载：使用 from_file() 方法从单个文件加载。
    - 从路径加载：使用 from_path() 方法从路径加载。
    - 批量加载：使用 from_paths() 方法批量加载多个路径。
    """

    # 公开 API ---------------------------------------------------------------
    @staticmethod
    def create(
        content: str,
        *,
        source: Optional[str] = None,
        file_type: Literal["text", "image"] = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditContent:
        """
        直接创建一个 AuditContent 对象。

        参数
        - content (str): 必需，内容。
        - source (Optional[str]): 可选，内容来源（如文件路径/URL）。
        - file_type (Literal["text", "image"]): 文件类型，默认为 "text"。
        - metadata (Optional[Dict[str, Any]]): 可选，附加元信息。

        返回
        - AuditContent: 待审核内容模型对象，可直接用于审核管理器。

        示例：
        >>> from ai_content_audit import loader
        >>> audit_content = loader.audit_data.create(
        ...     content="这是一个示例文本，用于演示审核功能。",
        ...     source="main.py 示例",
        ...     file_type="text",
        ... )
        """
        return AuditContent(
            content=content, source=source, file_type=file_type, metadata=metadata
        )

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> AuditContent:
        """
        从字典加载 AuditContent，键包含 [content, source, file_type, metadata]。

        参数
        - data (Mapping[str, Any]): 包含 AuditContent 字段的字典
          - content (str): 必需，内容
          - source (Optional[str]): 可选，内容来源
          - file_type (Literal["text", "image"]): 文件类型，默认为 "text"。
          - metadata (Optional[Dict[str, Any]]): 可选，附加元信息

        返回
        - AuditContent: 待审核内容模型对象，可直接用于审核管理器。

        异常
        - ValidationError: 字段类型或内容不合法
        - ValueError: 无效的 AuditContent 字段

        示例：
        >>> from ai_content_audit import loader
        >>> data = {
        ...     "content": "这是一个示例文本，用于演示审核功能。",
        ...     "source": "main.py 示例",
        ...     "file_type": "text",
        ... }
        >>> audit_content = loader.audit_data.from_dict(data)
        """
        try:
            meta = data.get("metadata")
            if meta is not None and not isinstance(meta, dict):
                meta = None
            return AuditContent(
                content=data.get("content"),
                source=data.get("source"),
                file_type=data.get("file_type", "text"),
                metadata=meta,
            )
        except ValidationError:
            raise
        except Exception as e:
            raise ValueError(f"无效的字段: {e}") from e

    @staticmethod
    def from_file(
        path: Union[str, Path],
        *,
        encoding: str = "utf-8",
    ) -> AuditContent:
        """
        从单个文件加载文本内容

        参数
        - path (Union[str, Path]): 文件路径。
        - encoding (str): 文件读取编码，默认 "utf-8"。

        返回
        - AuditContent: 带 source=文件路径 的内容模型。

        异常
        - FileNotFoundError: 文件不存在。
        - ValueError: 不支持的文件类型。

        示例：
        >>> from ai_content_audit import loader
        >>> audit_content = loader.audit_data.from_file("example.txt")
        """
        result = MediaLoader.from_file(path, encoding=encoding)
        return result

    @staticmethod
    def from_path(
        path: Union[str, Path],
        *,
        recursive: bool = True,
        encoding: str = "utf-8",
    ) -> List[AuditContent]:
        """
        从路径加载待审核内容：
        - 若为文件：行为同 from_file。
        - 若为目录：收集其中符合要求文件，返回列表。

        参数
        - path (Union[str, Path]): 文件或目录路径。
        - recursive (bool): 当 path 为目录时，是否递归查找（默认 True，使用 rglob）。
        - encoding (str): 文件读取编码，默认 "utf-8"。

        返回
        - List[AuditContent]: 待审核内容模型列表（按文件路径排序）。

        异常
        - FileNotFoundError: 路径不存在。

        示例：
        >>> from ai_content_audit import loader
        >>> audit_content_list = loader.audit_data.from_path("documents/")
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        if p.is_file():
            return [AuditContentLoader.from_file(p, encoding=encoding)]

        texts: List[AuditContent] = []
        files: List[Path] = []
        # 收集所有文件，不限制扩展名
        files.extend(list(p.rglob("*") if recursive else p.glob("*")))
        # 过滤出文件（排除目录）
        files = [fp for fp in files if fp.is_file()]
        for fp in sorted(files):
            try:
                result = AuditContentLoader.from_file(fp, encoding=encoding)
                texts.append(result)
            except ValueError:
                # 跳过不支持的文件类型
                continue
        return texts

    @staticmethod
    def from_paths(
        paths: Sequence[Union[str, Path]],
        *,
        recursive: bool = True,
        encoding: str = "utf-8",
    ) -> List[AuditContent]:
        """
        批量加载多个路径（文件或目录可混合）。

        参数
        - paths (Sequence[Union[str, Path]]): 路径序列。
        - recursive (bool): 遍历目录时是否递归（默认 True）。
        - encoding (str): 文件读取编码，默认 "utf-8"。

        返回
        - List[AuditContent]: 汇总的待审核内容模型列表。

        示例：
        >>> from ai_content_audit import loader
        >>> audit_content_list = loader.audit_data.from_paths(["file1.txt", "dir/"])
        """
        all_texts: List[AuditContent] = []
        for p in paths:
            all_texts.extend(
                AuditContentLoader.from_path(p, recursive=recursive, encoding=encoding)
            )
        return all_texts
