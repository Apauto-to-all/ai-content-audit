import json
import logging
import os
from dotenv import load_dotenv
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai_content_audit import (
    loader,
    AuditManager,
)
from openai import OpenAI

# logging.basicConfig(level=logging.DEBUG)

# 加载 .env
load_dotenv()

DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_MODEL = os.getenv("DASHSCOPE_MODEL", "qwen-plus-2025-07-28")


# 获取 OpenAI 客户端
client = OpenAI(
    base_url=os.getenv("DASHSCOPE_BASE_URL", ""),
    api_key=os.getenv("DASHSCOPE_API_KEY", ""),
)

llm_model = LLM_MODEL


def test_audit():
    """直接在 main.py 中测试审核功能"""
    # 创建审核管理器
    audit_manager = AuditManager(client=client, model=llm_model)

    # 使用 AuditOptionsItemLoader 创建审核项
    audit_item = loader.options_item.create(
        name="是否包含敏感信息",
        instruction="检查文本中是否出现用户定义的敏感信息（如个人隐私、密钥、内网地址等）。",
        options={
            "有": "检测有敏感信息",
            "无": "没有检测到敏感信息",
            "不确定": "无法判断是否含有敏感信息",
        },
    )

    # 使用 AuditTextLoader 创建审核文本
    audit_text = loader.audit_data.create(
        content="本文由Apauto发布，联系电话：13800138000。我们在深圳研发AI内容审核系统。",
        source="main.py 示例",
    )

    # 调用单文本审核
    result = audit_manager.audit_one(audit_text, audit_item)
    print("单文本审核结果：")
    print("=" * 60)
    print(f"结果ID: {result.id}")
    print(f"文本ID: {result.text_id}")
    print(f"审核项ID: {result.item_id}")
    print(f"审核项: {result.item_name}")
    print(f"文本节选: {result.text_excerpt}...")
    print(f"决策: {result.decision.choice}")
    print(f"理由: {result.decision.reason}")
    print("=" * 60)


def test_batch_audit():
    """批量审核示例：多个文本 + 多个审核项"""
    # 创建审核管理器
    audit_manager = AuditManager(client=client, model=llm_model)

    # 使用 AuditOptionsItemLoader 创建多个审核项
    audit_items = [
        loader.options_item.create(
            name="是否包含敏感信息",
            instruction="检查文本中是否出现用户定义的敏感信息（如个人隐私、密钥、内网地址等）。",
            options={
                "有": "检测到敏感信息",
                "无": "没有检测到敏感信息",
                "不确定": "无法判断是否含有敏感信息",
            },
        ),
        loader.options_item.create(
            name="是否包含广告内容",
            instruction="检查文本中是否包含广告推广或营销信息。",
            options={
                "True": "检测到广告内容",
                "False": "没检测到广告内容",
                "不确定": "无法判断是否含有广告内容",
            },
        ),
    ]

    # 使用 AuditTextLoader 创建多个审核文本
    audit_texts = [
        loader.audit_data.create(
            content="本文由Apauto发布，联系电话：13800138000。我们在深圳研发AI内容审核系统。",
            source="示例文本1",
        ),
        loader.audit_data.create(
            content="欢迎使用我们的产品！限时优惠，仅此一次！联系我们获取更多信息。",
            source="示例文本2",
        ),
    ]

    # 调用批量审核
    batch_results = audit_manager.audit_batch(audit_texts, audit_items)

    # 打印批量结果
    for i, res in enumerate(batch_results, 1):
        print(f"结果 {i}:")
        print(f"  结果ID: {res.id}")
        print(f"  批次ID: {res.batch_id}")
        print(f"  文本ID: {res.text_id}")
        print(f"  审核项ID: {res.item_id}")
        print(f"  审核项: {res.item_name}")
        print(f"  文本节选: {res.text_excerpt}...")
        print(f"  决策: {res.decision.choice}")
        print(f"  理由: {res.decision.reason}")
        print("-" * 40)
    print("=" * 80)


def test_load_from_file():
    """从文件加载审核项和文本的示例"""
    # 创建审核管理器
    audit_manager = AuditManager(client=client, model=llm_model)

    # 从 JSON 文件加载审核项
    audit_item = loader.options_item.from_json_file(
        "example/data/items/audit_item.json"
    )

    # 从文件加载审核文本
    audit_text = loader.audit_data.from_file("example/data/texts/sample.txt")

    # 执行审核
    result = audit_manager.audit_one(audit_text, audit_item)
    print("从文件加载审核结果：")
    print("=" * 60)
    print(f"审核项: {result.item_name}")
    print(f"文本来源: {audit_text.source}")
    print(f"决策: {result.decision.choice}")
    print(f"理由: {result.decision.reason}")
    print("=" * 60)


def test_load_from_directory():
    """从目录批量加载文本的示例"""
    # 创建审核管理器
    audit_manager = AuditManager(client=client, model=llm_model)

    # 从 JSON 文件加载审核项
    audit_item = loader.options_item.from_json_file(
        "example/data/items/audit_item.json"
    )

    # 从目录加载所有文本文件
    audit_texts = loader.audit_data.from_path("example/data/texts/")

    print(f"从目录加载了 {len(audit_texts)} 个文本文件")

    # 对每个文本执行审核
    for i, text in enumerate(audit_texts, 1):
        result = audit_manager.audit_one(text, audit_item)
        print(f"文件 {i}: {text.source}")
        print(f"  决策: {result.decision.choice}")
        print(f"  理由: {result.decision.reason}")
        print("-" * 40)


def test_multiple_audit_items():
    """使用多个审核项的示例"""
    # 创建审核管理器
    audit_manager = AuditManager(client=client, model=llm_model)

    # 加载多个审核项
    audit_items = [
        loader.options_item.from_json_file("example/data/items/audit_item.json"),
        loader.options_item.from_json_file("example/data/items/ad_audit_item.json"),
    ]

    # 加载文本
    audit_texts = loader.audit_data.from_paths(
        [
            "example/data/texts/sample.txt",
            "example/data/texts/advertisement.txt",
            "example/data/texts/blog.md",
        ]
    )

    # 批量审核
    results = audit_manager.audit_batch(audit_texts, audit_items)

    print("多审核项批量审核结果：")
    print("=" * 80)
    for i, res in enumerate(results, 1):
        print(f"结果 {i}:")
        print(f"  文本: {res.text_excerpt[:50]}...")
        print(f"  审核项: {res.item_name}")
        print(f"  决策: {res.decision.choice}")
        print(f"  理由: {res.decision.reason}")
        print("-" * 40)
    print("=" * 80)


if __name__ == "__main__":
    test_audit()
    print("\n" + "=" * 50 + "\n")
    test_load_from_file()
    print("\n" + "=" * 50 + "\n")
    test_load_from_directory()
    print("\n" + "=" * 50 + "\n")
    test_multiple_audit_items()
