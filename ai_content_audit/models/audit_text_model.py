from __future__ import annotations
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator


class AuditText(BaseModel):
    """待审核文本的数据模型。

    字段
    - id: 全局唯一ID（UUID4，随机生成）。
    - content: 文本内容（必须）。
    - source: 文本来源（如文件路径、URL、渠道名）。
    - metadata: 额外的元信息（自由键值对）。
    """

    id: UUID = Field(default_factory=uuid4, description="全局唯一ID（UUID4）")
    content: str = Field(..., description="文本内容")
    source: Optional[str] = Field(
        default=None, description="文本来源（文件路径/URL 等）"
    )
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="额外元信息")
