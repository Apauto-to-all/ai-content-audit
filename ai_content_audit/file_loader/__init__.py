"""
文件加载器模块

这个模块提供专门的文件加载功能

已实现：
- 加载图像文件并转换为大模型图像输入格式
"""

from ai_content_audit.file_loader.image_loader import load_image

# 导出主要函数
__all__ = ["load_image"]
