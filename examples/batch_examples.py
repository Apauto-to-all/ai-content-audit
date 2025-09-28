"""
批量处理示例

演示如何批量审核多个文本和多个审核项。
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


def batch_multiple_texts_single_item():
    """批量审核多个文本，单个审核项"""
    print("=== 批量审核多个文本（单个审核项）===")

    audit_manager = AuditManager(client=client, model=model)

    # 创建审核项
    audit_item = loader.options_item.create(
        name="内容质量检查",
        instruction="检查文本内容质量和合规性。",
        options={
            "优质": "内容优质",
            "一般": "内容一般",
            "差": "内容质量差",
        },
    )

    # 创建多个文本
    audit_texts = [
        loader.audit_data.create(
            content="这是一个高质量的文章，内容详实，结构清晰。",
            source="优质文章",
        ),
        loader.audit_data.create(
            content="随便写写",
            source="低质量内容",
        ),
        loader.audit_data.create(
            content="这篇文章内容丰富，逻辑性强，值得一读。",
            source="中等质量",
        ),
    ]

    # 批量审核
    results = audit_manager.audit_batch(audit_texts, [audit_item])

    for i, result in enumerate(results, 1):
        print(f"结果 {i}:")
        print(f"  文本: {result.text_excerpt[:30]}...")
        print(f"  来源: {result.text_excerpt}")
        print(f"  决策: {result.decision.choice}")
        print(f"  理由: {result.decision.reason}")
        print()


def batch_single_text_multiple_items():
    """单个文本，多个审核项"""
    print("=== 单个文本多个审核项 ===")

    audit_manager = AuditManager(client=client, model=model)

    # 创建多个审核项
    audit_items = [
        loader.options_item.create(
            name="敏感信息检查",
            instruction="检查是否包含敏感信息。",
            options={"无": "无敏感信息", "有": "有敏感信息"},
        ),
        loader.options_item.create(
            name="广告内容检查",
            instruction="检查是否包含广告内容。",
            options={"非广告": "非广告", "广告": "广告内容"},
        ),
        loader.options_item.create(
            name="语言质量检查",
            instruction="检查语言质量和规范性。",
            options={"规范": "语言规范", "不规范": "语言不规范"},
        ),
    ]

    # 创建测试文本
    audit_text = loader.audit_data.create(
        content="我们的产品超级棒！限时优惠，联系电话13800138000立即购买！",
        source="测试文本",
    )

    # 批量审核
    results = audit_manager.audit_batch([audit_text], audit_items)

    for i, result in enumerate(results, 1):
        print(f"审核项 {i}: {result.item_name}")
        print(f"  决策: {result.decision.choice}")
        print(f"  理由: {result.decision.reason}")
        print()


def batch_multiple_texts_multiple_items():
    """多个文本，多个审核项"""
    print("=== 多个文本多个审核项 ===")

    audit_manager = AuditManager(client=client, model=model)

    # 创建审核项
    audit_items = [
        loader.options_item.create(
            name="合规性检查",
            instruction="检查内容是否合规。",
            options={"合规": "内容合规", "不合规": "内容不合规"},
        ),
        loader.options_item.create(
            name="质量检查",
            instruction="检查内容质量。",
            options={"优质": "质量优质", "一般": "质量一般"},
        ),
    ]

    # 创建多个文本
    audit_texts = [
        loader.audit_data.create(
            content="这是一个正常的用户评论，表达了满意。",
            source="评论1",
        ),
        loader.audit_data.create(
            content="垃圾广告！立即购买我们的产品！",
            source="广告内容",
        ),
        loader.audit_data.create(
            content="详细的技术文章，包含大量专业知识。",
            source="技术文章",
        ),
    ]

    # 批量审核
    results = audit_manager.audit_batch(audit_texts, audit_items)

    print("批量审核结果汇总：")
    print("=" * 80)

    for i, result in enumerate(results, 1):
        print(f"结果 {i}:")
        print(f"  批次ID: {result.batch_id}")
        print(f"  文本: {result.text_excerpt[:40]}...")
        print(f"  审核项: {result.item_name}")
        print(f"  决策: {result.decision.choice}")
        print(f"  理由: {result.decision.reason}")
        print("-" * 40)

    print("=" * 80)


def batch_with_file_loading():
    """从文件加载数据进行批量审核"""
    print("=== 从文件加载进行批量审核 ===")

    audit_manager = AuditManager(client=client, model=model)

    # 从文件加载审核项
    audit_items = [
        loader.options_item.from_json_file("example/data/items/audit_item.json"),
        loader.options_item.from_json_file("example/data/items/ad_audit_item.json"),
    ]

    # 从目录加载文本
    audit_texts = loader.audit_data.from_path("example/data/texts/")

    print(f"加载了 {len(audit_items)} 个审核项，{len(audit_texts)} 个文本文件")

    # 批量审核
    results = audit_manager.audit_batch(audit_texts, audit_items)

    # 统计结果
    total_results = len(results)
    print(f"\n总共生成 {total_results} 个审核结果")

    # 按审核项分组统计
    item_stats = {}
    for result in results:
        item_name = result.item_name
        choice = result.decision.choice
        if item_name not in item_stats:
            item_stats[item_name] = {}
        if choice not in item_stats[item_name]:
            item_stats[item_name][choice] = 0
        item_stats[item_name][choice] += 1

    print("\n审核统计：")
    for item_name, choices in item_stats.items():
        print(f"  {item_name}:")
        for choice, count in choices.items():
            print(f"    {choice}: {count} 次")


if __name__ == "__main__":
    batch_multiple_texts_single_item()
    batch_single_text_multiple_items()
    batch_multiple_texts_multiple_items()
    batch_with_file_loading()
