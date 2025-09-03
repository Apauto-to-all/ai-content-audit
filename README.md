# ai-content-audit

基于大语言模型（LLM）的内容审核工具包：定义审核项、加载文本、调用模型获得结构化判定结果。

## 安装

- 使用 Python 3.12+
- 克隆本仓库：

```bash
git clone https://github.com/Apauto-to-all/ai-content-audit.git
cd ai-content-audit
```

- 安装依赖包：

```bash
pip install openai pydantic
```

## 快速上手

核心调用如下：

```python
from openai import OpenAI
from ai_content_audit import AuditManager, loader

client = OpenAI(base_url="https:/", api_key="your_key")
manager = AuditManager(client=client, model="qwen-plus")

# 定义审核项
item = loader.options_item.create(
    name="是否包含敏感信息",
    instruction="检查文本中是否出现用户定义的敏感信息。",
    options={"有":"检测到", "无":"未检测到", "不确定":"无法判断"},
)

# 准备文本
text = loader.audit_data.create(content="本文由xxx发布，联系电话：13800138000。")

# 审核
result = manager.audit_one(text, item)
print(f"审核项: {result.item_name}")
print(f"文本节选: {result.text_excerpt}...")
print(f"决策: {result.decision.choice}")
print(f"理由: {result.decision.reason}")

```

## 许可证

Apache-2.0，见 [LICENSE](LICENSE)。
