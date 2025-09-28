"""
基础审核示例

演示如何使用 AuditManager 进行基本的文本审核操作。
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai_content_audit import loader, AuditManager
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 配置 OpenAI 客户端
client = OpenAI(
    base_url=os.getenv(
        "DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    ),
    api_key=os.getenv("DASHSCOPE_API_KEY", ""),
)
model = os.getenv("DASHSCOPE_MODEL", "qwen-plus-2025-07-28")


def basic_single_audit():
    """基础单文本审核示例"""
    print("=== 基础单文本审核示例 ===")

    # 创建审核管理器
    audit_manager = AuditManager(client=client, model=model)

    # 创建审核项
    audit_item = loader.options_item.create(
        name="内容合规性检查",
        instruction="检查文本内容是否符合平台发布标准。",
        options={
            "合规": "内容符合发布标准",
            "不合规": "内容不符合发布标准",
            "需要审核": "需要人工审核",
        },
    )

    # 创建审核文本
    audit_text = loader.audit_data.create(
        content="这是一个正常的用户评论，表达了对产品的满意。",
        source="用户评论",
    )

    # 执行审核
    result = audit_manager.audit_one(audit_text, audit_item)

    print(f"审核项: {result.item_name}")
    print(f"文本: {result.text_excerpt}")
    print(f"决策: {result.decision.choice}")
    print(f"理由: {result.decision.reason}")
    print()


def sensitive_content_audit():
    """敏感信息检测示例"""
    print("=== 敏感信息检测示例 ===")

    audit_manager = AuditManager(client=client, model=model)

    # 敏感信息检测审核项
    audit_item = loader.options_item.create(
        name="敏感信息检测",
        instruction="检查文本中是否包含敏感信息，如个人隐私、联系方式等。",
        options={
            "无敏感信息": "未检测到敏感信息",
            "有敏感信息": "检测到敏感信息",
            "不确定": "无法确定",
        },
    )

    # 包含敏感信息的文本
    audit_text = loader.audit_data.create(
        content="用户张三，电话：13800138000，邮箱：zhangsan@example.com",
        source="用户信息",
    )

    result = audit_manager.audit_one(audit_text, audit_item)

    print(f"审核项: {result.item_name}")
    print(f"文本: {result.text_excerpt}")
    print(f"决策: {result.decision.choice}")
    print(f"理由: {result.decision.reason}")
    print()


def advertisement_detection():
    """广告内容检测示例"""
    print("=== 广告内容检测示例 ===")

    audit_manager = AuditManager(client=client, model=model)

    # 广告检测审核项
    audit_item = loader.options_item.create(
        name="广告内容检测",
        instruction="检查文本是否包含商业广告或营销推广内容。",
        options={
            "非广告": "不包含广告内容",
            "广告": "包含广告内容",
            "软文": "软文营销",
        },
    )

    # 广告文本
    audit_text = loader.audit_data.create(
        content="限时优惠！我们的产品现在8折销售，立即购买享受更多折扣！",
        source="营销内容",
    )

    result = audit_manager.audit_one(audit_text, audit_item)

    print(f"审核项: {result.item_name}")
    print(f"文本: {result.text_excerpt}")
    print(f"决策: {result.decision.choice}")
    print(f"理由: {result.decision.reason}")
    print()


if __name__ == "__main__":
    basic_single_audit()
    sensitive_content_audit()
    advertisement_detection()
