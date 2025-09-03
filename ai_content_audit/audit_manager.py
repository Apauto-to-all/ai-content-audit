from typing import Dict, List, Tuple, Optional, Union
from uuid import uuid4
from openai import OpenAI
from ai_content_audit.models import (
    AuditOptionsItem,
    AuditDecision,
    AuditText,
    AuditResult,
)
from ai_content_audit.prompts import build_messages


def _ensure_choice(choice: str | None, options: Dict[str, str]) -> str:
    """
    规范化审核结果的选择项，确保其在允许的选项范围内。

    此函数用于处理大模型输出的 choice 字段，可能存在拼写错误或不在选项中的情况。
    优先匹配精确选项，其次尝试匹配“不确定”类标签，最后回退到第一个选项。

    参数：
    - choice (str | None): 模型输出的原始选择项，可能为 None 或无效值。
    - options (Dict[str, str]): 审核项的选项映射，键为选项标签，值为说明。

    返回：
    - str: 规范化后的选择项，保证在 options 的键中。

    """
    if choice and choice in options:
        return choice
    # 尝试回退到“不确定”类标签
    for k in options.keys():
        if k in ("不确定", "无法判断", "Uncertain", "Unknown"):
            return k
    # 否则回退到第一个选项
    return next(iter(options.keys()))


class AuditManager:
    """
    审核管理器（类管理模式）

    职责：
    - 管理与大模型的交互（持有 client 与默认 model）。
    - 将审核项与审核文本组装为消息，调用模型生成结构化结果（AuditDecision）。
    - 支持批量审核，提高处理效率。
    """

    def __init__(self, client: OpenAI, model: str) -> None:
        """
        初始化审核管理器。

        参数：
        - client (OpenAI): OpenAI 兼容客户端，用于与大模型交互。应已配置 base_url 与 api_key。
        - model (str): 默认模型名称，方法调用时可临时覆盖。需与客户端兼容。

        使用场景：
        - 单文本审核：调用 audit_one 对单个文本应用单个审核项。
        - 批量审核：调用 audit_batch 对多个文本应用多个审核项，自动处理失败项。
        """
        self.client = client
        self.model = model

    def _audit_text_with_item(
        self,
        text: AuditText,
        item: AuditOptionsItem,
        *,
        client: Optional[OpenAI] = None,
        model: Optional[str] = None,
    ) -> AuditDecision:
        """
        内部方法：审核单个文本与单个审核项，返回 AuditDecision。

        参数：
        - text (AuditText): 待审核文本。
        - item (AuditOptionsItem): 审核项。
        - client (Optional[OpenAI]): 可选覆盖客户端。
        - model (Optional[str]): 可选覆盖模型。

        返回：
        - AuditDecision: 审核决策结果。
        """
        # 解析文本内容
        content = text.content

        # 构建消息
        messages = build_messages(content, item)

        # 选择客户端与模型（允许方法级覆盖）
        use_client = client or self.client
        use_model = model or self.model

        # 结构化输出（优先使用 parse -> Pydantic）
        resp = use_client.chat.completions.parse(
            model=use_model,
            messages=messages,
            response_format=AuditDecision,
        )
        result: AuditDecision = resp.choices[0].message.parsed

        # 结果兜底与清洗
        result.choice = _ensure_choice(result.choice, item.options)
        result.reason = (result.reason or "").strip() or "基于文本与选项说明给出的判定"
        return result

    def audit_one(
        self,
        text: AuditText,
        item: AuditOptionsItem,
        *,
        client: Optional[OpenAI] = None,
        model: Optional[str] = None,
    ) -> AuditResult:
        """
        审核单个文本与单个审核项。

        参数：
        - text (AuditText): 待审核文本，AuditText模型
        - item (AuditOptionsItem): 审核项定义，AuditOptionsItem模型
        - client (Optional[OpenAI]): 可选覆盖客户端。
        - model (Optional[str]): 可选覆盖模型。

        返回：
        - AuditResult: 包含完整的审核信息。

        示例：
        >>> from ai_content_audit import AuditManager, loader
        >>> from openai import OpenAI
        >>> client = OpenAI(base_url="https:/", api_key="your_api_key")
        >>> manager = AuditManager(client, model="qwen-plus")
        >>> text = loader.audit_data.create(content="这是一个示例文本，用于演示审核功能。")
        >>> item = loader.options_item.create(
        ...     name="是否包含敏感信息",
        ...     instruction="检查文本中是否出现用户定义的敏感信息（如个人隐私、密钥、内网地址等）。",
        ...     options={
        ...         "有": "检测有敏感信息",
        ...         "无": "没有检测到敏感信息",
        ...         "不确定": "无法判断是否含有敏感信息",
        ...     }
        ... )
        >>> result = manager.audit_one(text, item)
        >>> print("审核结果：")
        >>> print("=" * 60)
        >>> print(f"审核项: {result.item_name}")
        >>> print(f"文本节选: {result.text_excerpt}...")
        >>> print(f"决策: {result.decision.choice}")
        >>> print(f"理由: {result.decision.reason}")
        >>> print("=" * 60)
        """
        # 获取审核决策
        decision = self._audit_text_with_item(text, item, client=client, model=model)

        # 构建 AuditResult
        result = AuditResult(
            text_id=text.id,
            item_id=item.id,
            item_name=item.name,
            text_excerpt=text.content,
            decision=decision,
        )
        return result

    def audit_batch(
        self,
        text: List[AuditText],
        items: List[AuditOptionsItem],
        *,
        client: Optional[OpenAI] = None,
        model: Optional[str] = None,
    ) -> List[AuditResult]:
        """
        批量审核：对多个文本依次应用多个审核项。

        参数：
        - text (List[AuditText]): 待审核文本列表，每个文本将应用所有审核项。
        - items (List[AuditOptionsItem]): 审核项列表，对每个文本依次应用。
        - client (Optional[OpenAI]): 可选覆盖客户端。
        - model (Optional[str]): 可选覆盖模型。

        返回：
        - List[AuditResult]: 审核结果列表，每个元素包含完整的审核信息。

        失败策略：
        - 单项失败不影响其它项，失败项返回兜底 choice 与 "模型调用失败" 理由。
        - 整体不抛出异常，确保批量处理继续。

        示例：
        >>> from ai_content_audit import AuditManager, loader
        >>> from openai import OpenAI
        >>> client = OpenAI(base_url="https:/", api_key="your_api_key")
        >>> manager = AuditManager(client, model="qwen-plus")
        >>> texts = [
        ...     loader.audit_data.create(content="文本1"),
        ...     loader.audit_data.create(content="文本2")
        ... ]
        >>> items = [
        ...     loader.options_item.create(name="审核项1", instruction="指令1", options={"通过": "说明", "不通过": "说明"}),
        ...     loader.options_item.create(name="审核项2", instruction="指令2", options={"通过": "说明", "不通过": "说明"})
        ... ]
        >>> results = manager.audit_batch(texts, items)
        >>> # 打印批量结果
        >>> for i, res in enumerate(results, 1):
        ...     print(f"结果 {i}:")
        ...     print(f"  审核项: {res.item_name}")
        ...     print(f"  文本节选: {res.text_excerpt}...")
        ...     print(f"  决策: {res.decision.choice}")
        ...     print(f"  理由: {res.decision.reason}")
        ...     print("-" * 40)
        >>> print("=" * 80)
        """
        # 生成批次ID
        batch_id = uuid4()
        results: List[AuditResult] = []

        for t in text:
            for it in items:
                try:
                    decision = self._audit_text_with_item(
                        t, it, client=client, model=model
                    )
                    result = AuditResult(
                        batch_id=batch_id,
                        text_id=t.id,
                        item_id=it.id,
                        item_name=it.name,
                        text_excerpt=t.content,
                        decision=decision,
                    )
                    results.append(result)
                except Exception:
                    # 失败时创建兜底结果
                    fallback_decision = AuditDecision(
                        choice=_ensure_choice(None, it.options),
                        reason="模型调用失败",
                    )
                    result = AuditResult(
                        batch_id=batch_id,
                        text_id=t.id,
                        item_id=it.id,
                        item_name=it.name,
                        text_excerpt=t.content,
                        decision=fallback_decision,
                    )
                    results.append(result)
        return results
