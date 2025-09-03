from pydantic import BaseModel, Field


class AuditDecision(BaseModel):
    """审核决策：仅两个字段——choice(在 options 中的一个) 与 reason(简要理由)。"""

    choice: str = Field(..., description="模型在给定选项中做出的唯一选择（标签）")
    reason: str = Field(..., description="做出该选择的简短理由（引用关键依据）")
