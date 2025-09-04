import pytest
from ai_content_audit.audit_manager import AuditManager, _ensure_choice
from ai_content_audit.models import (
    AuditOptionsItem,
    AuditContent,
    AuditDecision,
    AuditResult,
)


class TestEnsureChoice:
    """测试 _ensure_choice 函数"""

    def test_exact_match(self):
        """测试精确匹配"""
        options = {"有": "desc", "无": "desc"}
        assert _ensure_choice("有", options) == "有"

    def test_uncertain_fallback(self):
        """测试回退到不确定标签"""
        options = {"不确定": "desc", "有": "desc"}
        assert _ensure_choice("invalid", options) == "不确定"

    def test_first_option_fallback(self):
        """测试回退到第一个选项"""
        options = {"无": "desc", "有": "desc"}
        assert _ensure_choice("invalid", options) == "无"

    def test_none_choice(self):
        """测试 None 输入"""
        options = {"有": "desc"}
        assert _ensure_choice(None, options) == "有"


class TestAuditManager:
    """测试 AuditManager 类"""

    @pytest.fixture
    def mock_client(self, mocker):
        """模拟 OpenAI 客户端"""
        client = mocker.Mock()
        mock_response = mocker.Mock()
        mock_choice = mocker.Mock()
        mock_choice.message.parsed = AuditDecision(choice="有", reason="测试理由")
        mock_response.choices = [mock_choice]
        client.chat.completions.parse.return_value = mock_response
        return client

    @pytest.fixture
    def manager(self, mock_client):
        """创建 AuditManager 实例"""
        return AuditManager(client=mock_client, model="test-model")

    @pytest.fixture
    def sample_text(self):
        """示例 AuditContent"""
        return AuditContent(content="测试文本", source="test", file_type="text")

    @pytest.fixture
    def sample_item(self):
        """示例 AuditOptionsItem"""
        return AuditOptionsItem(
            name="测试项", instruction="测试指令", options={"有": "desc", "无": "desc"}
        )

    def test_init(self, mock_client):
        """测试初始化"""
        manager = AuditManager(client=mock_client, model="test-model")
        assert manager.client == mock_client
        assert manager.model == "test-model"

    def test_audit_one_success(self, manager, sample_text, sample_item, mock_client):
        """测试 audit_one 成功"""
        result = manager.audit_one(sample_text, sample_item)

        assert isinstance(result, AuditResult)
        assert result.text_id == sample_text.id
        assert result.item_id == sample_item.id
        assert result.item_name == sample_item.name
        assert result.text_excerpt == sample_text.content
        assert result.decision.choice == "有"
        assert result.decision.reason == "测试理由"

        # 验证客户端调用
        mock_client.chat.completions.parse.assert_called_once()

    def test_audit_one_with_overrides(
        self, manager, sample_text, sample_item, mock_client, mocker
    ):
        """测试 audit_one 带覆盖参数"""
        override_client = mocker.Mock()
        override_client.chat.completions.parse.return_value = mocker.Mock(
            choices=[
                mocker.Mock(
                    message=mocker.Mock(
                        parsed=AuditDecision(choice="无", reason="覆盖理由")
                    )
                )
            ]
        )

        result = manager.audit_one(
            sample_text, sample_item, client=override_client, model="override-model"
        )

        assert result.decision.choice == "无"
        assert result.decision.reason == "覆盖理由"

        # 验证使用覆盖客户端
        override_client.chat.completions.parse.assert_called_once()

    def test_audit_batch_success(self, manager, sample_text, sample_item, mock_client):
        """测试 audit_batch 成功"""
        texts = [sample_text]
        items = [sample_item]

        results = manager.audit_batch(texts, items)

        assert len(results) == 1
        result = results[0]
        assert isinstance(result, AuditResult)
        assert result.batch_id is not None
        assert result.text_id == sample_text.id
        assert result.item_id == sample_item.id

    def test_audit_batch_multiple(self, manager, mock_client, mocker):
        """测试 audit_batch 多个文本和项"""
        text1 = AuditContent(content="文本1", file_type="text")
        text2 = AuditContent(content="文本2", file_type="text")
        item1 = AuditOptionsItem(
            name="项1", instruction="指令1", options={"有": "desc"}
        )
        item2 = AuditOptionsItem(
            name="项2", instruction="指令2", options={"无": "desc"}
        )

        # 模拟不同响应
        responses = [
            mocker.Mock(
                choices=[
                    mocker.Mock(
                        message=mocker.Mock(
                            parsed=AuditDecision(choice="有", reason="理由1")
                        )
                    )
                ]
            ),
            mocker.Mock(
                choices=[
                    mocker.Mock(
                        message=mocker.Mock(
                            parsed=AuditDecision(choice="无", reason="理由2")
                        )
                    )
                ]
            ),
            mocker.Mock(
                choices=[
                    mocker.Mock(
                        message=mocker.Mock(
                            parsed=AuditDecision(choice="有", reason="理由3")
                        )
                    )
                ]
            ),
            mocker.Mock(
                choices=[
                    mocker.Mock(
                        message=mocker.Mock(
                            parsed=AuditDecision(choice="无", reason="理由4")
                        )
                    )
                ]
            ),
        ]
        mock_client.chat.completions.parse.side_effect = responses

        results = manager.audit_batch([text1, text2], [item1, item2])

        assert len(results) == 4  # 2 texts * 2 items
        assert all(isinstance(r, AuditResult) for r in results)
        assert len(set(r.batch_id for r in results)) == 1  # 同一批次

    def test_audit_batch_failure_handling(
        self, manager, sample_text, sample_item, mock_client
    ):
        """测试 audit_batch 失败处理"""
        # 模拟异常
        mock_client.chat.completions.parse.side_effect = Exception("API 错误")

        results = manager.audit_batch([sample_text], [sample_item])

        assert len(results) == 1
        result = results[0]
        assert result.decision.choice == "有"  # 兜底选择
        assert result.decision.reason == "模型调用失败"

    def test_audit_batch_with_overrides(
        self, manager, sample_text, sample_item, mocker
    ):
        """测试 audit_batch 带覆盖参数"""
        override_client = mocker.Mock()
        override_client.chat.completions.parse.return_value = mocker.Mock(
            choices=[
                mocker.Mock(
                    message=mocker.Mock(
                        parsed=AuditDecision(choice="无", reason="覆盖理由")
                    )
                )
            ]
        )

        results = manager.audit_batch(
            [sample_text], [sample_item], client=override_client, model="override-model"
        )

        assert len(results) == 1
        assert results[0].decision.choice == "无"

        # 验证使用覆盖客户端
        override_client.chat.completions.parse.assert_called_once()
