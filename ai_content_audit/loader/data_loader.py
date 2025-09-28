from typing import Any, Dict, Literal, Mapping, Optional
from pydantic import ValidationError
from ai_content_audit.models import AuditContent


class AuditContentLoader:
    """
    待审核内容数据加载器：用于加载待审核的内容。

    功能
    - 支持从字符串直接创建待审核内容。
    - 支持从字典数据加载待审核内容。

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
        >>> # 创建文本待审核内容
        >>> audit_content_text = loader.audit_data.create(
        ...     content="这是一个示例文本，用于演示审核功能。",
        ...     file_type="text",
        ... )
        >>> # 创建图像待审核内容
        >>> # 加载图像文件，将其转化为待审核图像数据
        >>> image_data = file_loader.load_image("path/to/image.jpg")
        >>> audit_content_image = loader.audit_data.create(
        ...     content=image_data,
        ...     file_type="image",
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
        >>> # 创建文本待审核内容
        >>> data = {
        ...     "content": "这是一个示例文本，用于演示审核功能。",
        ...     "file_type": "text",
        ... }
        >>> audit_content_text = loader.audit_data.from_dict(data)
        >>> # 创建图像待审核内容
        >>> # 加载图像文件，将其转化为待审核图像数据
        >>> image_data = file_loader.load_image("path/to/image.jpg")
        >>> data = {
        ...     "content": image_data,
        ...     "file_type": "image",
        ... }
        >>> audit_content_image = loader.audit_data.from_dict(data)
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
