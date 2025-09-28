"""
AI内容审核系统 - 批量审核示例

这个示例展示了如何使用 AI 内容审核系统的批量审核功能，包括：
- 多个文本单个审核项
- 单个文本多个审核项
- 多个文本多个审核项
- 批量审核错误处理
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


def multiple_texts_single_item():
    """
    多个文本单个审核项示例

    演示如何使用单个审核项批量审核多个文本
    """
    print("=== 多个文本单个审核项示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 多个测试文本
    test_texts = [
        "我的电话号码是 138-1234-5678",
        "这是一段普通的文本内容",
        "请联系邮箱 admin@example.com",
        "技术讨论：人工智能应用",
        "身份证号：110101199001011234",
    ]

    # 创建敏感信息检测审核项
    sensitive_item = loader.options_item.create(
        name="敏感信息检测",
        instruction="检查文本中是否包含电话号码、邮箱地址、身份证号等个人敏感信息",
        options={"包含": "检测到敏感信息", "不包含": "未检测到敏感信息"},
    )

    # 创建审核内容列表
    audit_contents = []
    for i, text in enumerate(test_texts, 1):
        audit_content = loader.audit_data.create(
            content=text, file_type="text", metadata={"text_id": i}
        )
        audit_contents.append(audit_content)

    print(f"批量审核 {len(audit_contents)} 个文本")

    # 执行批量审核
    results = audit_manager.audit_batch(
        contents=audit_contents, items=[sensitive_item], model="qwen-plus"
    )

    # 输出结果
    for i, result in enumerate(results, 1):
        print(f"\n文本 {i}: {test_texts[i-1][:30]}...")
        print(f"  审核结果: {result.decision.choice}")
        print(f"  审核说明: {result.decision.reason}")

    print()


def single_text_multiple_items():
    """
    单个文本多个审核项示例

    演示如何使用多个审核项审核单个文本
    """
    print("=== 单个文本多个审核项示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 测试文本
    test_text = """
    新产品促销活动！
    购买我们的AI工具享受限时优惠，联系电话：138-1234-5678
    邮箱咨询：sales@company.com
    赶快行动，数量有限！
    """

    # 创建多个审核项
    sensitive_item = loader.options_item.create(
        name="敏感信息检测",
        instruction="检查文本中是否包含电话号码、邮箱地址等个人敏感信息",
        options={"包含": "检测到敏感信息", "不包含": "未检测到敏感信息"},
    )

    ad_item = loader.options_item.create(
        name="广告内容检测",
        instruction="检查文本是否是广告内容",
        options={"是广告": "检测到广告内容", "不是广告": "未检测到广告内容"},
    )

    quality_item = loader.options_item.create(
        name="内容质量检测",
        instruction="评估文本的内容质量和专业性",
        options={
            "高质量": "内容专业、结构清晰",
            "一般质量": "内容基本合格",
            "低质量": "内容需要改进",
        },
    )

    # 创建审核内容
    audit_content = loader.audit_data.create(content=test_text, file_type="text")

    print(f"测试文本: {test_text[:60]}...")

    # 使用不同审核项进行审核
    items = [sensitive_item, ad_item, quality_item]

    for item in items:
        print(f"\n使用审核项: {item.name}")

        result = audit_manager.audit_one(
            content=audit_content, item=item, model="qwen-plus"
        )

        print(f"  审核结果: {result.decision.choice}")
        print(f"  审核说明: {result.decision.reason}")

    print()


def multiple_texts_multiple_items():
    """
    多个文本多个审核项示例

    演示如何使用多个审核项批量审核多个文本
    """
    print("=== 多个文本多个审核项示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 多个测试文本
    test_texts = [
        "联系电话：138-1234-5678，新品促销限时优惠",
        "技术文档：人工智能系统架构设计",
        "广告内容：买一送一，立即购买！邮箱：contact@example.com",
        "公司介绍：我们专注于AI技术研发",
    ]

    # 创建多个审核项
    sensitive_item = loader.options_item.create(
        name="敏感信息检测",
        instruction="检查文本中是否包含电话号码、邮箱地址等个人敏感信息",
        options={"包含": "检测到敏感信息", "不包含": "未检测到敏感信息"},
    )

    ad_item = loader.options_item.create(
        name="广告内容检测",
        instruction="检查文本是否是广告内容",
        options={"是广告": "检测到广告内容", "不是广告": "未检测到广告内容"},
    )

    # 创建审核内容列表
    audit_contents = []
    for i, text in enumerate(test_texts, 1):
        audit_content = loader.audit_data.create(
            content=text, file_type="text", metadata={"text_id": i}
        )
        audit_contents.append(audit_content)

    print(f"批量审核 {len(audit_contents)} 个文本，使用 2 个审核项")

    # 对每个审核项执行批量审核
    items = [("敏感信息检测", sensitive_item), ("广告内容检测", ad_item)]

    for item_name, item in items:
        print(f"\n=== 使用审核项: {item_name} ===")

        results = audit_manager.audit_batch(
            contents=audit_contents, items=[item], model="qwen-plus"
        )

        for i, result in enumerate(results, 1):
            print(
                f"文本 {i}: {result.decision.choice} - {result.decision.reason[:50]}..."
            )

    print()


def batch_audit_error_handling():
    """
    批量审核错误处理示例

    演示如何处理批量审核中的错误情况
    """
    print("=== 批量审核错误处理示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 包含可能问题的测试文本
    test_texts = [
        "正常文本内容",
        "",  # 空文本
        "包含敏感信息：138-1234-5678",
        "x" * 10000,  # 超长文本
        "正常文本内容2",
    ]

    # 创建审核项
    sensitive_item = loader.options_item.create(
        name="敏感信息检测",
        instruction="检查文本中是否包含敏感信息",
        options={"包含": "检测到敏感信息", "不包含": "未检测到敏感信息"},
    )

    # 创建审核内容列表
    audit_contents = []
    for i, text in enumerate(test_texts, 1):
        try:
            audit_content = loader.audit_data.create(
                content=text, file_type="text", metadata={"text_id": i}
            )
            audit_contents.append(audit_content)
            print(f"文本 {i}: 创建成功")
        except Exception as e:
            print(f"文本 {i}: 创建失败 - {e}")

    print(f"\n成功创建 {len(audit_contents)} 个审核内容")

    # 执行批量审核
    try:
        results = audit_manager.audit_batch(
            contents=audit_contents, items=[sensitive_item], model="qwen-plus"
        )

        print("\n批量审核结果:")
        for i, result in enumerate(results, 1):
            print(f"文本 {i}: {result.decision.choice}")

    except Exception as e:
        print(f"批量审核出错: {e}")

    print()


def main():
    """
    主函数，运行所有批量处理示例
    """
    try:
        # 多个文本单个审核项
        multiple_texts_single_item()

        # 单个文本多个审核项
        single_text_multiple_items()

        # 多个文本多个审核项
        multiple_texts_multiple_items()

        # 批量审核错误处理
        batch_audit_error_handling()

        print("=== 所有批量处理示例执行完成 ===")

    except Exception as e:
        print(f"执行示例时出错: {e}")
        print("请检查环境变量配置是否正确")


if __name__ == "__main__":
    main()
