import os
from nonebot.log import logger
from pydantic import BaseModel, Field


class ChatConfig(BaseModel):
    """聊天插件配置"""

    api_key: str | None = Field(default=None, description="API密钥")
    api_base: str = Field(
        default="https://open.bigmodel.cn/api/paas/v4", description="API地址"
    )
    model: str = Field(default="glm-4.5-air", description="使用的模型")
    max_tokens: int = Field(default=1000, description="最大令牌数")
    temperature: float = Field(default=1.0, description="回复温度")
    timeout: int = Field(default=30, description="API超时时间(秒)")
    max_concurrent: int = Field(default=5, description="最大并发请求数")
    max_history: int = Field(default=10, description="最大历史消息数")
    storage_backend: str = Field(default="memory", description="存储后端(memory/redis)")

    @classmethod
    def from_env(cls) -> "ChatConfig":
        """从环境变量加载配置（兼容 NoneBot2 的 .env 命名规则）"""
        try:
            # 手动加载.env文件（NoneBot可能没有自动加载）
            from dotenv import load_dotenv

            env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
            if os.path.exists(env_path):
                _ = load_dotenv(env_path)
                logger.info("[SUCCESS] 手动加载.env文件成功")
            else:
                logger.warning("[WARNING] .env文件不存在,使用现有环境变量")

            # 安全转换环境变量
            def safe_int(value: str | None, default: int) -> int:
                if value is None:
                    return default
                try:
                    return int(value)
                except (ValueError, TypeError):
                    logger.warning(
                        f"环境变量 {value} 无法转换为整数，使用默认值 {default}"
                    )
                    return default

            def safe_float(value: str | None, default: float) -> float:
                if value is None:
                    return default
                try:
                    return float(value)
                except (ValueError, TypeError):
                    logger.warning(
                        f"环境变量 {value} 无法转换为浮点数，使用默认值 {default}"
                    )
                    return default

            api_key = os.getenv("CHAT__API_KEY") or os.getenv("CHAT_API_KEY")

            return cls(
                api_key=api_key,
                api_base=os.getenv(
                    "CHAT__API_BASE", "https://open.bigmodel.cn/api/paas/v4"
                ),
                model=os.getenv("CHAT__MODEL", "glm-4.5-air"),
                max_tokens=safe_int(os.getenv("CHAT__MAX_TOKENS"), 1000),
                temperature=safe_float(os.getenv("CHAT__TEMPERATURE"), 1.0),
                timeout=safe_int(os.getenv("CHAT__TIMEOUT"), 30),
            )
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            # 返回默认配置
            return cls()

    model_config = {  # pyright: ignore[reportUnannotatedClassAttribute]
        "extra": "ignore"
    }

    def _safe_int(self, value: str | None, default: int) -> int:
        """安全转换整数（用于测试）"""
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"环境变量 {value} 无法转换为整数，使用默认值 {default}")
            return default

    def _safe_float(self, value: str | None, default: float) -> float:
        """安全转换浮点数（用于测试）"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"环境变量 {value} 无法转换为浮点数，使用默认值 {default}")
            return default
