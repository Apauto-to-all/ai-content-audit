from typing import Dict, List
from ai_content_audit.models import AuditOptionsItem, AuditDecision, AuditContent
from structured_output_prompt import generate_structured_prompt


def build_messages(
    content: AuditContent, item: AuditOptionsItem
) -> List[Dict[str, str]]:
    """构建消息列表，用于大模型审核文本或图片"""
    options_list = "\n".join([f"- {k}：{v}" for k, v in item.options.items()])

    output_prompt = generate_structured_prompt(AuditDecision, language="zh")

    if content.file_type == "text":
        # 文本审核
        user_content = (
            f"审核项：{item.name}\n"
            f"审核理由/依据：{item.instruction}\n"
            f"可选项（标签：含义）：\n{options_list}\n\n"
            f"待审核文本：\n{content.content}\n\n"
            f"输出要求：{output_prompt}\n"
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
                    f"输出要求：{output_prompt}\n"
                    "如果无法明确判断且存在‘不确定’或类似选项，请选择该选项。"
                ),
            },
        ]
    else:
        raise ValueError(f"不支持的文件类型: {content.file_type}")

    return [
        {
            "role": "system",
            "content": (
                "你是内容审核助手。请严格依据提供的审核项说明与选项定义，"
                "对输入文本做出唯一选择，并给出简短理由。"
                "只允许从提供的选项标签中选择一个。"
            ),
        },
        {"role": "user", "content": user_content},
    ]
