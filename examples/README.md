# AI内容审核系统示例

这个目录包含了 AI 内容审核系统的各种使用示例，按功能分类组织。

## 项目结构更新说明

项目已重新组织为标准的 Python 包结构，主要模块位于 `ai_content_audit` 目录下：

- **`ai_content_audit/`**: 主包目录
  - **`__init__.py`**: 包初始化文件，导出主要功能
  - **`audit_manager.py`**: 审核管理器核心功能
  - **`loader/`**: 数据加载器模块
    - **`data_loader.py`**: 审核内容数据加载器
    - **`checks_loader.py`**: 审核项加载器
  - **`file_loader/`**: 文件加载器模块
    - **`image_loader.py`**: 图像文件加载功能

## 示例文件说明

### 基础示例

- **`basic_examples.py`**: 基础审核功能演示
  - 基础单文本审核
  - 敏感信息检测
  - 广告内容检测

### 批量处理示例

- **`batch_examples.py`**: 批量审核功能演示
  - 多个文本单个审核项
  - 单个文本多个审核项
  - 多个文本多个审核项
  - 批量审核错误处理

### 图像审核示例

- **`image_examples.py`**: 图像审核功能演示
  - 单张图片审核（暴力内容检测）
  - 批量图片审核（多张图片、多审核项）
  - 混合审核（文本 + 图片）
  - 图像安全检测

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
examples/data/
└── monalisa-100x100.jpg  # 蒙娜丽莎示例图片
```

**注意**: 由于项目结构更新，示例文件现在使用 `create()` 和 `from_dict()` 方法
而不是不存在的文件加载方法。如需文件加载功能，请使用现有的数据模拟方法。

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
   DASHSCOPE_MODEL=qwen-plus
   ```

   对于图像审核示例，还需要配置视觉模型：

   ```env
   VISION_MODEL=qwen-vl-plus
   ```

### 运行特定示例

```bash
# 运行基础示例
python examples/basic_examples.py

# 运行批量处理示例
python examples/batch_examples.py

# 运行图像审核示例
python examples/image_examples.py

# 运行高级用法示例
python examples/advanced_examples.py
```

## 注意事项

1. 运行示例需要有效的 API 密钥，可能产生额外费用
2. 示例中的文本和图片内容仅用于演示
3. 可以根据需要修改示例中的参数和配置
4. 图像审核需要确保图片文件存在且格式支持
