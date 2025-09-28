"""
AI内容审核系统 - 基础用法示例

这个示例展示了如何使用 AI 内容审核系统的基本功能，包括：
- 环境设置
- 文本内容审核
- 敏感信息检测
- 广告内容检测
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径并加载环境变量
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
load_dotenv()

from openai import OpenAI
from ai_content_audit import AuditManager, loader


def setup_environment():
    """
    设置环境变量和客户端

    返回:
        OpenAI: 配置好的 OpenAI 客户端
    """
    # 从环境变量获取配置
    base_url = os.getenv(
        "DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    api_key = os.getenv("DASHSCOPE_API_KEY")

    if not api_key:
        raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量")

    # 创建 OpenAI 客户端
    client = OpenAI(base_url=base_url, api_key=api_key)

    return client


def basic_text_audit():
    """
    基础单文本审核示例

    演示如何使用单个文本和单个审核项进行审核
    """
    print("=== 基础单文本审核示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 创建待审核文本
    text_content = """
    这是一段示例文本，包含一些敏感信息。
    我的电话号码是 138-1234-5678，邮箱是 test@example.com。
    请不要泄露这些个人信息。
    """

    # 创建审核内容
    audit_content = loader.audit_data.create(content=text_content, file_type="text")

    # 创建敏感信息检测审核项
    sensitive_item = loader.options_item.create(
        name="敏感信息检测",
        instruction="检查文本中是否包含电话号码、邮箱地址等个人敏感信息",
        options={
            "包含": "检测到敏感信息",
            "不包含": "未检测到敏感信息",
            "不确定": "无法判断是否包含敏感信息",
        },
    )

    # 执行审核
    result = audit_manager.audit_one(
        content=audit_content, item=sensitive_item, model="qwen-plus"
    )

    # 输出结果
    print(f"审核结果: {result.decision.choice}")
    print(f"审核说明: {result.decision.reason}")
    print()


def sensitive_information_detection():
    """
    敏感信息检测示例

    演示如何检测不同类型的敏感信息
    """
    print("=== 敏感信息检测示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 测试文本列表
    test_texts = [
        "我的身份证号是 110101199001011234",
        "请联系我：138-1234-5678",
        "发送邮件到 admin@company.com",
        "这是一段普通的文本，没有敏感信息",
    ]

    # 创建敏感信息检测审核项
    sensitive_item = loader.options_item.create(
        name="个人敏感信息检测",
        instruction="检查文本中是否包含身份证号、电话号码、邮箱地址等个人敏感信息",
        options={
            "包含": "检测到敏感信息",
            "不包含": "未检测到敏感信息",
            "不确定": "无法判断是否包含敏感信息",
        },
    )

    for i, text in enumerate(test_texts, 1):
        print(f"\n测试文本 {i}: {text}")

        # 创建审核内容
        audit_content = loader.audit_data.create(content=text, file_type="text")

        # 执行审核
        result = audit_manager.audit_one(
            content=audit_content, item=sensitive_item, model="qwen-plus"
        )

        print(f"  审核结果: {result.decision.choice}")
        print(f"  审核说明: {result.decision.reason}")

    print()


def advertisement_detection():
    """
    广告内容检测示例

    演示如何检测广告内容
    """
    print("=== 广告内容检测示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 测试文本列表
    test_texts = [
        "限时优惠！购买我们的产品享受8折优惠，赶快行动吧！",
        "这是一篇技术博客文章，讨论人工智能的发展趋势",
        "新品上市！买一送一，仅限今天！立即下单！",
        "关于项目进度的汇报文档",
    ]

    # 创建广告内容检测审核项
    ad_item = loader.options_item.create(
        name="广告内容检测",
        instruction="检查文本是否是广告内容，包含促销、限时优惠、购买等关键词",
        options={
            "是广告": "检测到广告内容",
            "不是广告": "未检测到广告内容",
            "不确定": "无法判断是否是广告",
        },
    )

    for i, text in enumerate(test_texts, 1):
        print(f"\n测试文本 {i}: {text}")

        # 创建审核内容
        audit_content = loader.audit_data.create(content=text, file_type="text")

        # 执行审核
        result = audit_manager.audit_one(
            content=audit_content, item=ad_item, model="qwen-plus"
        )

        print(f"  审核结果: {result.decision.choice}")
        print(f"  审核说明: {result.decision.reason}")

    print()


def main():
    """
    主函数，运行所有基础示例
    """
    try:
        # 运行基础单文本审核
        basic_text_audit()

        # 运行敏感信息检测
        sensitive_information_detection()

        # 运行广告内容检测
        advertisement_detection()

        print("=== 所有基础示例执行完成 ===")

    except Exception as e:
        print(f"执行示例时出错: {e}")
        print("请检查环境变量配置是否正确")


if __name__ == "__main__":
    main()
