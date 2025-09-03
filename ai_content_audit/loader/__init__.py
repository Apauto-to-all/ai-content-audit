"""
AI内容审核数据加载器模块。

此模块提供用于加载审核文本和审核项的工具类。
使用 `audit_data` 加载文本数据，
以及 `options_item` 加载审核选项项。
"""

from __future__ import annotations
from ai_content_audit.loader.data_loader import AuditTextLoader as audit_data
from ai_content_audit.loader.checks_loader import AuditOptionsItemLoader as options_item

__all__ = [
    "audit_data",
    "options_item",
]
