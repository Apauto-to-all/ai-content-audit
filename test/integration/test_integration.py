"""集成测试：测试整个AI内容审核系统的集成功能"""

import pytest
from ai_content_audit.audit_manager import AuditManager
from ai_content_audit.loader.data_loader import AuditContentLoader
from ai_content_audit.loader.checks_loader import AuditOptionsItemLoader
from ai_content_audit.models.audit_decision_model import AuditDecision


class TestIntegration:
    """集成测试类"""

    def test_complete_workflow_single_audit(self, mock_openai_client, mocker):
        """测试完整的单次审核工作流"""
        # 设置模拟响应
        mock_decision = AuditDecision(choice="无", reason="内容正常，未发现敏感信息")

        mock_message = mocker.Mock()
        mock_message.parsed = mock_decision

        mock_choice = mocker.Mock()
        mock_choice.message = mock_message

        mock_choices = [mock_choice]

        mock_response = mocker.Mock()
        mock_response.choices = mock_choices

        mock_openai_client.chat.completions.parse.return_value = mock_response

        # 1. 创建审核内容
        content = AuditContentLoader.create(
            content="这是一个正常的测试文本，不包含任何敏感信息。",
            file_type="text",
            metadata={"source": "integration_test"},
        )

        # 2. 创建审核项
        item = AuditOptionsItemLoader.create(
            name="敏感信息检测",
            instruction="检查文本中是否包含个人隐私、密钥等敏感信息",
            options={
                "有": "检测到敏感信息",
                "无": "未检测到敏感信息",
                "不确定": "无法确定是否包含敏感信息",
            },
        )

        # 3. 创建审核管理器并执行审核
        manager = AuditManager(client=mock_openai_client, model="test-model")
        result = manager.audit_one(content, item)

        # 4. 验证结果
        assert result.text_id == content.id
        assert result.item_id == item.id
        assert result.item_name == item.name
        assert result.text_excerpt == content.content
        assert result.decision.choice == "无"
        assert result.decision.reason == "内容正常，未发现敏感信息"

    def test_complete_workflow_batch_audit(self, mock_openai_client, mocker):
        """测试完整的批量审核工作流"""
        # 设置模拟响应
        mock_decision = AuditDecision(choice="通过", reason="内容质量良好")

        mock_message = mocker.Mock()
        mock_message.parsed = mock_decision

        mock_choice = mocker.Mock()
        mock_choice.message = mock_message

        mock_choices = [mock_choice]

        mock_response = mocker.Mock()
        mock_response.choices = mock_choices

        mock_openai_client.chat.completions.parse.return_value = mock_response

        # 1. 创建多个审核内容
        contents = [
            AuditContentLoader.create(content="第一个测试文本"),
            AuditContentLoader.create(content="第二个测试文本"),
            AuditContentLoader.create(content="第三个测试文本"),
        ]

        # 2. 创建多个审核项
        items = [
            AuditOptionsItemLoader.create(
                name="内容质量审核",
                instruction="评估文本内容的质量",
                options={"通过": "质量良好", "不通过": "质量需要改进"},
            ),
            AuditOptionsItemLoader.create(
                name="语法检查",
                instruction="检查文本语法是否正确",
                options={"正确": "语法正确", "错误": "存在语法错误"},
            ),
        ]

        # 3. 创建审核管理器并执行批量审核
        manager = AuditManager(client=mock_openai_client, model="test-model")
        results = manager.audit_batch(contents, items)

        # 4. 验证结果
        # 应该有 3个内容 × 2个审核项 = 6个结果
        assert len(results) == 6

        # 验证批次ID一致性
        batch_ids = {result.batch_id for result in results}
        assert len(batch_ids) == 1

        # 验证每个结果的结构
        for result in results:
            assert result.text_id in [c.id for c in contents]
            assert result.item_id in [i.id for i in items]
            assert result.decision.choice == "通过"

    def test_workflow_with_different_content_types(self, mock_openai_client, mocker):
        """测试不同类型内容的审核工作流"""
        # 设置模拟响应
        mock_decision = AuditDecision(choice="合适", reason="内容合适")

        mock_message = mocker.Mock()
        mock_message.parsed = mock_decision

        mock_choice = mocker.Mock()
        mock_choice.message = mock_message

        mock_choices = [mock_choice]

        mock_response = mocker.Mock()
        mock_response.choices = mock_choices

        mock_openai_client.chat.completions.parse.return_value = mock_response

        # 测试文本内容
        text_content = AuditContentLoader.create(
            content="这是一段文本内容", file_type="text"
        )

        # 测试图像内容（模拟）
        image_content = AuditContentLoader.create(
            content="base64_encoded_image_data",
            file_type="image",
            metadata={"format": "PNG", "size": "800x600"},
        )

        item = AuditOptionsItemLoader.create(
            name="内容适宜性审核",
            instruction="判断内容是否适宜",
            options={"合适": "内容适宜", "不合适": "内容不适宜"},
        )

        manager = AuditManager(client=mock_openai_client, model="test-model")

        # 测试文本审核
        text_result = manager.audit_one(text_content, item)
        assert text_result.decision.choice == "合适"

        # 测试图像审核
        image_result = manager.audit_one(image_content, item)
        assert image_result.decision.choice == "合适"

    def test_workflow_with_custom_metadata(self, mock_openai_client, mocker):
        """测试带自定义元数据的审核工作流"""
        mock_decision = AuditDecision(choice="分类正确", reason="内容分类准确")

        mock_message = mocker.Mock()
        mock_message.parsed = mock_decision

        mock_choice = mocker.Mock()
        mock_choice.message = mock_message

        mock_choices = [mock_choice]

        mock_response = mocker.Mock()
        mock_response.choices = mock_choices

        mock_openai_client.chat.completions.parse.return_value = mock_response

        # 创建带丰富元数据的内容
        content = AuditContentLoader.create(
            content="这是一篇关于人工智能的技术文章",
            file_type="text",
            metadata={
                "category": "技术",
                "author": "测试作者",
                "tags": ["AI", "机器学习", "深度学习"],
                "word_count": 1500,
                "language": "中文",
            },
        )

        item = AuditOptionsItemLoader.create(
            name="内容分类审核",
            instruction="根据内容判断其分类是否正确",
            options={
                "分类正确": "分类准确",
                "分类错误": "分类不准确",
                "需要调整": "分类需要微调",
            },
        )

        manager = AuditManager(client=mock_openai_client, model="test-model")
        result = manager.audit_one(content, item)

        # 元数据不应该影响审核结果
        assert result.decision.choice == "分类正确"

    def test_error_handling_in_workflow(self, mock_openai_client, mocker):
        """测试工作流中的错误处理"""
        # 模拟API调用失败
        mock_openai_client.chat.completions.parse.side_effect = Exception("API调用失败")

        content = AuditContentLoader.create(content="测试文本")
        item = AuditOptionsItemLoader.create(
            name="测试项", instruction="测试", options={"通过": "通过"}
        )

        manager = AuditManager(client=mock_openai_client, model="test-model")

        # 单次审核应该抛出异常
        with pytest.raises(Exception):
            manager.audit_one(content, item)

        # 批量审核应该使用回退机制
        results = manager.audit_batch([content], [item])
        assert len(results) == 1
        assert results[0].decision.choice == "Error"
        assert results[0].decision.reason == "模型调用失败"

    def test_performance_with_large_batch(self, mock_openai_client, mocker):
        """测试大批量处理的性能"""
        # 设置模拟响应
        mock_decision = AuditDecision(choice="测试", reason="测试原因")

        mock_message = mocker.Mock()
        mock_message.parsed = mock_decision

        mock_choice = mocker.Mock()
        mock_choice.message = mock_message

        mock_choices = [mock_choice]

        mock_response = mocker.Mock()
        mock_response.choices = mock_choices

        mock_openai_client.chat.completions.parse.return_value = mock_response

        # 创建大批量数据
        batch_size = 10
        contents = [
            AuditContentLoader.create(content=f"测试文本{i}") for i in range(batch_size)
        ]

        items = [
            AuditOptionsItemLoader.create(
                name=f"审核项{j}", instruction=f"审核指令{j}", options={"选项": "说明"}
            )
            for j in range(3)  # 3个审核项
        ]

        manager = AuditManager(client=mock_openai_client, model="test-model")

        # 执行批量审核
        results = manager.audit_batch(contents, items)

        # 验证结果数量
        expected_count = batch_size * len(items)
        assert len(results) == expected_count

        # 验证API调用次数
        assert mock_openai_client.chat.completions.parse.call_count == expected_count

    def test_message_building_integration(self, mock_openai_client, mocker):
        """测试消息构建与审核的集成"""
        # 设置模拟响应
        mock_decision = AuditDecision(choice="通过", reason="消息构建正确")

        mock_message = mocker.Mock()
        mock_message.parsed = mock_decision

        mock_choice = mocker.Mock()
        mock_choice.message = mock_message

        mock_choices = [mock_choice]

        mock_response = mocker.Mock()
        mock_response.choices = mock_choices

        mock_openai_client.chat.completions.parse.return_value = mock_response

        # 使用mocker.patch替代@patch装饰器
        mock_build_messages = mocker.patch(
            "ai_content_audit.audit_manager.build_messages"
        )
        mock_build_messages.return_value = [{"role": "user", "content": "测试消息"}]

        content = AuditContentLoader.create(content="测试文本")
        item = AuditOptionsItemLoader.create(
            name="测试", instruction="测试", options={"选项": "说明"}
        )

        manager = AuditManager(client=mock_openai_client, model="test-model")
        result = manager.audit_one(content, item)

        # 验证消息构建被调用
        mock_build_messages.assert_called_once_with(content=content, item=item)

        # 验证API调用使用了构建的消息
        mock_openai_client.chat.completions.parse.assert_called_once()
        call_args = mock_openai_client.chat.completions.parse.call_args
        assert call_args[1]["messages"] == [{"role": "user", "content": "测试消息"}]
