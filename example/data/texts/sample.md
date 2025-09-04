# AI内容审核系统示例

## 简介

本文档演示如何使用AI内容审核系统进行文本审核。

## 功能特性

- **敏感信息检测**：自动识别个人隐私、联系方式等敏感内容
- **广告内容识别**：检测营销推广信息
- **批量处理**：支持多个文本同时审核
- **自定义规则**：可配置审核项和选项

## 使用示例

```python
from ai_content_audit import AuditManager, loader

# 创建审核管理器
manager = AuditManager(client, model="qwen-plus")

# 加载审核项
item = loader.options_item.from_json_file("audit_item.json")

# 加载文本
text = loader.audit_data.from_file("sample.txt")

# 执行审核
result = manager.audit_one(text, item)
```

## 注意事项

- 确保API密钥正确配置
- 文件编码建议使用UTF-8
- 审核结果仅供参考
