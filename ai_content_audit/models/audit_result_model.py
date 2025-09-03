from typing import Optional
from pydantic import BaseModel, Field, model_validator
from ai_content_audit.models.audit_decision_model import AuditDecision
from uuid import UUID, uuid4


class AuditResult(BaseModel):
    """
    审核结果模型：封装单个审核的完整信息。

    用于 audit_batch 的输出，便于区分不同文本和审核项的结果。
    """

    id: UUID = Field(default_factory=uuid4, description="审核结果的全局唯一ID（UUID4）")
    batch_id: Optional[UUID] = Field(
        None, description="批次ID（同一批次审核共用，便于分组和追踪）"
    )
    text_id: UUID = Field(..., description="对应的文本ID")
    item_id: UUID = Field(..., description="对应的审核项ID")
    item_name: str = Field(..., description="审核项名称（冗余，便于展示）")
    text_excerpt: str = Field(..., description="审核文本的节选（前100字符），用于展示")
    decision: AuditDecision = Field(
        ..., description="审核决策（包含 choice 和 reason）"
    )

    @model_validator(mode="after")
    def _set_text_excerpt(self) -> "AuditResult":
        """自动生成文本节选（前100字符）"""
        if self.text_excerpt:
            self.text_excerpt = self.text_excerpt[:100]
        return self
