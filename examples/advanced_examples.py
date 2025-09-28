"""
AI内容审核系统 - 高级用法示例

这个示例展示了如何使用 AI 内容审核系统的高级功能，包括：
- 自定义审核选项配置
- 性能对比测试
- 元数据使用
- 复杂场景处理
"""

import os
import sys
import time
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


def error_handling_examples():
    """
    错误处理机制示例

    演示如何处理各种错误情况
    """
    print("=== 错误处理机制示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 测试各种错误情况
    error_cases = [
        # 空内容
        {"content": "", "description": "空文本内容"},
        # 超长内容
        {"content": "x" * 10000, "description": "超长文本内容"},
        # 特殊字符
        {"content": "特殊字符测试：\x00\x01\x02", "description": "包含特殊字符"},
        # 正常内容
        {"content": "这是一段正常的文本内容", "description": "正常文本内容"},
    ]

    # 创建审核项
    sensitive_item = loader.options_item.create(
        name="敏感信息检测",
        instruction="检查文本中是否包含敏感信息",
        options={"包含": "检测到敏感信息", "不包含": "未检测到敏感信息"},
    )

    for case in error_cases:
        print(f"\n测试案例: {case['description']}")

        try:
            # 创建审核内容
            audit_content = loader.audit_data.create(
                content=case["content"], file_type="text"
            )

            # 执行审核
            result = audit_manager.audit_one(
                content=audit_content, item=sensitive_item, model="qwen-plus"
            )

            print(f"  审核成功: {result.decision.choice}")

        except Exception as e:
            print(f"  审核失败: {type(e).__name__}: {e}")

    print()


def custom_model_usage():
    """
    自定义模型使用示例

    演示如何使用不同的模型进行审核
    """
    print("=== 自定义模型使用示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 测试文本
    test_text = "这是一段包含电话号码 138-1234-5678 的测试文本"

    # 创建审核项
    sensitive_item = loader.options_item.create(
        name="敏感信息检测",
        instruction="检查文本中是否包含电话号码等敏感信息",
        options={"包含": "检测到敏感信息", "不包含": "未检测到敏感信息"},
    )

    # 创建审核内容
    audit_content = loader.audit_data.create(content=test_text, file_type="text")

    # 测试不同的模型
    models = ["qwen-plus", "qwen-turbo", "qwen-max"]  # 示例模型名称

    for model in models:
        print(f"\n使用模型: {model}")

        try:
            start_time = time.time()

            result = audit_manager.audit_one(
                content=audit_content, item=sensitive_item, model=model
            )

            end_time = time.time()
            response_time = end_time - start_time

            print(f"  审核结果: {result.decision.choice}")
            print(f"  响应时间: {response_time:.2f}秒")

        except Exception as e:
            print(f"  模型 {model} 审核失败: {e}")

    print()


def performance_comparison():
    """
    性能对比测试示例

    演示如何对比不同配置的性能
    """
    print("=== 性能对比测试示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 测试文本列表
    test_texts = [
        "短文本测试",
        "这是一段中等长度的测试文本，用于性能对比",
        "这是一段较长的测试文本，包含更多的内容和细节，用于测试不同长度文本的处理性能差异",
    ]

    # 创建审核项
    sensitive_item = loader.options_item.create(
        name="敏感信息检测",
        instruction="检查文本中是否包含敏感信息",
        options={"包含": "检测到敏感信息", "不包含": "未检测到敏感信息"},
    )

    # 性能测试
    print("\n单文本审核性能测试:")
    for i, text in enumerate(test_texts, 1):
        audit_content = loader.audit_data.create(content=text, file_type="text")

        start_time = time.time()

        try:
            result = audit_manager.audit_one(
                content=audit_content, item=sensitive_item, model="qwen-plus"
            )

            end_time = time.time()
            response_time = end_time - start_time

            print(
                f"文本 {i} (长度: {len(text)}): {response_time:.2f}秒 - {result.decision.choice}"
            )

        except Exception as e:
            print(f"文本 {i} 审核失败: {e}")

    # 批量审核性能测试
    print("\n批量审核性能测试:")

    # 创建批量审核内容
    batch_contents = []
    for text in test_texts * 2:  # 重复文本以增加批量大小
        audit_content = loader.audit_data.create(content=text, file_type="text")
        batch_contents.append(audit_content)

    start_time = time.time()

    try:
        results = audit_manager.audit_batch(
            contents=batch_contents, items=[sensitive_item], model="qwen-plus"
        )

        end_time = time.time()
        batch_time = end_time - start_time

        print(f"批量审核 {len(batch_contents)} 个文本: {batch_time:.2f}秒")
        print(f"平均每个文本: {batch_time/len(batch_contents):.2f}秒")

    except Exception as e:
        print(f"批量审核失败: {e}")

    print()


def custom_options_configuration():
    """
    自定义选项配置示例

    演示如何配置复杂的审核选项
    """
    print("=== 自定义选项配置示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 测试文本
    test_text = """
    这是一篇技术博客文章，讨论人工智能在医疗领域的应用。
    文章介绍了深度学习算法在医学影像分析中的使用，
    以及自然语言处理在电子病历分析中的应用。
    """

    # 创建复杂的审核项配置
    complex_items = [
        {
            "name": "内容质量评估",
            "instruction": "从专业性、结构清晰度、内容深度等方面评估文本质量",
            "options": {
                "优秀": "内容专业、结构清晰、深度足够",
                "良好": "内容基本合格，有一定专业性",
                "一般": "内容质量一般，需要改进",
                "较差": "内容质量较差，需要大幅改进",
            },
        },
        {
            "name": "技术准确性评估",
            "instruction": "评估文本中技术内容的准确性和时效性",
            "options": {
                "准确": "技术内容准确且时效性好",
                "基本准确": "技术内容基本准确，有小问题",
                "不准确": "技术内容存在明显错误",
                "无法判断": "无法评估技术准确性",
            },
        },
        {
            "name": "适用性评估",
            "instruction": "评估文本对不同读者群体的适用性",
            "options": {
                "专业读者": "适合专业技术人员阅读",
                "普通读者": "适合普通读者阅读",
                "初学者": "适合初学者阅读",
                "不适用": "内容不清晰，不适合任何读者",
            },
        },
    ]

    # 创建审核内容
    audit_content = loader.audit_data.create(content=test_text, file_type="text")

    for item_config in complex_items:
        # 从配置创建审核项
        audit_item = loader.options_item.create(
            name=item_config["name"],
            instruction=item_config["instruction"],
            options=item_config["options"],
        )

        print(f"\n审核项: {item_config['name']}")

        try:
            result = audit_manager.audit_one(
                content=audit_content, item=audit_item, model="qwen-plus"
            )

            print(f"  评估结果: {result.decision.choice}")
            print(f"  评估说明: {result.decision.reason}")

        except Exception as e:
            print(f"  审核失败: {e}")

    print()


def metadata_usage_examples():
    """
    元数据使用示例

    演示如何使用元数据功能
    """
    print("=== 元数据使用示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 创建带元数据的审核内容
    metadata_content = loader.audit_data.create(
        content="这是一段测试文本，包含元数据信息",
        file_type="text",
        metadata={
            "source": "测试数据",
            "author": "AI助手",
            "timestamp": "2024-12-19",
            "category": "技术文档",
            "priority": "高",
        },
    )

    # 创建审核项
    sensitive_item = loader.options_item.create(
        name="敏感信息检测",
        instruction="检查文本中是否包含敏感信息",
        options={"包含": "检测到敏感信息", "不包含": "未检测到敏感信息"},
    )

    # 执行审核
    result = audit_manager.audit_one(
        content=metadata_content, item=sensitive_item, model="qwen-plus"
    )

    print("审核内容元数据:")
    for key, value in metadata_content.metadata.items():
        print(f"  {key}: {value}")

    print(f"\n审核结果: {result.decision.choice}")
    print(f"审核说明: {result.decision.reason}")
    print()


def main():
    """
    主函数，运行所有高级用法示例
    """
    try:
        # 错误处理机制
        error_handling_examples()

        # 自定义模型使用
        custom_model_usage()

        # 性能对比测试
        performance_comparison()

        # 自定义选项配置
        custom_options_configuration()

        # 元数据使用
        metadata_usage_examples()

        print("=== 所有高级用法示例执行完成 ===")

    except Exception as e:
        print(f"执行示例时出错: {e}")
        print("请检查环境变量配置是否正确")


if __name__ == "__main__":
    main()
