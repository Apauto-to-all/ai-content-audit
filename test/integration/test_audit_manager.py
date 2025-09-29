"""测试审核管理器模块"""

import pytest
from ai_content_audit.audit_manager import AuditManager
from ai_content_audit.models import AuditDecision


class TestAuditManager:
    """测试审核管理器类"""

    def test_init_with_defaults(self, mock_openai_client):
        """测试使用默认参数初始化审核管理器"""
        manager = AuditManager(client=mock_openai_client)

        assert manager.client == mock_openai_client
        assert manager.model is None  # 默认应为None

    def test_init_with_parameters(self, mock_openai_client):
        """测试使用自定义参数初始化审核管理器"""
        manager = AuditManager(client=mock_openai_client, model="custom-model")

        assert manager.client == mock_openai_client
        assert manager.model == "custom-model"

    def test_audit_one_success(
        self, mock_openai_client, sample_audit_content, sample_audit_item, mocker
    ):
        """测试单次审核成功场景"""
        # 设置模拟响应
        mock_decision = AuditDecision(choice="无", reason="测试通过")

        # 正确设置Mock对象的层次结构
        mock_message = mocker.Mock()
        mock_message.parsed = mock_decision
        mock_choice = mocker.Mock()
        mock_choice.message = mock_message
        mock_response = mocker.Mock()
        mock_response.choices = [mock_choice]

        mock_openai_client.chat.completions.parse.return_value = mock_response

        manager = AuditManager(client=mock_openai_client, model="test-model")
        result = manager.audit_one(sample_audit_content, sample_audit_item)

        # 验证结果
        assert result.decision == mock_decision
        assert result.content_id == sample_audit_content.id
        assert result.item_id == sample_audit_item.id

        # 验证API调用
        mock_openai_client.chat.completions.parse.assert_called_once()

    def test_audit_one_with_override_parameters(
        self, mock_openai_client, sample_audit_content, sample_audit_item, mocker
    ):
        """测试单次审核时覆盖参数"""
        # 设置模拟响应
        mock_decision = AuditDecision(choice="有", reason="发现敏感信息")

        # 正确设置Mock对象的层次结构
        mock_message = mocker.Mock()
        mock_message.parsed = mock_decision
        mock_choice = mocker.Mock()
        mock_choice.message = mock_message
        mock_response = mocker.Mock()
        mock_response.choices = [mock_choice]

        mock_openai_client.chat.completions.parse.return_value = mock_response

        manager = AuditManager(client=mock_openai_client, model="test-model")
        result = manager.audit_one(
            sample_audit_content, sample_audit_item, model="override-model"
        )

        # 验证结果
        assert result.decision == mock_decision

        # 验证API调用使用了覆盖的参数
        mock_openai_client.chat.completions.parse.assert_called_once()
        call_args = mock_openai_client.chat.completions.parse.call_args
        assert call_args.kwargs.get("model") == "override-model"

    def test_audit_one_missing_client(self, sample_audit_content, sample_audit_item):
        """测试缺少客户端时的错误处理"""
        manager = AuditManager()

        with pytest.raises(ValueError, match="客户端未指定"):
            manager.audit_one(sample_audit_content, sample_audit_item)

    def test_audit_one_missing_model(
        self, mock_openai_client, sample_audit_content, sample_audit_item
    ):
        """测试缺少模型时的错误处理"""
        manager = AuditManager(client=mock_openai_client)

        with pytest.raises(ValueError, match="模型未指定"):
            manager.audit_one(sample_audit_content, sample_audit_item)

    def test_audit_batch_success(
        self, mock_openai_client, sample_audit_content, sample_audit_item, mocker
    ):
        """测试批量审核成功场景"""
        # 设置模拟响应
        mock_decision = AuditDecision(choice="无", reason="批量测试通过")

        # 正确设置Mock对象的层次结构
        mock_message = mocker.Mock()
        mock_message.parsed = mock_decision
        mock_choice = mocker.Mock()
        mock_choice.message = mock_message
        mock_response = mocker.Mock()
        mock_response.choices = [mock_choice]

        mock_openai_client.chat.completions.parse.return_value = mock_response

        contents = [sample_audit_content]
        items = [sample_audit_item]

        manager = AuditManager(client=mock_openai_client, model="test-model")
        results = manager.audit_batch(contents, items)

        # 验证结果数量
        assert len(results) == 1
        assert results[0].decision == mock_decision

        # 验证API调用次数
        assert mock_openai_client.chat.completions.parse.call_count == 1

    def test_audit_batch_with_fallback(
        self, mock_openai_client, sample_audit_content, sample_audit_item, mocker
    ):
        """测试批量审核中的失败回退机制"""
        # 设置模拟响应：第一次成功，第二次失败
        mock_decision = AuditDecision(choice="无", reason="成功")

        def side_effect(*args, **kwargs):
            if not hasattr(side_effect, "call_count"):
                side_effect.call_count = 0
            side_effect.call_count += 1

            if side_effect.call_count == 2:  # 第二次调用失败
                raise Exception("模拟API调用失败")

            # 正确设置Mock对象的层次结构
            mock_message = mocker.Mock()
            mock_message.parsed = mock_decision
            mock_choice = mocker.Mock()
            mock_choice.message = mock_message
            mock_response = mocker.Mock()
            mock_response.choices = [mock_choice]
            return mock_response

        mock_openai_client.chat.completions.parse.side_effect = side_effect

        contents = [sample_audit_content]
        items = [sample_audit_item, sample_audit_item]  # 两个相同的审核项

        manager = AuditManager(client=mock_openai_client, model="test-model")
        results = manager.audit_batch(contents, items)

        # 验证结果数量
        assert len(results) == 2

        # 验证第一个结果成功
        assert results[0].decision.choice == "无"
        assert results[0].decision.reason == "成功"

        # 验证第二个结果失败（应该返回错误决策）
        assert results[1].decision.choice == "ERROR"
        assert results[1].decision.reason.startswith("审核出现错误：")

    def test_audit_batch_empty_inputs(
        self, mock_openai_client, sample_audit_content, sample_audit_item
    ):
        """测试批量审核空输入"""
        manager = AuditManager(client=mock_openai_client, model="test-model")

        # 测试空内容列表
        results = manager.audit_batch([], [sample_audit_item])
        assert len(results) == 0

        # 测试空审核项列表
        results = manager.audit_batch([sample_audit_content], [])
        assert len(results) == 0

    def test_private_method_calls_build_messages(
        self, mock_openai_client, sample_audit_content, sample_audit_item, mocker
    ):
        """测试私有方法正确调用build_messages函数"""
        # 模拟build_messages函数
        mock_messages = [
            {"role": "system", "content": "系统提示"},
            {"role": "user", "content": "用户内容"},
        ]

        # 使用mocker.patch替代@patch装饰器
        mock_build_messages = mocker.patch(
            "ai_content_audit.audit_manager.build_messages", return_value=mock_messages
        )

        # 设置模拟响应
        mock_decision = AuditDecision(choice="测试", reason="测试原因")
        mock_message = mocker.Mock()
        mock_message.parsed = mock_decision
        mock_choice = mocker.Mock()
        mock_choice.message = mock_message
        mock_response = mocker.Mock()
        mock_response.choices = [mock_choice]
        mock_openai_client.chat.completions.parse.return_value = mock_response

        manager = AuditManager(client=mock_openai_client, model="test-model")
        result = manager.audit_one(sample_audit_content, sample_audit_item)

        # 验证build_messages被正确调用
        mock_build_messages.assert_called_once_with(
            content=sample_audit_content, item=sample_audit_item
        )

        # 验证结果
        assert result.decision == mock_decision
