"""
文件加载示例

演示如何从文件和目录加载审核项和文本数据。
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


def load_from_json_file():
    """从 JSON 文件加载审核项示例"""
    print("=== 从 JSON 文件加载审核项 ===")

    audit_manager = AuditManager(client=client, model=model)

    # 从 JSON 文件加载审核项
    audit_item = loader.options_item.from_json_file(
        "example/data/items/audit_item.json"
    )

    # 创建测试文本
    audit_text = loader.audit_data.create(
        content="公司内部系统，IP地址：192.168.1.100，数据库密码：admin123",
        source="系统日志",
    )

    result = audit_manager.audit_one(audit_text, audit_item)

    print(f"审核项来源: example/data/items/audit_item.json")
    print(f"审核项: {result.item_name}")
    print(f"文本: {result.text_excerpt}")
    print(f"决策: {result.decision.choice}")
    print(f"理由: {result.decision.reason}")
    print()


def load_text_from_file():
    """从文件加载文本示例"""
    print("=== 从文件加载文本 ===")

    audit_manager = AuditManager(client=client, model=model)

    # 加载审核项
    audit_item = loader.options_item.create(
        name="内容审核",
        instruction="检查文本内容是否合适。",
        options={"合适": "内容合适", "不合适": "内容不合适"},
    )

    # 从文件加载文本
    audit_text = loader.audit_data.from_file("example/data/texts/sample.txt")

    result = audit_manager.audit_one(audit_text, audit_item)

    print(f"文本来源: {audit_text.source}")
    print(f"文本内容: {audit_text.content[:100]}...")
    print(f"决策: {result.decision.choice}")
    print(f"理由: {result.decision.reason}")
    print()


def load_from_directory():
    """从目录批量加载文本示例"""
    print("=== 从目录批量加载文本 ===")

    audit_manager = AuditManager(client=client, model=model)

    # 加载审核项
    audit_item = loader.options_item.create(
        name="批量内容审核",
        instruction="批量检查文本内容。",
        options={"通过": "审核通过", "不通过": "审核不通过"},
    )

    # 从目录加载所有文本文件
    audit_texts = loader.audit_data.from_path("example/data/texts/")

    print(f"从目录加载了 {len(audit_texts)} 个文本文件")

    for i, text in enumerate(audit_texts, 1):
        result = audit_manager.audit_one(text, audit_item)
        print(f"文件 {i}: {os.path.basename(text.source)}")
        print(f"  内容: {text.content[:50]}...")
        print(f"  决策: {result.decision.choice}")
        print(f"  理由: {result.decision.reason}")
        print()


def load_multiple_files():
    """加载多个文件示例"""
    print("=== 加载多个指定文件 ===")

    audit_manager = AuditManager(client=client, model=model)

    # 加载审核项
    audit_item = loader.options_item.create(
        name="多文件审核",
        instruction="审核多个文件的内容。",
        options={"正常": "内容正常", "异常": "内容异常"},
    )

    # 加载多个指定文件
    file_paths = [
        "example/data/texts/sample.txt",
        "example/data/texts/blog.md",
    ]

    audit_texts = loader.audit_data.from_paths(file_paths)

    for i, text in enumerate(audit_texts, 1):
        result = audit_manager.audit_one(text, audit_item)
        print(f"文件 {i}: {os.path.basename(text.source)}")
        print(f"  决策: {result.decision.choice}")
        print(f"  理由: {result.decision.reason}")
        print()


if __name__ == "__main__":
    load_from_json_file()
    load_text_from_file()
    load_from_directory()
    load_multiple_files()
