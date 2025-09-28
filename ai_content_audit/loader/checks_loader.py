from typing import Any, Dict, Mapping
from pydantic import ValidationError
from ai_content_audit.models import AuditOptionsItem


class AuditOptionsItemLoader:
    """
    审核项加载器

    目标
    - 统一“创建/加载/批量加载”审核项的入口。
    - 提供清晰的类型标注与错误信息。
    - 易扩展：后续可加 TOML/YAML、模板库等。

    使用方法：
    - 创建审核项：使用 create() 方法创建。
    - 从字典加载：使用 from_dict() 方法从字典数据加载。
    - 从 JSON 文件加载：使用 from_json_file() 方法从 JSON 文件加载。
    """

    # 直接创建
    @staticmethod
    def create(
        name: str, instruction: str, options: Dict[str, str]
    ) -> AuditOptionsItem:
        """
        创建一个审核项，用于定义审核规则和选项。

        参数：
        - name (str): 审核项的名称。
        - instruction (str): 审核的判定依据说明，告诉模型如何判断。
        - options (dict[str, str]): 审核选项映射，键为选项标签，值为该选项的含义说明。

        返回：
        - AuditOptionsItem: 构建好的审核项对象，可直接用于审核管理器。

        示例：
        >>> from ai_content_audit import loader
        >>> item = loader.options_item.create(
        ...     name="是否包含敏感信息",
        ...     instruction="检查文本中是否出现用户定义的敏感信息（如个人隐私、密钥、内网地址等）。",
        ...     options={
        ...         "有": "检测有敏感信息",
        ...         "无": "没有检测到敏感信息",
        ...         "不确定": "无法判断是否含有敏感信息",
        ...     }
        ... )
        """
        return AuditOptionsItem(name=name, instruction=instruction, options=options)

    # 从字典加载（常用于外部配置转入）
    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> AuditOptionsItem:
        """
        从字典加载一个审核项，用于定义审核规则和选项。

        参数：
        - data (Mapping[str, Any]): 包含审核项字段的字典，必须包含 name、instruction 和 options 键。

        返回：
        - AuditOptionsItem: 构建好的审核项对象，可直接用于审核管理器。

        异常：
        - KeyError: 缺少必须字段 (name/instruction/options)
        - ValidationError: 字段类型或内容不合法
        - ValueError: 入参 data 不是映射类型

        示例：
        >>> from ai_content_audit import loader
        >>> data = {
        ...     "name": "是否包含敏感信息",
        ...     "instruction": "检查文本中是否出现用户定义的敏感信息（如个人隐私、密钥、内网地址等）。",
        ...     "options": {
        ...         "有": "检测有敏感信息",
        ...         "无": "没有检测到敏感信息",
        ...         "不确定": "无法判断是否含有敏感信息",
        ...     }
        ... }
        >>> item = loader.options_item.from_dict(data)
        """
        try:
            return AuditOptionsItem(**data)  # 交给 Pydantic 做强校验
        except ValidationError:
            # 透传更友好的异常信息
            raise
        except TypeError as e:
            raise ValueError(
                f"入参 data 必须是映射类型，实际为: {type(data).__name__}"
            ) from e
