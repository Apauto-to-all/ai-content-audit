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

# 加载 .env
load_dotenv()

DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
VISION_MODEL = "qwen-vl-plus-2025-08-15"  # 视觉模型

# 获取 OpenAI 客户端
client = OpenAI(
    base_url=os.getenv("DASHSCOPE_BASE_URL", ""),
    api_key=os.getenv("DASHSCOPE_API_KEY", ""),
)


def test_image_audit():
    """图片审核示例：审核单张图片"""
    # 创建审核管理器（使用视觉模型）
    audit_manager = AuditManager(client=client, model=VISION_MODEL)

    # 创建针对图片的审核项
    audit_item = loader.options_item.create(
        name="是否包含暴力内容",
        instruction="检查图像中是否包含暴力、血腥或恐怖元素。",
        options={
            "有": "检测到暴力内容",
            "无": "没有检测到暴力内容",
            "不确定": "无法判断是否含有暴力内容",
        },
    )

    # 从文件加载图片（使用 MediaLoader）
    image_path = "example/data/images/monalisa-200x200.jpg"
    audit_image = loader.audit_data.from_file(image_path)

    print(f"加载图片：{audit_image.source}")
    print(f"图片类型：{audit_image.file_type}")
    print(f"内容长度：{len(audit_image.content)} 字符")

    # 执行图片审核
    result = audit_manager.audit_one(audit_image, audit_item)

    print("\n图片审核结果：")
    print("=" * 60)
    print(f"结果ID: {result.id}")
    print(f"图片ID: {result.text_id}")
    print(f"审核项ID: {result.item_id}")
    print(f"审核项: {result.item_name}")
    print(f"图片来源: {audit_image.source}")
    print(f"决策: {result.decision.choice}")
    print(f"理由: {result.decision.reason}")
    print("=" * 60)


def test_batch_image_audit():
    """批量图片审核示例：审核多张图片"""
    # 创建审核管理器
    audit_manager = AuditManager(client=client, model=VISION_MODEL)

    # 创建审核项
    audit_items = [
        loader.options_item.create(
            name="是否包含暴力内容",
            instruction="检查图像中是否包含暴力、血腥或恐怖元素。",
            options={
                "有": "检测到暴力内容",
                "无": "没有检测到暴力内容",
                "不确定": "无法判断是否含有暴力内容",
            },
        ),
        loader.options_item.create(
            name="是否为艺术作品",
            instruction="判断图像是否为艺术作品（如绘画、雕塑等）。",
            options={
                "是": "是艺术作品",
                "否": "不是艺术作品",
                "不确定": "无法判断",
            },
        ),
    ]

    # 加载多张图片
    image_paths = [
        "example/data/images/monalisa-200x200.jpg",
        "example/data/images/monalisa-200x200.png",
        "example/data/images/monalisa-200x200.webp",
    ]

    audit_images = [loader.audit_data.from_file(path) for path in image_paths]

    print(f"加载了 {len(audit_images)} 张图片")

    # 批量审核
    batch_results = audit_manager.audit_batch(audit_images, audit_items)

    print("\n批量图片审核结果：")
    print("=" * 80)
    for i, res in enumerate(batch_results, 1):
        print(f"结果 {i}:")
        print(f"  结果ID: {res.id}")
        print(f"  批次ID: {res.batch_id}")
        print(f"  图片ID: {res.text_id}")
        print(f"  审核项ID: {res.item_id}")
        print(f"  审核项: {res.item_name}")
        print(f"  图片来源: {res.text_excerpt[:50]}...")
        print(f"  决策: {res.decision.choice}")
        print(f"  理由: {res.decision.reason}")
        print("-" * 40)
    print("=" * 80)


def test_mixed_audit():
    """混合审核示例：文本 + 图片"""
    # 创建审核管理器
    audit_manager = AuditManager(client=client, model=VISION_MODEL)

    # 创建审核项
    audit_item = loader.options_item.create(
        name="内容合规性检查",
        instruction="检查内容是否符合平台规范，无违规信息。",
        options={
            "合规": "内容合规",
            "不合规": "内容不合规",
            "不确定": "无法判断",
        },
    )

    # 加载文本和图片
    audit_contents = [
        loader.audit_data.create(
            content="这是一个正常的文本示例。",
            source="文本示例",
        ),
        loader.audit_data.from_file("example/data/images/monalisa-200x200.jpg"),
    ]

    print("混合审核内容：")
    for content in audit_contents:
        print(f"- {content.source} ({content.file_type})")

    # 批量审核
    results = audit_manager.audit_batch(audit_contents, [audit_item])

    print("\n混合审核结果：")
    print("=" * 60)
    for i, res in enumerate(results, 1):
        print(f"结果 {i}:")
        print(f"  审核项: {res.item_name}")
        print(f"  内容类型: {'文本' if '文本' in res.text_excerpt else '图片'}")
        print(f"  决策: {res.decision.choice}")
        print(f"  理由: {res.decision.reason}")
        print("-" * 40)
    print("=" * 60)


if __name__ == "__main__":
    print("图片审核示例")
    print("=" * 50)
    test_image_audit()
    print("\n" + "=" * 50 + "\n")
    test_batch_image_audit()
    print("\n" + "=" * 50 + "\n")
    test_mixed_audit()
