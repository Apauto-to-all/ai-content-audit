import json
import pytest
import tempfile
from pathlib import Path
from pydantic import ValidationError

from ai_content_audit.loader.checks_loader import AuditOptionsItemLoader
from ai_content_audit.models import AuditOptionsItem


class TestAuditOptionsItemLoader:
    """测试 AuditOptionsItemLoader 类"""

    def test_create_success(self):
        """测试 create 方法正常创建"""
        name = "测试审核项"
        instruction = "测试指令"
        options = {"有": "检测到", "无": "未检测到"}

        item = AuditOptionsItemLoader.create(name, instruction, options)

        assert isinstance(item, AuditOptionsItem)
        assert item.name == name
        assert item.instruction == instruction
        assert item.options == options

    def test_from_dict_success(self):
        """测试 from_dict 方法正常加载"""
        data = {
            "name": "测试审核项",
            "instruction": "测试指令",
            "options": {"有": "检测到", "无": "未检测到"},
        }

        item = AuditOptionsItemLoader.from_dict(data)

        assert isinstance(item, AuditOptionsItem)
        assert item.name == data["name"]
        assert item.instruction == data["instruction"]
        assert item.options == data["options"]

    def test_from_dict_missing_key(self):
        """测试 from_dict 方法缺少必要字段"""
        data = {"name": "测试", "instruction": "指令"}  # 缺少 options

        with pytest.raises(ValidationError):
            AuditOptionsItemLoader.from_dict(data)

    def test_from_dict_invalid_type(self):
        """测试 from_dict 方法传入非映射类型"""
        data = "invalid"

        with pytest.raises(ValueError, match="入参 data 必须是映射类型"):
            AuditOptionsItemLoader.from_dict(data)

    def test_from_json_file_success(self):
        """测试 from_json_file 方法正常加载"""
        data = {
            "name": "测试审核项",
            "instruction": "测试指令",
            "options": {"有": "检测到", "无": "未检测到"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = Path(f.name)

        try:
            item = AuditOptionsItemLoader.from_json_file(temp_path)

            assert isinstance(item, AuditOptionsItem)
            assert item.name == data["name"]
            assert item.instruction == data["instruction"]
            assert item.options == data["options"]
        finally:
            temp_path.unlink()

    def test_from_json_file_not_found(self):
        """测试 from_json_file 方法文件不存在"""
        non_existent_path = Path("non_existent.json")

        with pytest.raises(FileNotFoundError):
            AuditOptionsItemLoader.from_json_file(non_existent_path)

    def test_from_json_file_invalid_json(self):
        """测试 from_json_file 方法 JSON 格式错误"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="JSON 解析失败"):
                AuditOptionsItemLoader.from_json_file(temp_path)
        finally:
            temp_path.unlink()

    def test_from_json_file_invalid_root_type(self):
        """测试 from_json_file 方法 JSON 根类型不是对象"""
        data = ["array", "instead", "of", "object"]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="不支持的 JSON 根类型"):
                AuditOptionsItemLoader.from_json_file(temp_path)
        finally:
            temp_path.unlink()
