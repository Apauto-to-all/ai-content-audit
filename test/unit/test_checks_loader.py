"""测试审核项加载器模块"""

import pytest
from ai_content_audit.loader.checks_loader import AuditOptionsItemLoader
from ai_content_audit.models.audit_options_item_model import AuditOptionsItem


class TestAuditOptionsItemLoader:
    """测试审核项加载器类"""

    def test_create_basic_item(self):
        """测试创建基本审核项"""
        name = "是否包含敏感信息"
        instruction = "检查文本中是否出现敏感信息"
        options = {"有": "检测有敏感信息", "无": "没有检测到敏感信息"}

        result = AuditOptionsItemLoader.create(
            name=name, instruction=instruction, options=options
        )

        assert isinstance(result, AuditOptionsItem)
        assert result.name == name
        assert result.instruction == instruction
        assert result.options == options
        assert result.id is not None

    def test_create_with_multiple_options(self):
        """测试创建带多个选项的审核项"""
        options = {
            "选项1": "说明1",
            "选项2": "说明2",
            "选项3": "说明3",
            "选项4": "说明4",
        }

        result = AuditOptionsItemLoader.create(
            name="多选项测试", instruction="测试多选项功能", options=options
        )

        assert len(result.options) == 4
        assert result.options == options

    def test_from_dict_basic(self):
        """测试从字典加载基本审核项"""
        data = {
            "name": "从字典创建的审核项",
            "instruction": "测试从字典加载功能",
            "options": {"通过": "审核通过", "不通过": "审核不通过"},
        }

        result = AuditOptionsItemLoader.from_dict(data)

        assert isinstance(result, AuditOptionsItem)
        assert result.name == data["name"]
        assert result.instruction == data["instruction"]
        assert result.options == data["options"]

    def test_from_dict_with_additional_fields(self):
        """测试从字典加载时忽略额外字段"""
        data = {
            "name": "测试审核项",
            "instruction": "测试指令",
            "options": {"是": "是", "否": "否"},
            "extra_field": "应该被忽略的字段",
        }

        result = AuditOptionsItemLoader.from_dict(data)

        # 验证基本字段正确
        assert result.name == data["name"]
        assert result.instruction == data["instruction"]
        assert result.options == data["options"]

    def test_from_dict_missing_required_field(self):
        """测试从字典加载时缺少必需字段"""
        # 缺少name字段
        data = {"instruction": "测试指令", "options": {"是": "是"}}

        with pytest.raises(Exception):
            AuditOptionsItemLoader.from_dict(data)

    def test_from_dict_invalid_options_type(self):
        """测试从字典加载时选项类型错误"""
        data = {
            "name": "测试",
            "instruction": "测试",
            "options": "应该是字典而不是字符串",
        }

        with pytest.raises(Exception):
            AuditOptionsItemLoader.from_dict(data)

    def test_from_dict_invalid_data_type(self):
        """测试从非字典类型加载"""
        with pytest.raises(ValueError, match="入参 data 必须是映射类型"):
            AuditOptionsItemLoader.from_dict("invalid_data")

    def test_create_and_from_dict_equivalence(self):
        """测试create和from_dict方法创建的等价性"""
        name = "等价性测试"
        instruction = "测试两种创建方法的等价性"
        options = {"相同": "应该相同", "结果": "应该一致"}

        # 使用create方法
        create_result = AuditOptionsItemLoader.create(
            name=name, instruction=instruction, options=options
        )

        # 使用from_dict方法
        dict_result = AuditOptionsItemLoader.from_dict(
            {"name": name, "instruction": instruction, "options": options}
        )

        # 验证内容等价
        assert create_result.name == dict_result.name
        assert create_result.instruction == dict_result.instruction
        assert create_result.options == dict_result.options

    def test_unique_ids(self):
        """测试每次创建都生成唯一的ID"""
        item1 = AuditOptionsItemLoader.create(
            name="项1", instruction="指令1", options={"是": "是"}
        )
        item2 = AuditOptionsItemLoader.create(
            name="项2", instruction="指令2", options={"否": "否"}
        )

        assert item1.id != item2.id

    def test_empty_options(self):
        """测试空选项的处理"""
        with pytest.raises(Exception):
            AuditOptionsItemLoader.create(
                name="空选项测试", instruction="测试空选项", options={}
            )

    def test_single_option(self):
        """测试单个选项的审核项"""
        result = AuditOptionsItemLoader.create(
            name="单选项测试",
            instruction="测试单选项",
            options={"唯一选项": "只有一个选项"},
        )

        assert len(result.options) == 1
        assert "唯一选项" in result.options
