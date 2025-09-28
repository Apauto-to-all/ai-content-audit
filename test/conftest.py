"""pytest 配置文件，用于设置测试环境和共享的fixture"""

import pytest
from openai import OpenAI


@pytest.fixture
def mock_openai_client(mocker):
    """创建模拟的 OpenAI 客户端"""
    mock_client = mocker.Mock(spec=OpenAI)
    mock_client.chat.completions.parse = mocker.Mock()
    return mock_client


@pytest.fixture
def sample_audit_content():
    """创建示例审核内容"""
    from ai_content_audit.loader.data_loader import AuditContentLoader

    return AuditContentLoader.create(
        content="这是一个测试文本内容，用于单元测试。",
        file_type="text",
        metadata={"source": "test"},
    )


@pytest.fixture
def sample_audit_item():
    """创建示例审核项"""
    from ai_content_audit.loader.checks_loader import AuditOptionsItemLoader

    return AuditOptionsItemLoader.create(
        name="是否包含敏感信息",
        instruction="检查文本中是否出现敏感信息",
        options={
            "有": "检测有敏感信息",
            "无": "没有检测到敏感信息",
            "不确定": "无法判断是否含有敏感信息",
        },
    )


@pytest.fixture
def sample_audit_decision():
    """创建示例审核决策"""
    from ai_content_audit.models.audit_decision_model import AuditDecision

    return AuditDecision(choice="无", reason="文本内容正常，未发现敏感信息")
