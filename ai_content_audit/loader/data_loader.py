from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union
from pydantic import ValidationError
from ai_content_audit.models import AuditText


class AuditTextLoader:
    """
    文本数据加载器：用于加载待审核的文本内容。

    功能
    - 支持从 .txt / .md 单个文件读取文本。
    - 支持从目录批量加载（递归搜集 .txt / .md）。
    - 可自定义读取编码，默认 utf-8。

    使用方法：
    - 创建文本：使用 create() 方法直接创建。
    - 从字典加载：使用 from_dict() 方法从字典数据加载。
    - 从文件加载：使用 from_file() 方法从单个文件加载。
    - 从路径加载：使用 from_path() 方法从路径加载。
    - 批量加载：使用 from_paths() 方法批量加载多个路径。
    - 所有方法返回 AuditText 或 List[AuditText] 对象，可直接用于审核管理器。
    """

    # 公开 API ---------------------------------------------------------------
    @staticmethod
    def create(
        content: str,
        *,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditText:
        """
        直接创建一个 AuditText。

        参数
        - content (str): 必需，文本内容。
        - source (Optional[str]): 可选，文本来源（如文件路径/URL）。
        - metadata (Optional[Dict[str, Any]]): 可选，附加元信息。

        返回
        - AuditText: 构建好的文本模型对象，可直接用于审核管理器。

        示例：
        >>> from ai_content_audit import loader
        >>> text = loader.audit_data.create(
        ...     content="这是一个示例文本，用于演示审核功能。",
        ...     source="main.py 示例",
        ... )
        """
        return AuditText(content=content, source=source, metadata=metadata)

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> AuditText:
        """
        从字典加载 AuditText，键包含 content[, source, metadata]。

        参数
        - data (Mapping[str, Any]): 包含 AuditText 字段的字典
          - content (str): 必需，文本内容
          - source (Optional[str]): 可选，文本来源
          - metadata (Optional[Dict[str, Any]]): 可选，附加元信息

        返回
        - AuditText: 构建好的文本模型对象，可直接用于审核管理器。

        异常
        - ValidationError: 字段类型或内容不合法
        - ValueError: 无效的 AuditText 字段

        示例：
        >>> from ai_content_audit import loader
        >>> data = {
        ...     "content": "这是一个示例文本，用于演示审核功能。",
        ...     "source": "main.py 示例",
        ... }
        >>> text = loader.audit_data.from_dict(data)
        """
        try:
            meta = data.get("metadata")
            if meta is not None and not isinstance(meta, dict):
                meta = None
            return AuditText(
                content=data.get("content"),
                source=data.get("source"),
                metadata=meta,
            )
        except ValidationError:
            raise
        except Exception as e:
            raise ValueError(f"无效的 AuditText 字段: {e}") from e

    @staticmethod
    def from_file(
        path: Union[str, Path],
        *,
        encoding: str = "utf-8",
    ) -> AuditText:
        """
        从单个文件加载文本内容（仅支持 .txt / .md）。

        参数
        - path (Union[str, Path]): 文件路径。
        - encoding (str): 文件读取编码，默认 "utf-8"。

        返回
        - AuditText: 带 source=文件路径 的文本模型。

        异常
        - FileNotFoundError: 文件不存在。
        - ValueError: 不支持的文件类型。

        示例：
        >>> from ai_content_audit import loader
        >>> text = loader.audit_data.from_file("example.txt")
        """
        p = Path(path)
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(p)
        if p.suffix.lower() not in {".txt", ".md"}:
            raise ValueError(f"不支持的文件类型: {p.suffix}（仅支持 .txt / .md）")
        content = _read_and_normalize_text(p, encoding=encoding)
        return AuditTextLoader.create(content, source=str(p))

    @staticmethod
    def from_path(
        path: Union[str, Path],
        *,
        recursive: bool = True,
        encoding: str = "utf-8",
    ) -> List[AuditText]:
        """
        从路径加载文本：
        - 若为文件：行为同 from_file。
        - 若为目录：收集其中的 .txt/.md 文件（递归由参数控制），逐个读取并返回文本列表。

        参数
        - path (Union[str, Path]): 文件或目录路径。
        - recursive (bool): 当 path 为目录时，是否递归查找（默认 True，使用 rglob）。
        - encoding (str): 文件读取编码，默认 "utf-8"。

        返回
        - List[AuditText]: 文本模型列表（按文件路径排序）。

        异常
        - FileNotFoundError: 路径不存在。

        示例：
        >>> from ai_content_audit import loader
        >>> texts = loader.audit_data.from_path("documents/")
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        if p.is_file():
            return [AuditTextLoader.from_file(p, encoding=encoding)]

        patterns = ["*.txt", "*.md"]
        texts: List[AuditText] = []
        files: List[Path] = []
        for pattern in patterns:
            files.extend(list(p.rglob(pattern) if recursive else p.glob(pattern)))
        for fp in sorted(files):
            texts.append(
                AuditTextLoader.create(
                    _read_and_normalize_text(fp, encoding=encoding),
                    source=str(fp),
                )
            )
        return texts

    @staticmethod
    def from_paths(
        paths: Sequence[Union[str, Path]],
        *,
        recursive: bool = True,
        encoding: str = "utf-8",
    ) -> List[AuditText]:
        """
        批量加载多个路径（文件或目录可混合）。

        参数
        - paths (Sequence[Union[str, Path]]): 路径序列。
        - recursive (bool): 遍历目录时是否递归（默认 True）。
        - encoding (str): 文件读取编码，默认 "utf-8"。

        返回
        - List[AuditText]: 汇总的文本模型列表。

        示例：
        >>> from ai_content_audit import loader
        >>> texts = loader.audit_data.from_paths(["file1.txt", "dir/"])
        """
        all_texts: List[AuditText] = []
        for p in paths:
            all_texts.extend(
                AuditTextLoader.from_path(p, recursive=recursive, encoding=encoding)
            )
        return all_texts


def _read_and_normalize_text(path: Path, *, encoding: str = "utf-8") -> str:
    """读取文件文本并规范化换行符为 "\n"。"""
    data = path.read_text(encoding=encoding)
    data = data.replace("\r\n", "\n").replace("\r", "\n")
    return data
