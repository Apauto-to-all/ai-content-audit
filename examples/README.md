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

### 图像审核示例

- **`image_examples.py`**: 图像审核功能演示
  - 单张图片审核（暴力内容检测）
  - 批量图片审核（多张图片、多审核项）
  - 混合审核（文本 + 图片）

### 高级用法示例

- **`advanced_examples.py`**: 高级功能和错误处理演示
  - 错误处理机制
  - 自定义模型使用
  - 性能对比测试
  - 自定义选项配置
  - 元数据使用
  - 批量审核错误处理

### 综合示例

- **`example.py`**: 综合使用演示（位于项目根目录）
  - 单文本审核
  - 批量审核
  - 文件加载
  - 目录加载
  - 多审核项处理

## 数据文件结构

```text
data/
├── items/              # 审核项配置文件
│   ├── audit_item.json      # 敏感信息检测配置
│   └── ad_audit_item.json   # 广告内容检测配置
├── texts/              # 示例文本文件
│   ├── sample.txt           # 公司介绍文本
│   ├── advertisement.txt    # 广告内容
│   ├── blog.md             # 博客文章
│   └── sample.md           # 系统文档
└── images/             # 示例图片文件（图像未上传，请手动添加示例图片）
    ├── monalisa-200x200.jpg  # 蒙娜丽莎图片 (JPEG)
    ├── monalisa-200x200.png  # 蒙娜丽莎图片 (PNG)
    ├── monalisa-200x200.tiff # 蒙娜丽莎图片 (TIFF)
    └── monalisa-200x200.webp # 蒙娜丽莎图片 (WebP)
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
   DASHSCOPE_MODEL=qwen-plus
   ```

   对于图像审核示例，还需要配置视觉模型：

   ```env
   VISION_MODEL=qwen-vl-plus
   ```

### 运行特定示例

```bash
# 运行基础示例
python example/basic_examples.py

# 运行文件操作示例
python example/file_examples.py

# 运行批量处理示例
python example/batch_examples.py

# 运行图像审核示例
python example/image_examples.py

# 运行高级用法示例
python example/advanced_examples.py

# 运行综合示例
python example/example.py
```

## 注意事项

1. 运行示例需要有效的 API 密钥，可能产生额外费用
2. 示例中的文本和图片内容仅用于演示
3. 可以根据需要修改示例中的参数和配置
4. 图像审核需要确保图片文件存在且格式支持
