# ai-content-audit

基于大语言模型（LLM）的内容审核工具包：支持文本和图像审核，定义审核项、加载内容、调用模型获得结构化判定结果。

## 安装

- 使用 Python 3.12+

- 安装：

项目已上传至 PyPI，可以直接使用 pip 安装：

```bash
pip install ai-content-audit
```

- 开发安装（可选）：

克隆本仓库：

```bash
git clone https://github.com/Apauto-to-all/ai-content-audit.git
cd ai-content-audit
```

安装依赖包：

```bash
uv sync
```

## 快速上手

### 文本审核

```python
from openai import OpenAI
from ai_content_audit import AuditManager, loader
client = OpenAI(base_url="https://", api_key="your_key")
manager = AuditManager(client=client, model="qwen-plus")
# 定义审核项
item = loader.options_item.create(
    name="是否包含敏感信息",
    instruction="检查文本中是否出现用户定义的敏感信息。",
    options={"有": "检测到", "无": "未检测到", "不确定": "无法判断"},
)
# 加载审核内容
text = loader.audit_data.create(content="本文由xxx发布，联系电话：13800138000。")
# 审核
result = manager.audit_one(text, item)
print("审核结果：")
print(f"结果ID：{result.id}")
print(f"内容项ID：{result.content_id}")
print(f"审核项ID: {result.item_id}")
print(f"审核项: {result.item_name}")
print(f"文本节选: {result.content_excerpt}...")
print(f"决策: {result.decision.choice}")
print(f"理由: {result.decision.reason}")
```

### 图像审核

```python
from openai import OpenAI
from ai_content_audit import AuditManager, loader, file_loader
client = OpenAI(base_url="https://", api_key="your_key")
manager = AuditManager(client=client, model="qwen-vl-plus")
# 图像审核
# 加载图像文件，将其转化为大模型图像输入格式，这里采用 base64 编码
image_data = file_loader.load_image("path/to/image.jpg")
# 加载图像审核内容
image_audit_content = loader.audit_data.create(content=image_data, file_type="image")
# 加载审核项
image_audit_item = loader.options_item.create(
    name="图像审核项名称",
    instruction="审核指令 - 图像",
    options={"选项1": "说明", "选项2": "说明"},
)
# 执行图像审核，需要指定支持图像理解的大模型，如 qwen-vl-plus
result = manager.audit_one(
    content=image_audit_content,
    item=image_audit_item,
    model="qwen-vl-plus",  # 如果 manager 初始化时提供了默认视觉模型，这里可以省略
)
print("审核结果：")
print(f"结果ID：{result.id}")
print(f"内容项ID：{result.content_id}")
print(f"审核项ID: {result.item_id}")
print(f"审核项: {result.item_name}")
print(f"图片base64节选: {result.content_excerpt}...")
print(f"决策: {result.decision.choice}")
print(f"理由: {result.decision.reason}")
```

### 批量审核

```python
from openai import OpenAI
from ai_content_audit import AuditManager, loader
client = OpenAI(base_url="https://", api_key="your_api_key")
manager = AuditManager(client=client, model="qwen-plus")
# 加载审核内容列表
contents = [
    loader.audit_data.create(content="文本1"),
    loader.audit_data.create(content="文本2")
]
# 加载审核项列表
items = [
    loader.options_item.create(name="审核项1", instruction="指令1", options={"通过": "说明", "不通过": "说明"}),
    loader.options_item.create(name="审核项2", instruction="指令2", options={"通过": "说明", "不通过": "说明"})
]
# 使用默认并发数5
results = manager.audit_batch(contents, items)
# 或指定并发数
results = manager.audit_batch(contents, items, max_concurrency=3)
# 打印批量结果
for i, res in enumerate(results, 1):
    print(f"结果 {i}:")
    print(f"  批量ID: {res.batch_id}")
    print(f"  文本项ID: {res.content_id}") # 用于区分
    print(f"  审核项ID: {res.item_id}") # 用于区分
    print(f"  审核项: {res.item_name}")
    print(f"  内容节选: {res.content_excerpt}...")
    print(f"  决策: {res.decision.choice}")
    print(f"  理由: {res.decision.reason}")
    print("-" * 40)
print("=" * 80)
```

## 功能特性

- ✅ **文本审核**：支持纯文本内容审核
- ✅ **图像审核**：支持 JPEG、PNG、WebP 等格式，使用视觉模型
- ✅ **批量审核**：并发审核多个内容和多个审核项
- ✅ **结构化输出**：基于 structured-output-prompt 库生成的格式化输出指令，适用于不支持JSON Schema的大模型，比如 qwen 模型

## 示例

查看 `examples/` 目录中的[示例说明](examples/README.md)

## 许可证

Apache-2.0，见 [LICENSE](LICENSE)。
