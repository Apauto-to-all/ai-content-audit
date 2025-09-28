"""测试消息构建器模块"""

from ai_content_audit.prompts.build_messages import build_messages
from ai_content_audit.models import AuditContent, AuditOptionsItem


class TestBuildMessages:
    """测试消息构建函数"""

    def test_build_messages_text_content(self):
        """测试构建文本内容的审核消息"""
        content = AuditContent(content="这是一个需要审核的文本内容。", file_type="text")

        item = AuditOptionsItem(
            name="内容质量审核",
            instruction="请评估文本内容的质量",
            options={
                "优秀": "内容质量很高",
                "良好": "内容质量不错",
                "一般": "内容质量一般",
            },
        )

        messages = build_messages(content=content, item=item)

        # 验证消息结构（应该包含system和user两个消息）
        assert len(messages) == 2

        # 验证system消息
        system_message = messages[0]
        assert system_message["role"] == "system"
        assert "content" in system_message
        assert "内容审核助手" in system_message["content"]

        # 验证user消息
        user_message = messages[1]
        assert user_message["role"] == "user"
        assert "content" in user_message

        # 验证消息内容包含必要信息
        message_content = user_message["content"]
        assert item.name in message_content
        assert item.instruction in message_content
        assert "这是一个需要审核的文本内容" in message_content

        # 验证选项被正确格式化
        for option_key, option_desc in item.options.items():
            assert option_key in message_content
            assert option_desc in message_content

    def test_build_messages_image_content(self):
        """测试构建图像内容的审核消息"""
        content = AuditContent(content="base64_encoded_image_data", file_type="image")

        item = AuditOptionsItem(
            name="图像内容审核",
            instruction="请审核图像内容是否合适",
            options={"合适": "图像内容合适", "不合适": "图像内容不合适"},
        )

        messages = build_messages(content=content, item=item)

        # 验证消息结构（应该包含system和user两个消息）
        assert len(messages) == 2

        # 验证system消息
        system_message = messages[0]
        assert system_message["role"] == "system"
        assert "content" in system_message

        # 验证user消息
        user_message = messages[1]
        assert user_message["role"] == "user"
        assert "content" in user_message

        # 验证图像内容处理
        message_content = user_message["content"]
        assert isinstance(message_content, list)

        # 应该包含图像部分和文本部分
        assert len(message_content) == 2

        # 第一个元素应该是图像
        image_part = message_content[0]
        assert image_part["type"] == "image_url"
        assert "image_url" in image_part
        assert "url" in image_part["image_url"]
        assert image_part["image_url"]["url"] == "base64_encoded_image_data"

        # 第二个元素应该是文本
        text_part = message_content[1]
        assert text_part["type"] == "text"
        assert item.name in text_part["text"]
        assert item.instruction in text_part["text"]

    def test_build_messages_with_metadata(self):
        """测试构建带元数据的审核消息"""
        content = AuditContent(
            content="测试文本",
            file_type="text",
            metadata={"source": "用户提交", "category": "技术文章"},
        )

        item = AuditOptionsItem(
            name="测试审核", instruction="测试审核", options={"通过": "通过"}
        )

        messages = build_messages(content=content, item=item)

        # 元数据不应该影响消息结构
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_build_messages_empty_options(self):
        """测试构建空选项的审核消息"""
        content = AuditContent(content="测试文本")

        # 创建只有一个选项的审核项
        item = AuditOptionsItem(
            name="单选项审核",
            instruction="单选项测试",
            options={"唯一选项": "只有一个选项"},
        )

        messages = build_messages(content=content, item=item)

        # 应该正常构建消息
        assert len(messages) == 2
        user_message = messages[1]
        assert "唯一选项" in user_message["content"]

    def test_build_messages_long_content(self):
        """测试构建长内容的审核消息"""
        # 创建长文本内容
        long_text = "这是一个很长的文本内容。" * 100
        content = AuditContent(content=long_text)

        item = AuditOptionsItem(
            name="长文本审核",
            instruction="审核长文本内容",
            options={"通过": "通过", "不通过": "不通过"},
        )

        messages = build_messages(content=content, item=item)

        # 应该正常构建消息
        assert len(messages) == 2
        user_message = messages[1]

        # 长文本应该被包含在消息中
        message_content = user_message["content"]
        assert "这是一个很长的文本内容" in message_content

    def test_build_messages_special_characters(self):
        """测试构建包含特殊字符的审核消息"""
        content = AuditContent(content="包含特殊字符的文本：@#$%^&*()")

        item = AuditOptionsItem(
            name="特殊字符审核",
            instruction="审核包含特殊字符的文本",
            options={"安全": "特殊字符安全", "不安全": "特殊字符不安全"},
        )

        messages = build_messages(content=content, item=item)

        # 应该正常构建消息
        assert len(messages) == 2
        user_message = messages[1]

        # 特殊字符应该被正确处理
        message_content = user_message["content"]
        assert "@#$%^&*()" in message_content

    def test_build_messages_instruction_formatting(self):
        """测试指令格式化的正确性"""
        content = AuditContent(content="测试文本")

        item = AuditOptionsItem(
            name="格式化测试",
            instruction="这是一个多行指令\n第二行指令\n第三行指令",
            options={"选项1": "说明1", "选项2": "说明2"},
        )

        messages = build_messages(content=content, item=item)

        # 多行指令应该被正确处理
        message_content = messages[1]["content"]
        assert "这是一个多行指令" in message_content
        assert "第二行指令" in message_content
        assert "第三行指令" in message_content

    def test_build_messages_options_ordering(self):
        """测试选项顺序的保持"""
        content = AuditContent(content="测试文本")

        # 创建有特定顺序的选项
        options = {
            "第一选项": "第一个选项",
            "第二选项": "第二个选项",
            "第三选项": "第三个选项",
        }

        item = AuditOptionsItem(
            name="顺序测试", instruction="测试选项顺序", options=options
        )

        messages = build_messages(content=content, item=item)

        message_content = messages[1]["content"]

        # 验证选项顺序（Python 3.7+ 保持字典插入顺序）
        option_keys = list(options.keys())
        first_pos = message_content.find(option_keys[0])
        second_pos = message_content.find(option_keys[1])
        third_pos = message_content.find(option_keys[2])

        # 选项应该按照字典顺序出现
        assert first_pos < second_pos < third_pos
