"""
AI内容审核系统 - 图像审核示例

这个示例展示了如何使用 AI 内容审核系统的图像审核功能，包括：
- 图像内容审核
- 图像安全检测
- 图像批量审核
- 图像审核结果分析
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径并加载环境变量
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
load_dotenv()

from openai import OpenAI
from ai_content_audit import AuditManager, loader, file_loader


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


def single_image_audit():
    """
    单张图片审核示例

    演示如何对单张图片进行内容审核
    """
    print("=== 单张图片审核示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 检查图片文件是否存在
    image_path = "examples/data/monalisa-100x100.jpg"
    if not os.path.exists(image_path):
        print(f"图片文件不存在: {image_path}")
        print("请确保已添加示例图片文件")
        return

    try:
        # 加载图像文件
        image_data = file_loader.load_image(image_path)
        print(f"成功加载图片: {image_path}")

        # 创建图像审核内容
        image_content = loader.audit_data.create(
            content=image_data,
            file_type="image",
            metadata={"filename": os.path.basename(image_path)},
        )

        # 创建图像审核项
        violence_item = loader.options_item.create(
            name="暴力内容检测",
            instruction="检查图片中是否包含暴力、血腥、武器等不适宜内容",
            options={
                "安全": "图片内容安全适宜",
                "暴力": "检测到暴力内容",
                "不确定": "无法判断是否包含暴力内容",
            },
        )

        # 执行图像审核
        print("正在执行图像审核...")
        result = audit_manager.audit_one(
            content=image_content,
            item=violence_item,
            model="qwen-vl-plus",  # 使用支持图像的模型
        )

        # 输出结果
        print(f"图片审核结果: {result.decision.choice}")
        print(f"审核说明: {result.decision.reason}")

    except Exception as e:
        print(f"图像审核出错: {e}")
        print("请检查图片文件格式和模型配置")

    print()


def batch_image_audit():
    """
    批量图片审核示例

    演示如何批量审核多张图片
    """
    print("=== 批量图片审核示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 检查图片文件是否存在
    image_files = [
        "examples/data/monalisa-100x100.jpg",
        # 可以添加更多图片文件路径
    ]

    # 过滤存在的图片文件
    existing_images = []
    for image_path in image_files:
        if os.path.exists(image_path):
            existing_images.append(image_path)
        else:
            print(f"图片文件不存在: {image_path}")

    if not existing_images:
        print("没有可用的图片文件")
        print("请确保已添加示例图片文件")
        return

    try:
        # 加载所有图片文件
        image_contents = []
        for image_path in existing_images:
            image_data = file_loader.load_image(image_path)
            image_content = loader.audit_data.create(
                content=image_data,
                file_type="image",
                metadata={"filename": os.path.basename(image_path)},
            )
            image_contents.append(image_content)
            print(f"加载图片: {os.path.basename(image_path)}")

        # 创建图像审核项
        content_item = loader.options_item.create(
            name="图像内容检测",
            instruction="检查图片的内容类型和适宜性",
            options={
                "适宜": "图片内容适宜展示",
                "不适宜": "图片内容不适宜展示",
                "艺术": "检测到艺术作品",
                "不确定": "无法判断图片内容",
            },
        )

        # 执行批量图像审核
        print(f"\n批量审核 {len(image_contents)} 张图片...")
        results = audit_manager.audit_batch(
            contents=image_contents,
            items=[content_item],
            model="qwen-vl-plus",  # 使用支持图像的模型
        )

        # 输出结果
        for i, result in enumerate(results, 1):
            print(f"\n图片 {i} ({existing_images[i-1]}):")
            print(f"  审核结果: {result.decision.choice}")
            print(f"  审核说明: {result.decision.reason}")

    except Exception as e:
        print(f"批量图像审核出错: {e}")
        print("请检查图片文件格式和模型配置")

    print()


def mixed_content_audit():
    """
    混合内容审核示例

    演示如何同时审核文本和图片内容
    """
    print("=== 混合内容审核示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 检查图片文件是否存在
    image_path = "examples/data/monalisa-100x100.jpg"
    if not os.path.exists(image_path):
        print(f"图片文件不存在: {image_path}")
        print("请确保已添加示例图片文件")
        return

    try:
        # 创建文本审核内容
        text_content = loader.audit_data.create(
            content="这是一段描述艺术作品的文本内容", file_type="text"
        )

        # 创建图像审核内容
        image_data = file_loader.load_image(image_path)
        image_content = loader.audit_data.create(
            content=image_data,
            file_type="image",
            metadata={"filename": os.path.basename(image_path)},
        )

        # 创建通用审核项
        general_item = loader.options_item.create(
            name="内容适宜性检测",
            instruction="检查内容是否适宜展示",
            options={
                "适宜": "内容适宜展示",
                "不适宜": "内容不适宜展示",
                "不确定": "无法判断内容适宜性",
            },
        )

        # 分别审核文本和图片
        contents = [
            ("文本", text_content, "qwen-plus"),
            ("图片", image_content, "qwen-vl-plus"),
        ]

        for content_type, content, model in contents:
            print(f"\n审核{content_type}内容:")

            result = audit_manager.audit_one(
                content=content, item=general_item, model=model
            )

            print(f"  {content_type}审核结果: {result.decision.choice}")
            print(f"  审核说明: {result.decision.reason}")

    except Exception as e:
        print(f"混合内容审核出错: {e}")
        print("请检查文件格式和模型配置")

    print()


def image_safety_detection():
    """
    图像安全检测示例

    演示如何进行图像安全检测
    """
    print("=== 图像安全检测示例 ===")

    # 设置环境
    client = setup_environment()

    # 创建审核管理器
    audit_manager = AuditManager(client=client)

    # 检查图片文件是否存在
    image_path = "examples/data/monalisa-100x100.jpg"
    if not os.path.exists(image_path):
        print(f"图片文件不存在: {image_path}")
        print("请确保已添加示例图片文件")
        return

    try:
        # 加载图像文件
        image_data = file_loader.load_image(image_path)
        image_content = loader.audit_data.create(content=image_data, file_type="image")

        # 创建多个安全检测审核项
        safety_items = [
            ("暴力内容检测", "检查图片中是否包含暴力、血腥内容"),
            ("色情内容检测", "检查图片中是否包含色情、裸露内容"),
            ("敏感信息检测", "检查图片中是否包含敏感信息如二维码、联系方式等"),
            ("版权内容检测", "检查图片是否可能涉及版权问题"),
        ]

        for item_name, instruction in safety_items:
            safety_item = loader.options_item.create(
                name=item_name,
                instruction=instruction,
                options={
                    "安全": "未检测到相关问题",
                    "有问题": "检测到相关问题",
                    "不确定": "无法判断",
                },
            )

            print(f"\n{item_name}:")
            result = audit_manager.audit_one(
                content=image_content, item=safety_item, model="qwen-vl-plus"
            )

            print(f"  检测结果: {result.decision.choice}")
            print(f"  检测说明: {result.decision.reason}")

    except Exception as e:
        print(f"图像安全检测出错: {e}")
        print("请检查图片文件格式和模型配置")

    print()


def main():
    """
    主函数，运行所有图像审核示例
    """
    try:
        # 单张图片审核
        single_image_audit()

        # 批量图片审核
        batch_image_audit()

        # 混合内容审核
        mixed_content_audit()

        # 图像安全检测
        image_safety_detection()

        print("=== 所有图像审核示例执行完成 ===")

    except Exception as e:
        print(f"执行示例时出错: {e}")
        print("请检查环境变量配置是否正确")
        print("注意：图像审核需要配置支持图像的模型（如 qwen-vl-plus）")


if __name__ == "__main__":
    main()
