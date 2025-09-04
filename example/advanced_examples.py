"""
高级用法示例

演示 AuditManager 的高级功能，如错误处理、自定义配置等。
"""

import os
import sys
import time
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


def error_handling_example():
    """错误处理示例"""
    print("=== 错误处理示例 ===")

    # 创建一个无效的客户端来模拟错误
    invalid_client = OpenAI(
        base_url="https://invalid-url.com",
        api_key="invalid-key",
    )

    audit_manager = AuditManager(client=invalid_client, model=model)

    audit_item = loader.options_item.create(
        name="测试审核项",
        instruction="测试错误处理。",
        options={"通过": "审核通过", "失败": "审核失败"},
    )

    audit_text = loader.audit_data.create(
        content="测试文本",
        source="测试",
    )

    try:
        result = audit_manager.audit_one(audit_text, audit_item)
        print(f"审核成功: {result.decision.choice}")
    except Exception as e:
        print(f"审核失败: {type(e).__name__}: {e}")

    print()


def custom_model_example():
    """使用不同模型的示例"""
    print("=== 自定义模型示例 ===")

    audit_manager = AuditManager(client=client, model="qwen-turbo")

    audit_item = loader.options_item.create(
        name="模型测试",
        instruction="测试不同模型的效果。",
        options={"有效": "模型响应有效", "无效": "模型响应无效"},
    )

    audit_text = loader.audit_data.create(
        content="这是一个测试文本，用于验证模型响应。",
        source="模型测试",
    )

    result = audit_manager.audit_one(audit_text, audit_item)

    print(f"使用模型: qwen-turbo")
    print(f"决策: {result.decision.choice}")
    print(f"理由: {result.decision.reason}")
    print()


def performance_comparison():
    """性能对比示例"""
    print("=== 性能对比示例 ===")

    audit_manager = AuditManager(client=client, model=model)

    audit_item = loader.options_item.create(
        name="性能测试",
        instruction="测试审核性能。",
        options={"完成": "审核完成"},
    )

    # 创建多个测试文本
    audit_texts = [
        loader.audit_data.create(
            content=f"这是测试文本 {i}，用于性能测试。" * 10,  # 较长文本
            source=f"测试文本{i}",
        )
        for i in range(5)
    ]

    # 单次审核
    print("单次审核性能:")
    start_time = time.time()
    for i, text in enumerate(audit_texts):
        result = audit_manager.audit_one(text, audit_item)
        print(
            f"  文本 {i+1}: {result.decision.choice} ({time.time() - start_time:.2f}s)"
        )
        start_time = time.time()

    # 批量审核
    print("\n批量审核性能:")
    start_time = time.time()
    results = audit_manager.audit_batch(audit_texts, [audit_item])
    batch_time = time.time() - start_time

    print(f"批量审核 5 个文本完成时间: {batch_time:.2f}s")
    print(f"平均每个文本: {batch_time/5:.2f}s")
    print()


def custom_options_example():
    """自定义选项示例"""
    print("=== 自定义选项示例 ===")

    audit_manager = AuditManager(client=client, model=model)

    # 复杂的审核项
    audit_item = loader.options_item.create(
        name="详细内容分析",
        instruction="对内容进行详细的多维度分析。",
        options={
            "优秀": "内容优秀，值得推荐",
            "良好": "内容良好，可以接受",
            "一般": "内容一般，需要改进",
            "差": "内容质量差，不建议发布",
            "违规": "内容违规，必须删除",
        },
    )

    audit_texts = [
        loader.audit_data.create(
            content="这是一篇写得非常好的技术文章，内容详实，结构清晰，值得学习。",
            source="优质内容",
        ),
        loader.audit_data.create(
            content="垃圾广告！立即购买！",
            source="违规内容",
        ),
    ]

    for text in audit_texts:
        result = audit_manager.audit_one(text, audit_item)
        print(f"文本: {text.source}")
        print(f"  决策: {result.decision.choice}")
        print(f"  理由: {result.decision.reason}")
        print()


def metadata_usage_example():
    """元数据使用示例"""
    print("=== 元数据使用示例 ===")

    audit_manager = AuditManager(client=client, model=model)

    audit_item = loader.options_item.create(
        name="元数据测试",
        instruction="测试元数据功能。",
        options={"成功": "元数据处理成功"},
    )

    # 使用元数据
    audit_text = loader.audit_data.create(
        content="测试文本",
        source="测试文件",
        metadata={
            "author": "测试用户",
            "category": "测试",
            "priority": "high",
            "tags": ["test", "demo"],
        },
    )

    result = audit_manager.audit_one(audit_text, audit_item)

    print(f"文本元数据: {audit_text.metadata}")
    print(f"审核结果ID: {result.id}")
    print(f"文本ID: {result.text_id}")
    print(f"审核项ID: {result.item_id}")
    print()


def batch_error_handling():
    """批量审核错误处理示例"""
    print("=== 批量审核错误处理 ===")

    # 创建正常客户端
    audit_manager = AuditManager(client=client, model=model)

    audit_item = loader.options_item.create(
        name="错误处理测试",
        instruction="测试批量审核的错误处理。",
        options={"正常": "处理正常", "错误": "处理错误"},
    )

    # 包含正常和异常的文本
    audit_texts = [
        loader.audit_data.create(content="正常文本1", source="正常1"),
        loader.audit_data.create(content="正常文本2", source="正常2"),
        loader.audit_data.create(content="", source="空文本"),  # 可能导致问题
    ]

    results = audit_manager.audit_batch(audit_texts, [audit_item])

    print("批量审核结果（包含错误处理）:")
    for i, result in enumerate(results, 1):
        print(f"结果 {i}: {result.text_excerpt}")
        print(f"  决策: {result.decision.choice}")
        print(f"  理由: {result.decision.reason}")
        print()


if __name__ == "__main__":
    error_handling_example()
    custom_model_example()
    performance_comparison()
    custom_options_example()
    metadata_usage_example()
    batch_error_handling()
