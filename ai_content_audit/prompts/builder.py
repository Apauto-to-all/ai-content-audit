from typing import Dict, List
from ai_content_audit.models import AuditOptionsItem, AuditDecision
from ai_content_audit.prompts.structured_output_prompt import structured_output
from ai_content_audit.prompts.system_prompt import get_system_prompt


def build_messages(text: str, item: AuditOptionsItem) -> List[Dict[str, str]]:
    """构建消息列表，用于大模型审核文本"""
    options_list = "\n".join([f"- {k}：{v}" for k, v in item.options.items()])
    user = (
        f"审核项：{item.name}\n"
        f"审核理由/依据：{item.instruction}\n"
        f"可选项（标签：含义）：\n{options_list}\n\n"
        f"待审核文本：\n{text}\n\n"
        f"输出要求：{structured_output(AuditDecision)}"
        "如果无法明确判断且存在‘不确定’或类似选项，请选择该选项。"
    )
    return [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": user},
    ]
