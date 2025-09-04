from typing import Dict, List
from ai_content_audit.models import AuditOptionsItem, AuditDecision, AuditContent
from ai_content_audit.prompts.structured_output_prompt import structured_output
from ai_content_audit.prompts.system_prompt import get_system_prompt


def build_messages(
    content: AuditContent, item: AuditOptionsItem
) -> List[Dict[str, str]]:
    """构建消息列表，用于大模型审核文本或图片"""
    options_list = "\n".join([f"- {k}：{v}" for k, v in item.options.items()])

    if content.file_type == "text":
        # 文本审核
        user_content = (
            f"审核项：{item.name}\n"
            f"审核理由/依据：{item.instruction}\n"
            f"可选项（标签：含义）：\n{options_list}\n\n"
            f"待审核文本：\n{content.content}\n\n"
            f"输出要求：{structured_output(AuditDecision)}\n"
            "如果无法明确判断且存在‘不确定’或类似选项，请选择该选项。"
        )
    elif content.file_type == "image":
        # 图片审核（使用 vision API）
        user_content = [
            {
                "type": "image_url",
                "image_url": {"url": content.content},  # content 为 base64 格式
            },
            {
                "type": "text",
                "text": (
                    f"审核项：{item.name}\n"
                    f"审核理由/依据：{item.instruction}\n"
                    f"可选项（标签：含义）：\n{options_list}\n\n"
                    "请分析提供的图像内容，并根据审核项给出判断。\n\n"
                    f"输出要求：{structured_output(AuditDecision)}\n"
                    "如果无法明确判断且存在‘不确定’或类似选项，请选择该选项。"
                ),
            },
        ]
    else:
        raise ValueError(f"不支持的文件类型: {content.file_type}")

    return [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": user_content},
    ]
