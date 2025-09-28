from typing import Any, Dict, Literal, Mapping, Optional
from pydantic import ValidationError
from ai_content_audit.models import AuditContent


class AuditContentLoader:
    """
    待审核内容数据加载器：用于加载待审核的内容。

    功能
    - 支持从字符串直接创建。
    - 支持从目录批量加载待审核文件。
    - 可自定义读取编码，默认 utf-8。

    使用方法：
    - 创建内容：使用 create() 方法直接创建。
    - 从字典加载：使用 from_dict() 方法从字典数据加载。
    """

    # 公开 API ---------------------------------------------------------------
    @staticmethod
    def create(
        content: str,
        file_type: Literal["text", "image"] = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditContent:
        """
        直接创建一个 AuditContent 对象。

        参数
        - content (str): 必需，内容，如果是图片则
        - file_type (Literal["text", "image"]): 文件类型，默认为 "text"。
        - metadata (Optional[Dict[str, Any]]): 可选，附加元信息。

        返回
        - AuditContent: 待审核内容模型对象，可直接用于审核管理器。

        示例：
        >>> from ai_content_audit import loader
        >>> audit_content = loader.audit_data.create(
        ...     content="这是一个示例文本，用于演示审核功能。",
        ...     file_type="text",
        ... )
        """
        return AuditContent(content=content, file_type=file_type, metadata=metadata)

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> AuditContent:
        """
        从字典加载 AuditContent，键包含 [content, file_type, metadata]。

        参数
        - data (Mapping[str, Any]): 包含 AuditContent 字段的字典
          - content (str): 必需，内容
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
                file_type=data.get("file_type", "text"),
                metadata=meta,
            )
        except ValidationError:
            raise
        except Exception as e:
            raise ValueError(f"无效的字段: {e}") from e
