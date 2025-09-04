from __future__ import annotations
from typing import Any, Dict, Optional, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class AuditContent(BaseModel):
    """待审核内容的数据模型。

    字段
    - id: 全局唯一ID（UUID4，随机生成）。
    - content: 内容（必须），如果是图像则为 base64 编码字符串。
    - source: 内容来源（如文件路径、URL、渠道名）。
    - file_type: 文件类型（"text" 或 "image"）。
    - metadata: 额外的元信息（自由键值对）。
    """

    id: UUID = Field(default_factory=uuid4, description="全局唯一ID（UUID4）")
    content: str = Field(..., description="内容")
    source: Optional[str] = Field(
        default=None, description="内容来源（文件路径/URL 等）"
    )
    file_type: Literal["text", "image"] = Field(default="text", description="内容类型")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="额外元信息")
