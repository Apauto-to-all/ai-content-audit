# AI内容审核系统示例

这个目录包含了 AI 内容审核系统的各种使用示例，按功能分类组织。

## 示例文件说明

### 基础示例

- **`basic_examples.py`**: 基础审核功能演示
  - 基础单文本审核
  - 敏感信息检测
  - 广告内容检测

### 文件操作示例

- **`file_examples.py`**: 文件加载和处理演示
  - 从 JSON 文件加载审核项
  - 从文件加载文本
  - 从目录批量加载文本
  - 加载多个指定文件

### 批量处理示例

- **`batch_examples.py`**: 批量审核功能演示
  - 多个文本单个审核项
  - 单个文本多个审核项
  - 多个文本多个审核项
  - 从文件加载进行批量审核

### 高级用法示例

- **`advanced_examples.py`**: 高级功能和错误处理演示
  - 错误处理机制
  - 自定义模型使用
  - 性能对比测试
  - 自定义选项配置
  - 元数据使用
  - 批量审核错误处理

## 数据文件结构

```text
data/
├── items/              # 审核项配置文件
│   ├── audit_item.json      # 敏感信息检测配置
│   └── ad_audit_item.json   # 广告内容检测配置
└── texts/              # 示例文本文件
    ├── sample.txt           # 公司介绍文本
    ├── advertisement.txt    # 广告内容
    ├── blog.md             # 博客文章
    └── sample.md           # 系统文档
```

## 运行示例

### 环境准备

1. 确保已安装项目依赖：

   ```bash
   uv sync
   ```

2. 配置环境变量（创建 `.env` 文件）：

   ```env
   DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   DASHSCOPE_API_KEY=your_api_key_here
   DASHSCOPE_MODEL=qwen-plus-2025-07-28
   ```

### 运行特定示例

```bash
# 运行基础示例
python example/basic_examples.py

# 运行文件操作示例
python example/file_examples.py

# 运行批量处理示例
python example/batch_examples.py

# 运行高级用法示例
python example/advanced_examples.py
```

### 运行所有示例

```bash
# 运行所有示例（按顺序）
python example/basic_examples.py && python example/file_examples.py && python example/batch_examples.py && python example/advanced_examples.py
```

## 示例特点

- **渐进式学习**：从基础到高级，循序渐进
- **实际场景**：使用真实的审核场景和数据
- **错误处理**：包含异常情况的处理演示
- **性能测试**：对比不同处理方式的性能
- **文件操作**：展示如何从文件加载配置和数据
- **批量处理**：演示高效的批量审核功能

## 注意事项

1. 运行示例需要有效的 API 密钥
2. 部分示例可能产生 API 调用费用
3. 示例中的文本内容仅用于演示
4. 可以根据需要修改示例中的参数和配置

## 扩展示例

如果需要更多类型的示例，可以：

1. 添加新的审核项配置文件
2. 创建更多样例文本文件
3. 实现新的审核场景
4. 添加性能监控和统计功能
