"""测试数据模型模块"""

import pytest
from uuid import UUID
from ai_content_audit.models import (
    AuditContent,
    AuditOptionsItem,
    AuditDecision,
    AuditResult,
)


class TestAuditContentModel:
    """测试审核内容模型"""

    def test_audit_content_creation(self):
        """测试审核内容创建"""
        content = AuditContent(
            content="测试文本内容", file_type="text", metadata={"source": "test"}
        )

        assert content.content == "测试文本内容"
        assert content.file_type == "text"
        assert content.metadata == {"source": "test"}
        assert isinstance(content.id, UUID)

    def test_audit_content_defaults(self):
        """测试审核内容默认值"""
        content = AuditContent(content="测试文本")

        assert content.file_type == "text"
        assert content.metadata is None

    def test_audit_content_validation(self):
        """测试审核内容验证"""
        # 测试无效的文件类型
        with pytest.raises(ValueError):
            AuditContent(
                content="测试", file_type="invalid_type"  # 应该是 "text" 或 "image"
            )


class TestAuditOptionsItemModel:
    """测试审核项模型"""

    def test_audit_options_item_creation(self):
        """测试审核项创建"""
        item = AuditOptionsItem(
            name="测试审核项",
            instruction="测试审核指令",
            options={"选项1": "说明1", "选项2": "说明2"},
        )

        assert item.name == "测试审核项"
        assert item.instruction == "测试审核指令"
        assert item.options == {"选项1": "说明1", "选项2": "说明2"}
        assert isinstance(item.id, UUID)

    def test_audit_options_item_validation(self):
        """测试审核项验证"""
        # 测试空选项
        with pytest.raises(ValueError):
            AuditOptionsItem(name="测试", instruction="测试", options={})

        # 测试缺少必需字段
        with pytest.raises(ValueError):
            AuditOptionsItem(
                name="测试",
                instruction="测试",
                # 缺少options字段
            )


class TestAuditDecisionModel:
    """测试审核决策模型"""

    def test_audit_decision_creation(self):
        """测试审核决策创建"""
        decision = AuditDecision(choice="通过", reason="内容符合要求")

        assert decision.choice == "通过"
        assert decision.reason == "内容符合要求"

    def test_audit_decision_defaults(self):
        """测试审核决策默认值"""
        decision = AuditDecision(choice="测试", reason="测试原因")

        assert decision.choice == "测试"
        assert decision.reason == "测试原因"


class TestAuditResultModel:
    """测试审核结果模型"""

    def test_audit_result_creation(self):
        """测试审核结果创建"""
        # 创建依赖对象
        content = AuditContent(content="测试文本")
        item = AuditOptionsItem(name="测试项", instruction="测试", options={"是": "是"})
        decision = AuditDecision(choice="是", reason="测试原因")

        result = AuditResult(
            content_id=content.id,
            item_id=item.id,
            item_name=item.name,
            content_excerpt=content.content,
            decision=decision,
        )

        assert result.content_id == content.id
        assert result.item_id == item.id
        assert result.item_name == item.name
        assert result.content_excerpt == content.content
        assert result.decision == decision
        assert result.batch_id is None

    def test_audit_result_with_batch_id(self):
        """测试带批次ID的审核结果"""
        from uuid import uuid4

        batch_id = uuid4()
        result = AuditResult(
            batch_id=batch_id,
            content_id=uuid4(),
            item_id=uuid4(),
            item_name="测试项",
            content_excerpt="测试文本",
            decision=AuditDecision(choice="测试", reason="测试原因"),
        )

        assert result.batch_id == batch_id

    def test_audit_result_validation(self):
        """测试审核结果验证"""
        from uuid import uuid4

        # 测试缺少必需字段
        with pytest.raises(ValueError):
            AuditResult(
                content_id=uuid4(),
                item_id=uuid4(),
                # 缺少其他必需字段
            )


class TestModelIntegration:
    """测试模型集成"""

    def test_models_work_together(self):
        """测试模型协同工作"""
        # 创建完整的审核流程数据
        content = AuditContent(
            content="这是一个需要审核的文本内容",
            file_type="text",
            metadata={"category": "test"},
        )

        item = AuditOptionsItem(
            name="内容质量审核",
            instruction="评估文本内容的质量和完整性",
            options={
                "优秀": "内容质量很高",
                "良好": "内容质量不错",
                "一般": "内容质量一般",
                "较差": "内容质量需要改进",
            },
        )

        decision = AuditDecision(
            choice="良好", reason="内容结构清晰，表达准确，但可以进一步优化"
        )

        result = AuditResult(
            content_id=content.id,
            item_id=item.id,
            item_name=item.name,
            content_excerpt=content.content[:50] + "...",  # 截取前50字符
            decision=decision,
        )

        # 验证数据一致性
        assert result.content_id == content.id
        assert result.item_id == item.id
        assert result.item_name == item.name
        assert result.decision.choice in item.options

        # 验证决策理由
        assert len(result.decision.reason) > 0

    def test_model_serialization(self):
        """测试模型序列化"""
        # 测试模型可以转换为字典
        content = AuditContent(content="测试")
        content_dict = content.model_dump()

        assert "id" in content_dict
        assert "content" in content_dict
        assert "file_type" in content_dict

        # 测试从字典重建
        reconstructed = AuditContent(**content_dict)
        assert reconstructed.content == content.content
        assert reconstructed.file_type == content.file_type
