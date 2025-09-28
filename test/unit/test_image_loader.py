"""测试图像加载器模块"""

import pytest
import base64
from ai_content_audit.file_loader.image_loader import load_image


class TestImageLoader:
    """测试图像加载器函数"""

    def test_load_image_success_png(self, tmp_path):
        """测试成功加载PNG图像"""
        # 创建临时PNG图像文件
        test_image_path = tmp_path / "test.png"
        test_image_data = b"fake_png_image_data"
        test_image_path.write_bytes(test_image_data)

        # 调用load_image函数
        result = load_image(str(test_image_path))

        # 验证结果格式
        assert result.startswith("data:image/png;base64,")

        # 验证base64编码内容
        base64_part = result.replace("data:image/png;base64,", "")
        decoded_data = base64.b64decode(base64_part)
        assert decoded_data == test_image_data

    def test_load_image_success_jpg(self, tmp_path):
        """测试成功加载JPG图像"""
        # 创建临时JPG图像文件
        test_image_path = tmp_path / "test.jpg"
        test_image_data = b"fake_jpg_image_data"
        test_image_path.write_bytes(test_image_data)

        # 调用load_image函数
        result = load_image(str(test_image_path))

        # 验证结果格式
        assert result.startswith("data:image/jpeg;base64,")

        # 验证base64编码内容
        base64_part = result.replace("data:image/jpeg;base64,", "")
        decoded_data = base64.b64decode(base64_part)
        assert decoded_data == test_image_data

    def test_load_image_unsupported_format(self, tmp_path):
        """测试加载不支持格式的文件"""
        test_file_path = tmp_path / "test.txt"
        test_file_path.write_text("not_an_image")

        with pytest.raises(ValueError, match="不支持的图像格式"):
            load_image(str(test_file_path))

    def test_load_image_not_found(self):
        """测试加载不存在的文件"""
        with pytest.raises(FileNotFoundError):
            load_image("nonexistent_file.png")

    def test_load_image_not_a_file(self, tmp_path):
        """测试加载非文件路径"""
        directory_path = tmp_path / "directory"
        directory_path.mkdir()

        with pytest.raises(ValueError, match="路径不是文件"):
            load_image(str(directory_path))

    def test_load_image_supported_formats(self, tmp_path):
        """测试所有支持的图像格式"""
        supported_formats = [
            ".jpg",
            ".jpeg",
            ".jpe",
            ".png",
            ".bmp",
            ".tif",
            ".tiff",
            ".webp",
            ".heic",
        ]

        for ext in supported_formats:
            test_file_path = tmp_path / f"test{ext}"
            test_file_path.write_bytes(b"fake_image_data")

            try:
                result = load_image(str(test_file_path))
                # 验证返回格式正确
                assert result.startswith("data:image/")
                assert ";base64," in result
            except Exception as e:
                pytest.fail(f"格式 {ext} 应该被支持，但出现错误: {e}")

    def test_load_image_base64_encoding(self, tmp_path):
        """测试base64编码的正确性"""
        # 创建测试图像数据
        test_image_data = b"test_image_content_12345"
        test_image_path = tmp_path / "test.png"
        test_image_path.write_bytes(test_image_data)

        result = load_image(str(test_image_path))

        # 提取base64部分并解码验证
        base64_part = result.split(";base64,")[1]
        decoded_data = base64.b64decode(base64_part)

        assert decoded_data == test_image_data

    def test_load_image_mime_type_correct(self, tmp_path):
        """测试MIME类型正确性"""
        test_cases = [
            (".jpg", "image/jpeg"),
            (".jpeg", "image/jpeg"),
            (".png", "image/png"),
            (".bmp", "image/bmp"),
            (".tif", "image/tiff"),
            (".tiff", "image/tiff"),
            (".webp", "image/webp"),
            (".heic", "image/heic"),
        ]

        for ext, expected_mime in test_cases:
            test_file_path = tmp_path / f"test{ext}"
            test_file_path.write_bytes(b"fake_data")

            result = load_image(str(test_file_path))

            # 验证MIME类型正确
            assert result.startswith(f"data:{expected_mime};base64,")

    def test_load_image_performance_large_file(self, tmp_path):
        """测试大文件加载性能"""
        # 创建较大的测试文件（1MB）
        large_image_data = b"x" * 1024 * 1024  # 1MB数据
        test_image_path = tmp_path / "large.png"
        test_image_path.write_bytes(large_image_data)

        # 测试加载性能
        result = load_image(str(test_image_path))

        # 验证结果格式正确
        assert result.startswith("data:image/png;base64,")

        # 验证base64编码内容长度
        base64_part = result.replace("data:image/png;base64,", "")
        assert len(base64_part) > 0
