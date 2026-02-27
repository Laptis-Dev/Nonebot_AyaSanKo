# fmt: off
import json
from typing import cast, ClassVar
from pydantic import BaseModel, Field, field_validator, ConfigDict
from nonebot import get_driver
from nonebot.log import logger


class ManagerConfig(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="ignore", populate_by_name=True)

    global_switch: bool = Field(default=True)
    ban_keywords: list[str] = Field(default_factory=list)
    group_whitelist: list[int] = Field(default_factory=list)
    user_blacklist: list[int] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)

    @field_validator("ban_keywords", mode="before")
    @classmethod
    def parse_str_list(cls, v: object) -> list[str]:
        if isinstance(v, str):
            try:
                result = cast(list[object], json.loads(v))
                return [str(item) for item in result]
            except json.JSONDecodeError:
                logger.warning(f"解析 ban_keywords 失败: {v}，将使用空列表")
                return []
        if isinstance(v, (list, set)):
            return [str(item) for item in list(cast(list[object], v))]
        return []

    @field_validator("commands", mode="before")
    @classmethod
    def parse_commands(cls, v: object) -> list[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    parsed = cast(list[object], json.loads(v))
                    return [str(cmd).strip() for cmd in parsed if cmd]
                except json.JSONDecodeError:
                    pass
            return [p.strip() for p in v.split(",") if p.strip()]
        if isinstance(v, (list, set)):
            return [str(cmd).strip() for cmd in list(cast(list[object], v)) if cmd]
        return []

    @field_validator("group_whitelist", "user_blacklist", mode="before")
    @classmethod
    def parse_int_list(cls, v: object) -> list[int]:
        items: list[object] = []
        if isinstance(v, int):
            # 单个整数直接包装成列表
            return [v]
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    items = cast(list[object], json.loads(v))
                except json.JSONDecodeError:
                    pass
            if not items:
                items = [p.strip() for p in v.split(",") if p.strip()]
        elif isinstance(v, (list, set)):
            items = list(cast(list[object], v))
        else:
            return []
        result: list[int] = []
        for item in items:
            try:
                result.append(int(str(item)))
            except (ValueError, TypeError):
                logger.warning(f"无效的数字: {item}")
        return result

    @classmethod
    def from_env(cls) -> "ManagerConfig":
        global_config = get_driver().config
        dumped = global_config.model_dump()
        manager_data = cast(dict[str, object], dumped.get("manager", {}))
        logger.info(f"[DEBUG] manager_data: {manager_data}")
        result = cls.model_validate(manager_data)
        assert result is not None, "ManagerConfig.model_validate 不应返回 None"
        return result


# 内部配置实例
_config: ManagerConfig | None = None


def get_config() -> ManagerConfig:
    global _config
    if _config is None:
        _config = ManagerConfig.from_env()
        logger.info(f"管理器配置加载完成: 全局开关={_config.global_switch}, 白名单群={_config.group_whitelist}, 黑名单用户={_config.user_blacklist}, 命令={_config.commands}")
    return _config  # 此时 _config 已经不是 None，但 mypy 不知道


def reload_config() -> ManagerConfig:
    global _config
    new_config = ManagerConfig.from_env()
    _config = new_config
    logger.info(f"管理器配置已重新加载: 全局开关={new_config.global_switch}, 白名单群={new_config.group_whitelist}, 黑名单用户={new_config.user_blacklist}, 命令={new_config.commands}")
    return new_config
# fmt: on
