import pytest
from pathlib import Path
from ai_content_audit.loader.media_loader import (
    get_file_type,
    MediaLoader,
    TextLoader,
    ImageLoader,
    SupportedTypes,
    FileType,
)
from ai_content_audit.models.audit_content_model import AuditContent


@pytest.fixture
def temp_text_file(tmp_path):
    """创建临时文本文件用于测试"""
    file = tmp_path / "test.txt"
    file.write_text("Hello World")
    return file


@pytest.fixture
def temp_image_file(tmp_path):
    """创建临时图像文件用于测试"""
    file = tmp_path / "test.jpg"
    file.write_bytes(b"fake image data")  # 模拟图像数据
    return file


class TestGetFileType:
    """测试 get_file_type 函数"""

    def test_text(self, mocker):
        """测试 get_file_type 函数识别文本文件"""
        mock_kind = mocker.MagicMock()
        mock_kind.extension = "txt"
        mock_kind.mime = "text/plain"
        mocker.patch("filetype.guess", return_value=mock_kind)
        result = get_file_type("test.txt")
        assert result.extension == "txt"
        assert result.mime_type == "text/plain"

    def test_unknown(self, mocker):
        """测试 get_file_type 函数处理未知文件类型"""
        mocker.patch("filetype.guess", return_value=None)
        mocker.patch("mimetypes.guess_type", return_value=("unknown", None))
        result = get_file_type("test.unknown")
        assert result.extension == "unknown"
        assert result.mime_type == "unknown"

    def test_no_suffix(self, mocker):
        """测试 get_file_type 函数处理无后缀文件"""
        mocker.patch("filetype.guess", return_value=None)
        mocker.patch("mimetypes.guess_type", return_value=(None, None))
        result = get_file_type("test")
        assert result.extension == "unknown"
        assert result.mime_type == "unknown"


class TestMediaLoader:
    """测试 MediaLoader 类"""

    def test_text(self, temp_text_file):
        """测试 MediaLoader 加载文本文件"""
        result = MediaLoader.from_file(temp_text_file)
        assert isinstance(result, AuditContent)
        assert result.content == "Hello World"
        assert result.file_type == "text"
        assert result.source == str(temp_text_file)

    def test_image(self, temp_image_file, mocker):
        """测试 MediaLoader 加载图像文件"""
        mock_kind = mocker.MagicMock()
        mock_kind.extension = "jpg"
        mock_kind.mime = "image/jpeg"
        mocker.patch("filetype.guess", return_value=mock_kind)
        result = MediaLoader.from_file(temp_image_file)
        assert isinstance(result, AuditContent)
        assert result.file_type == "image"
        assert result.source == str(temp_image_file)
        assert "data:image/jpeg;base64," in result.content

    def test_unsupported_type(self, tmp_path, mocker):
        """测试 MediaLoader 处理不支持的文件类型"""
        # 创建临时文件
        file = tmp_path / "test.exe"
        file.write_bytes(b"fake exe data")

        mock_kind = mocker.MagicMock()
        mock_kind.extension = "exe"
        mock_kind.mime = "application/octet-stream"
        mocker.patch("filetype.guess", return_value=mock_kind)

        with pytest.raises(ValueError, match="不支持的文件类型"):
            MediaLoader.from_file(file)

    def test_file_not_found(self):
        """测试 MediaLoader 处理文件不存在的情况"""
        with pytest.raises(FileNotFoundError):
            MediaLoader.from_file("nonexistent.txt")

    def test_unknown_type(self, tmp_path, mocker):
        """测试 MediaLoader 处理未知文件类型"""
        # 创建临时文件
        file = tmp_path / "test.unknown"
        file.write_bytes(b"fake unknown data")

        mocker.patch("filetype.guess", return_value=None)
        mocker.patch("mimetypes.guess_type", return_value=(None, None))

        with pytest.raises(ValueError, match="无法识别的文件"):
            MediaLoader.from_file(file)


class TestTextLoader:
    """测试 TextLoader 类"""

    def test_from_file(self, temp_text_file):
        """测试 TextLoader 直接加载文本文件"""
        result = TextLoader.from_file(temp_text_file)
        assert isinstance(result, AuditContent)
        assert result.content == "Hello World"
        assert result.file_type == "text"
        assert result.source == str(temp_text_file)

    def test_encoding(self, temp_text_file):
        """测试 TextLoader 处理不同编码"""
        # 假设文件是 UTF-8
        result = TextLoader.from_file(temp_text_file, encoding="utf-8")
        assert result.content == "Hello World"


class TestImageLoader:
    """测试 ImageLoader 类"""

    def test_from_file(self, temp_image_file, mocker):
        """测试 ImageLoader 直接加载图像文件"""
        mock_kind = mocker.MagicMock()
        mock_kind.extension = "jpg"
        mock_kind.mime = "image/jpeg"
        mocker.patch("filetype.guess", return_value=mock_kind)
        result = ImageLoader.from_file(temp_image_file, mime_type="image/jpeg")
        assert isinstance(result, AuditContent)
        assert result.file_type == "image"
        assert result.source == str(temp_image_file)
        assert "data:image/jpeg;base64," in result.content

    def test_encoding(self, temp_image_file, mocker):
        """测试 ImageLoader 处理不同编码"""
        mock_kind = mocker.MagicMock()
        mock_kind.extension = "jpg"
        mock_kind.mime = "image/jpeg"
        mocker.patch("filetype.guess", return_value=mock_kind)
        result = ImageLoader.from_file(
            temp_image_file, mime_type="image/jpeg", encoding="utf-8"
        )
        assert "data:image/jpeg;base64," in result.content


class TestSupportedTypes:
    """测试 SupportedTypes 类"""

    def test_types(self):
        """测试 SupportedTypes 类"""
        assert "txt" in SupportedTypes.text
        assert "jpg" in SupportedTypes.image
        assert "exe" not in SupportedTypes.text
        assert "exe" not in SupportedTypes.image


class TestFileType:
    """测试 FileType namedtuple"""

    def test_namedtuple(self):
        """测试 FileType namedtuple"""
        ft = FileType(extension="txt", mime_type="text/plain")
        assert ft.extension == "txt"
        assert ft.mime_type == "text/plain"
