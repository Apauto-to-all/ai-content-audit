import json
import pytest
import tempfile
from pathlib import Path
from pydantic import ValidationError

from ai_content_audit.loader.data_loader import AuditContentLoader
from ai_content_audit.models import AuditContent


class TestAuditTextLoader:
    """测试 AuditTextLoader 类"""

    def test_create_success(self):
        """测试 create 方法正常创建"""
        content = "测试文本内容"
        source = "test_source"
        metadata = {"key": "value"}

        text = AuditContentLoader.create(content, source=source, metadata=metadata)

        assert isinstance(text, AuditContent)
        assert text.content == content
        assert text.source == source
        assert text.metadata == metadata

    def test_create_minimal(self):
        """测试 create 方法最小参数"""
        content = "测试文本"

        text = AuditContentLoader.create(content)

        assert text.content == content
        assert text.source is None
        assert text.metadata is None

    def test_from_dict_success(self):
        """测试 from_dict 方法正常加载"""
        data = {
            "content": "测试文本",
            "source": "test_source",
            "metadata": {"key": "value"},
        }

        text = AuditContentLoader.from_dict(data)

        assert isinstance(text, AuditContent)
        assert text.content == data["content"]
        assert text.source == data["source"]
        assert text.metadata == data["metadata"]

    def test_from_dict_minimal(self):
        """测试 from_dict 方法最小字段"""
        data = {"content": "测试文本"}

        text = AuditContentLoader.from_dict(data)

        assert text.content == data["content"]
        assert text.source is None
        assert text.metadata is None

    def test_from_dict_invalid_metadata(self):
        """测试 from_dict 方法 metadata 类型错误"""
        data = {"content": "测试文本", "metadata": "invalid"}

        text = AuditContentLoader.from_dict(data)

        # metadata 应被设为 None
        assert text.metadata is None

    def test_from_dict_missing_content(self):
        """测试 from_dict 方法缺少 content"""
        data = {"source": "test"}

        with pytest.raises(ValidationError):
            AuditContentLoader.from_dict(data)

    def test_from_file_success(self):
        """测试 from_file 方法正常加载"""
        content = "测试文件内容\n第二行"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            text = AuditContentLoader.from_file(temp_path)

            assert isinstance(text, AuditContent)
            assert text.content == content.replace("\r\n", "\n").replace("\r", "\n")
            assert text.source == str(temp_path)
        finally:
            temp_path.unlink()

    def test_from_file_not_found(self):
        """测试 from_file 方法文件不存在"""
        non_existent_path = Path("non_existent.txt")

        with pytest.raises(FileNotFoundError):
            AuditContentLoader.from_file(non_existent_path)

    def test_from_file_unsupported_type(self):
        """测试 from_file 方法不支持的文件类型"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("content")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="不支持的文件类型"):
                AuditContentLoader.from_file(temp_path)
        finally:
            temp_path.unlink()

    def test_from_path_file(self):
        """测试 from_path 方法加载单个文件"""
        content = "文件内容"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            texts = AuditContentLoader.from_path(temp_path)

            assert len(texts) == 1
            assert texts[0].content == content
            assert texts[0].source == str(temp_path)
        finally:
            temp_path.unlink()

    def test_from_path_directory(self):
        """测试 from_path 方法加载目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file1 = temp_path / "file1.txt"
            file2 = temp_path / "file2.md"
            file1.write_text("内容1", encoding="utf-8")
            file2.write_text("内容2", encoding="utf-8")

            texts = AuditContentLoader.from_path(temp_path)

            assert len(texts) == 2
            sources = [t.source for t in texts]
            assert str(file1) in sources
            assert str(file2) in sources

    def test_from_path_directory_non_recursive(self):
        """测试 from_path 方法非递归加载目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sub_dir = temp_path / "sub"
            sub_dir.mkdir()
            file1 = temp_path / "file1.txt"
            file2 = sub_dir / "file2.txt"
            file1.write_text("内容1", encoding="utf-8")
            file2.write_text("内容2", encoding="utf-8")

            texts = AuditContentLoader.from_path(temp_path, recursive=False)

            assert len(texts) == 1
            assert texts[0].source == str(file1)

    def test_from_paths_multiple(self):
        """测试 from_paths 方法批量加载"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file1 = temp_path / "file1.txt"
            file2 = temp_path / "file2.md"
            file1.write_text("内容1", encoding="utf-8")
            file2.write_text("内容2", encoding="utf-8")

            texts = AuditContentLoader.from_paths([file1, file2])

            assert len(texts) == 2
