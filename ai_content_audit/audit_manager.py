from typing import List, Optional
from openai import OpenAI
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from ai_content_audit.models import (
    AuditOptionsItem,
    AuditDecision,
    AuditContent,
    AuditResult,
)
from ai_content_audit.prompts import build_messages


class AuditManager:
    """
    审核管理器

    职责：
    - 管理与大模型的交互，调用模型生成审核决策。
    - 将审核项与审核文本组装为消息，调用模型生成结构化结果（AuditDecision）。
    - 支持批量审核，提高处理效率。
    """

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: Optional[str] = None,
    ) -> None:
        """
        初始化审核管理器。

        参数：
        - client (OpenAI, optional): 默认 OpenAI 兼容客户端，用于与大模型交互，方法调用时可临时覆盖。默认值为 None。
        - model (str, optional): 默认模型名称，方法调用时可临时覆盖，需与客户端兼容。默认值为 None。

        使用场景：
        - 单文本审核：调用 audit_one 对单个文本应用单个审核项。
        - 批量审核：调用 audit_batch 对多个文本应用多个审核项，自动处理失败项。
        """
        self.client = client
        self.model = model

    def _audit_content_with_item(
        self,
        content: AuditContent,
        item: AuditOptionsItem,
        *,
        client: Optional[OpenAI] = None,
        model: Optional[str] = None,
    ) -> AuditDecision:
        """
        内部方法：审核单个待审核内容与单个审核项，返回 AuditDecision。

        参数：
        - content (AuditContent): 待审核内容。
        - item (AuditOptionsItem): 审核项。
        - client (Optional[OpenAI]): 可选覆盖客户端。
        - model (Optional[str]): 可选覆盖模型。

        返回：
        - AuditDecision: 审核决策结果。
        """
        # 选择客户端与模型（允许方法级覆盖）
        use_client = client or self.client
        if not use_client:
            raise ValueError(
                "client OpenAI 客户端未指定，无法执行审核。请在初始化时指定默认客户端，或在方法调用时指定 client 参数。"
            )
        use_model = model or self.model
        if not use_model:
            raise ValueError(
                "模型未指定，无法执行审核。请在初始化时指定默认模型，或在方法调用时指定 model 参数。"
            )

        try:
            # 构建消息
            messages = build_messages(content=content, item=item)

            # 结构化输出（优先使用 parse -> Pydantic）
            resp = use_client.chat.completions.parse(
                model=use_model,
                messages=messages,
                response_format=AuditDecision,
            )
            result: AuditDecision = resp.choices[0].message.parsed

        except Exception as e:
            result = AuditDecision(
                choice="ERROR",
                reason="审核错误",
            )

        return result

    def audit_one(
        self,
        content: AuditContent,
        item: AuditOptionsItem,
        *,
        client: Optional[OpenAI] = None,
        model: Optional[str] = None,
    ) -> AuditResult:
        """
        审核单个内容与单个审核项。

        参数：
        - content (AuditContent): 待审核内容，AuditContent模型
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
        >>> content = loader.audit_data.create(content="这是一个示例文本，用于演示审核功能。")
        >>> item = loader.options_item.create(
        ...     name="是否包含敏感信息",
        ...     instruction="检查文本中是否出现用户定义的敏感信息（如个人隐私、密钥、内网地址等）。",
        ...     options={
        ...         "有": "检测有敏感信息",
        ...         "无": "没有检测到敏感信息",
        ...         "不确定": "无法判断是否含有敏感信息",
        ...     }
        ... )
        >>> result = manager.audit_one(content, item)
        >>> print("审核结果：")
        >>> print("=" * 60)
        >>> print(f"审核项: {result.item_name}")
        >>> print(f"文本节选: {result.text_excerpt}...")
        >>> print(f"决策: {result.decision.choice}")
        >>> print(f"理由: {result.decision.reason}")
        >>> print("=" * 60)
        """
        # 获取审核决策
        decision = self._audit_content_with_item(
            content, item, client=client, model=model
        )

        # 构建 AuditResult
        result = AuditResult(
            text_id=content.id,
            item_id=item.id,
            item_name=item.name,
            text_excerpt=content.content,
            decision=decision,
        )
        return result

    def audit_batch(
        self,
        contents: List[AuditContent],
        items: List[AuditOptionsItem],
        *,
        max_concurrency: int = 5,
        client: Optional[OpenAI] = None,
        model: Optional[str] = None,
    ) -> List[AuditResult]:
        """
        批量审核：对多个内容依次应用多个审核项，支持并发处理。

        参数：
        - contents (List[AuditContent]): 待审核内容列表，每个内容将应用所有审核项。
        - items (List[AuditOptionsItem]): 审核项列表，对每个内容依次应用。
        - max_concurrency (int): 最大并发数，默认5，控制同时处理的请求数量。
        - client (Optional[OpenAI]): 可选覆盖客户端。
        - model (Optional[str]): 可选覆盖模型。

        返回：
        - List[AuditResult]: 审核结果列表，按任务完成顺序返回。

        失败策略：
        - 单项失败不影响其它项，失败项返回兜底 choice 与 "模型调用失败" 理由。
        - 整体不抛出异常，确保批量处理继续。

        示例：
        >>> from ai_content_audit import AuditManager, loader
        >>> from openai import OpenAI
        >>> client = OpenAI(base_url="https:/", api_key="your_api_key")
        >>> manager = AuditManager(client, model="qwen-plus")
        >>> contents = [
        ...     loader.audit_data.create(content="文本1"),
        ...     loader.audit_data.create(content="文本2")
        ... ]
        >>> items = [
        ...     loader.options_item.create(name="审核项1", instruction="指令1", options={"通过": "说明", "不通过": "说明"}),
        ...     loader.options_item.create(name="审核项2", instruction="指令2", options={"通过": "说明", "不通过": "说明"})
        ... ]
        >>> # 使用默认并发数5
        >>> results = manager.audit_batch(contents, items)
        >>> # 或指定并发数
        >>> results = manager.audit_batch(contents, items, max_concurrency=3)
        >>> # 打印批量结果（注意：顺序可能与输入不一致）
        >>> for i, res in enumerate(results, 1):
        ...     print(f"结果 {i}:")
        ...     print(f"  审核项: {res.item_name}")
        ...     print(f"  内容节选: {res.text_excerpt}...")
        ...     print(f"  决策: {res.decision.choice}")
        ...     print(f"  理由: {res.decision.reason}")
        ...     print("-" * 40)
        >>> print("=" * 80)
        """
        # 检测是否有任务
        if not contents or not items:
            return []

        # 生成批量任务 ID
        batch_id = uuid4()

        # 绑定 client/model 到工作函数
        worker_fn = partial(self._audit_content_with_item, client=client, model=model)

        # 两个惰性可迭代器，按嵌套顺序生成 (content, item) 对
        contents_iter = (content for content in contents for _ in range(len(items)))
        items_iter = (item for _ in contents for item in items)

        # 在 with 块内消费 executor.map 的迭代器，按嵌套顺序逐个取出 decision 并构造结果
        with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
            decision_iter = executor.map(worker_fn, contents_iter, items_iter)

        return [
            AuditResult(
                batch_id=batch_id,
                text_id=content.id,
                item_id=item.id,
                item_name=item.name,
                text_excerpt=content.content,
                decision=next(decision_iter),
            )
            for content in contents
            for item in items
        ]
