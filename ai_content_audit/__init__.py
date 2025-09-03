"""
AI 内容审核系统
================

这是一个基于大语言模型的 AI 内容审核工具包。

主要功能：
- 加载和处理审核文本数据
- 定义审核规则和选项
- 执行单文本或批量审核
- 支持多种数据源和配置

使用示例：
>>> from ai_content_audit import AuditManager, loader
>>> # 创建审核管理器
>>> audit_manager = AuditManager(client=client, model="qwen-plus")
>>> # 加载审核文本
>>> audit_text = loader.audit_data.create(content="待审核文本", source="来源")
>>> # 加载审核项
>>> audit_item = loader.options_item.create(
...     name="审核项名称",
...     instruction="审核指令",
...     options={"选项1": "说明", "选项2": "说明"}
... )
>>> # 执行审核
>>> result = audit_manager.audit_one(audit_text, audit_item)
"""

from ai_content_audit.audit_manager import AuditManager
from ai_content_audit import loader

__all__ = [
    "AuditManager",
    "loader",
]
