"""
AI 内容审核系统
================

这是一个基于大语言模型的 AI 内容审核工具包。

主要功能：
- 加载和处理审核文本数据
- 定义审核规则和选项
- 执行单/批量审核，支持文本和图像

使用示例：
>>> from openai import OpenAI
>>> from ai_content_audit import AuditManager, loader, file_loader
>>>
>>> # 创建 OpenAI 客户端
>>> client = OpenAI()
>>>
>>> # 创建审核管理器
>>> audit_manager = AuditManager(client=client)
>>>
>>> # 文本审核
>>> # 加载审核文本
>>> text_audit_content = loader.audit_data.create(content="待审核文本", file_type="text")
>>> # 加载审核项
>>> text_audit_item = loader.options_item.create(
...     name="文本审核项名称",
...     instruction="审核指令 - 文本",
...     options={"选项1": "说明", "选项2": "说明"},
... )
>>> # 执行文本审核
>>> text_result = audit_manager.audit_one(
...     content=text_audit_content,
...     item=text_audit_item,
...     model="qwen-plus",
... )
>>>
>>> # 图像审核
>>> # 加载图像文件，将其转化为大模型图像输入格式
>>> image_data = file_loader.load_image("path/to/image.jpg")
>>> # 加载图像审核内容
>>> image_audit_content = loader.audit_data.create(content=image_data, file_type="image")
>>> # 加载审核项
>>> image_audit_item = loader.options_item.create(
...     name="图像审核项名称",
...     instruction="审核指令 - 图像",
...     options={"选项1": "说明", "选项2": "说明"},
... )
>>> # 执行图像审核，需要指定支持图像理解的大模型，如 qwen-vl-plus
>>> image_result = audit_manager.audit_one(
...     content=image_audit_content,
...     item=image_audit_item,
...     model="qwen-vl-plus",
... )
"""

from ai_content_audit.audit_manager import AuditManager
from ai_content_audit import loader
from ai_content_audit import file_loader

__all__ = [
    "AuditManager",
    "loader",
    "file_loader",
]
