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
pip install openai pydantic filetype python-dotenv
```

或使用 uv：

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

### 图像审核

```python
# 使用视觉模型审核图片
manager = AuditManager(client=client, model="qwen-vl-plus")

# 加载图片
image = loader.audit_data.from_file("path/to/image.jpg")

# 审核
result = manager.audit_one(image, item)
print(f"决策: {result.decision.choice}")
print(f"理由: {result.decision.reason}")
```

## 功能特性

- ✅ **文本审核**：支持纯文本内容审核
- ✅ **图像审核**：支持 JPEG、PNG、WebP 等格式，使用视觉模型
- ✅ **批量审核**：同时审核多个内容和多个审核项
- ✅ **灵活加载**：从文件、目录或内存加载内容
- ✅ **结构化输出**：基于 Pydantic 的审核结果模型

## 示例

查看 `example/` 目录中的完整示例：

- `example.py`：基础文本审核示例
- `image_examples.py`：图像审核示例
- `batch_examples.py`：批量审核示例
- `file_examples.py`：文件加载示例

运行示例：

```bash
python example/example.py
python example/image_examples.py
```

## 许可证

Apache-2.0，见 [LICENSE](LICENSE)。
