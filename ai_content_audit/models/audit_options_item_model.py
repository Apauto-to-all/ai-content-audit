from typing import Dict, Optional
from uuid import UUID, uuid5, NAMESPACE_URL
from pydantic import BaseModel, Field, field_validator, model_validator


class AuditOptionsItem(BaseModel):
    """单个审核项的定义：名称、判定依据说明、以及可选项集合（标签->说明）。"""

    id: Optional[UUID] = Field(
        default=None,
        description="审核项的全局唯一ID（基于 name 和 options 的 keys 生成）",
    )
    name: str = Field(..., description="审核项名称")
    instruction: str = Field(..., description="该审核项的审核理由/判定依据说明")
    options: Dict[str, str] = Field(..., description="选项映射：标签 -> 选项含义说明")

    @classmethod
    def _generate_stable_id(cls, name: str, options: Dict[str, str]) -> UUID:
        """基于 name 和 options 的 keys 生成稳定的 UUID5"""
        # 只使用 options 的键（标签），排除描述性值，确保 ID 稳定且简洁
        options_keys_str = "|".join(sorted(options.keys()))
        key = f"{name}|{options_keys_str}"
        return uuid5(NAMESPACE_URL, key)

    @model_validator(mode="after")
    def _set_stable_id(self) -> "AuditOptionsItem":
        """自动生成稳定的 ID"""
        if self.id is None:
            self.id = self._generate_stable_id(self.name, self.options)
        return self

    @field_validator("options")
    @classmethod
    def _validate_options(cls, v: Dict[str, str]) -> Dict[str, str]:
        if not v or not isinstance(v, dict):
            raise ValueError("options 不能为空")
        for k, desc in v.items():
            if not k or not isinstance(k, str):
                raise ValueError("options 的键必须为非空字符串")
            if not isinstance(desc, str) or not desc.strip():
                raise ValueError(f"选项 {k} 的说明不能为空")
        return v
