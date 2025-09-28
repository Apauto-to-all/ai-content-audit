"""测试数据加载器模块"""

import pytest
from ai_content_audit.loader.data_loader import AuditContentLoader
from ai_content_audit.models.audit_content_model import AuditContent


class TestAuditContentLoader:
    """测试审核内容加载器类"""

    def test_create_basic_content(self):
        """测试创建基本审核内容"""
        content_text = "这是一个测试文本"

        result = AuditContentLoader.create(content=content_text)

        assert isinstance(result, AuditContent)
        assert result.content == content_text
        assert result.file_type == "text"
        assert result.metadata is None
        assert result.id is not None

    def test_create_with_file_type(self):
        """测试创建带文件类型的审核内容"""
        content_text = "base64编码的图片数据"

        result = AuditContentLoader.create(content=content_text, file_type="image")

        assert result.content == content_text
        assert result.file_type == "image"

    def test_create_with_metadata(self):
        """测试创建带元数据的审核内容"""
        content_text = "测试文本"
        metadata = {"source": "test", "category": "demo"}

        result = AuditContentLoader.create(content=content_text, metadata=metadata)

        assert result.metadata == metadata

    def test_from_dict_basic(self):
        """测试从字典加载基本审核内容"""
        data = {"content": "从字典创建的测试文本", "file_type": "text"}

        result = AuditContentLoader.from_dict(data)

        assert isinstance(result, AuditContent)
        assert result.content == data["content"]
        assert result.file_type == data["file_type"]

    def test_from_dict_with_metadata(self):
        """测试从字典加载带元数据的审核内容"""
        data = {
            "content": "测试文本",
            "file_type": "text",
            "metadata": {"key": "value"},
        }

        result = AuditContentLoader.from_dict(data)

        assert result.metadata == data["metadata"]

    def test_from_dict_default_file_type(self):
        """测试从字典加载时默认文件类型"""
        data = {"content": "测试文本"}

        result = AuditContentLoader.from_dict(data)

        assert result.file_type == "text"

    def test_from_dict_invalid_metadata(self):
        """测试从字典加载时无效的元数据处理"""
        data = {"content": "测试文本", "metadata": "invalid_metadata"}  # 应该是字典

        result = AuditContentLoader.from_dict(data)

        # 应该忽略无效的metadata
        assert result.metadata is None

    def test_from_dict_missing_content(self):
        """测试从字典加载时缺少必需字段"""
        data = {
            "file_type": "text"
            # 缺少content字段
        }

        with pytest.raises(Exception):
            AuditContentLoader.from_dict(data)

    def test_from_dict_invalid_data_type(self):
        """测试从非字典类型加载"""
        with pytest.raises(ValueError, match="无效的字段"):
            AuditContentLoader.from_dict("invalid_data")

    def test_create_and_from_dict_equivalence(self):
        """测试create和from_dict方法创建的等价性"""
        content_text = "测试文本"
        file_type = "text"
        metadata = {"test": "value"}

        # 使用create方法
        create_result = AuditContentLoader.create(
            content=content_text, file_type=file_type, metadata=metadata
        )

        # 使用from_dict方法
        dict_result = AuditContentLoader.from_dict(
            {"content": content_text, "file_type": file_type, "metadata": metadata}
        )

        # 验证内容等价
        assert create_result.content == dict_result.content
        assert create_result.file_type == dict_result.file_type
        assert create_result.metadata == dict_result.metadata

    def test_unique_ids(self):
        """测试每次创建都生成唯一的ID"""
        content1 = AuditContentLoader.create(content="文本1")
        content2 = AuditContentLoader.create(content="文本2")

        assert content1.id != content2.id
