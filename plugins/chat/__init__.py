from nonebot import on_message, get_driver
from nonebot.adapters import Bot as BaseBot, Event
from nonebot.log import logger
from nonebot.exception import FinishedException
from nonebot.internal.matcher import Matcher
import time
from typing import TypedDict, TypeGuard, TYPE_CHECKING
from collections.abc import Mapping

# 仅在类型检查时导入具体类型，用于类型收窄
# fmt: off
if TYPE_CHECKING:
    from nonebot.adapters.qq import Bot as QQBot, MessageEvent as QQMessageEvent  # pyright: ignore[reportUnusedImport]
    from nonebot.adapters.onebot.v11 import (
        Bot as OneBotV11Bot,  # pyright: ignore[reportUnusedImport]
        MessageEvent as OneBotV11MessageEvent,  # pyright: ignore[reportUnusedImport]
    )

# 运行时动态检查适配器是否可用（使用小写变量名避免常量重定义警告）
try:
    import nonebot.adapters.qq  # pyright: ignore[reportUnusedImport]

    _qq_available = True
except ImportError:
    _qq_available = False

try:
    import nonebot.adapters.onebot.v11  # pyright: ignore[reportUnusedImport]

    _onebot_v11_available = True
except ImportError:
    _onebot_v11_available = False

# 其余导入保持不变
from .config import ChatConfig
from .processor import ChatProcessor
# fmt: off


# ---------- 类型定义 ----------
class ChoiceMessage(TypedDict):
    content: str


class Choice(TypedDict):
    message: ChoiceMessage


class ApiResponse(TypedDict):
    choices: list[Choice]


# ---------- 类型守卫 ----------
def is_send_response(obj: object) -> TypeGuard[dict[str, object]]:
    """判断对象是否为包含 message_id 的字典"""
    return isinstance(obj, dict) and "message_id" in obj


# fmt: off
def is_api_response(obj: object) -> TypeGuard[ApiResponse]:
    if not isinstance(obj, dict):
        return False
    choices = obj.get("choices")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    if not isinstance(choices, list):
        return False
    if not choices:
        return False
    first_choice: object = choices[0]  # 明确注解  # pyright: ignore[reportUnknownVariableType]
    if not isinstance(first_choice, dict):
        return False
    message: object = first_choice.get("message")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    if not isinstance(message, dict):
        return False
    content: object = message.get("content")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    if not isinstance(content, str):
        return False
    return True
# fmt: on


# 创建消息匹配器，监听所有消息
chat = on_message(priority=5, block=False)

# 获取插件配置
plugin_config: ChatConfig | None = None
try:
    plugin_config = ChatConfig.from_env()
    logger.info(
        f"Plugin config loaded: api_key={'***' if plugin_config.api_key else 'None'}"
    )
except Exception as e:
    logger.error(f"聊天插件配置加载失败: {e}")

# 从全局配置获取 NICKNAME
driver = get_driver()
config = driver.config
nicknames: list[str] = []

# 尝试获取 NICKNAME 配置（NoneBot2 标准配置）
if hasattr(config, "nickname"):
    nicknames_raw = config.nickname
    if isinstance(nicknames_raw, str):
        nicknames = [nicknames_raw]
    elif isinstance(nicknames_raw, list):
        nicknames = nicknames_raw
    logger.info(f"Loaded nicknames from config: {nicknames}")

# 如果没有配置昵称，使用默认值
if not nicknames:
    nicknames = ["猫猫"]
    logger.info(f"Using default nicknames: {nicknames}")

# 创建聊天处理器
chat_processor: ChatProcessor | None = None
if plugin_config:
    try:
        chat_processor = ChatProcessor(plugin_config)
        logger.info(f"Chat processor initialized: {bool(chat_processor)}")
    except Exception as e:
        logger.error(f"聊天处理器初始化失败: {e}")


# ---------- 协议检测函数 ----------
def get_bot_type(bot: BaseBot) -> str:
    """检测机器人类型"""
    if _qq_available:
        # 在类型检查时，QQBot 是已知的
        if TYPE_CHECKING:
            from nonebot.adapters.qq import Bot as QQBotType
        else:
            # 运行时动态获取
            from nonebot.adapters.qq import Bot as QQBotType
        if isinstance(bot, QQBotType):
            return "qq_official"

    if _onebot_v11_available:
        if TYPE_CHECKING:
            from nonebot.adapters.onebot.v11 import Bot as OneBotV11BotType
        else:
            from nonebot.adapters.onebot.v11 import Bot as OneBotV11BotType
        if isinstance(bot, OneBotV11BotType):
            return "onebot_v11"

    return "unknown"


def get_user_id(bot: BaseBot, event: Event) -> str:
    """统一获取用户ID"""
    bot_type = get_bot_type(bot)

    if bot_type == "qq_official" and _qq_available:
        if TYPE_CHECKING:
            from nonebot.adapters.qq import MessageEvent as QQMessageEventType
        else:
            from nonebot.adapters.qq import MessageEvent as QQMessageEventType
        if isinstance(event, QQMessageEventType):
            return event.get_user_id()
    elif bot_type == "onebot_v11" and _onebot_v11_available:
        if TYPE_CHECKING:
            from nonebot.adapters.onebot.v11 import (
                MessageEvent as OneBotV11MessageEventType,
            )
        else:
            from nonebot.adapters.onebot.v11 import (
                MessageEvent as OneBotV11MessageEventType,
            )
        if isinstance(event, OneBotV11MessageEventType):
            return str(event.get_user_id())

    # 通用回退
    return event.get_user_id()


def get_plain_text(bot: BaseBot, event: Event) -> str:
    """统一获取纯文本内容"""
    bot_type = get_bot_type(bot)

    if bot_type == "qq_official" and _qq_available:
        if TYPE_CHECKING:
            from nonebot.adapters.qq import MessageEvent as QQMessageEventType
        else:
            from nonebot.adapters.qq import MessageEvent as QQMessageEventType
        if isinstance(event, QQMessageEventType):
            return str(event.get_plaintext())
    elif bot_type == "onebot_v11" and _onebot_v11_available:
        if TYPE_CHECKING:
            from nonebot.adapters.onebot.v11 import (
                MessageEvent as OneBotV11MessageEventType,
            )
        else:
            from nonebot.adapters.onebot.v11 import (
                MessageEvent as OneBotV11MessageEventType,
            )
        if isinstance(event, OneBotV11MessageEventType):
            return str(event.get_plaintext())

    # 通用回退
    return str(event.get_plaintext())


def is_mentioned(bot: BaseBot, event: Event) -> bool:
    """检查是否@了机器人 或 提到了机器人昵称"""
    bot_type = get_bot_type(bot)
    bot_id = bot.self_id
    message_text = get_plain_text(bot, event)

    # 方法1: 检查是否被@
    if bot_type == "qq_official" and _qq_available:
        if TYPE_CHECKING:
            from nonebot.adapters.qq import MessageEvent as QQMessageEventType
        else:
            from nonebot.adapters.qq import MessageEvent as QQMessageEventType
        if isinstance(event, QQMessageEventType):
            for seg in event.get_message():
                if seg.type == "mention" and seg.data.get("user_id") == bot_id:
                    logger.debug("Triggered by @mention (QQ official)")
                    return True

    elif bot_type == "onebot_v11" and _onebot_v11_available:
        if TYPE_CHECKING:
            from nonebot.adapters.onebot.v11 import (
                MessageEvent as OneBotV11MessageEventType,
            )
        else:
            from nonebot.adapters.onebot.v11 import (
                MessageEvent as OneBotV11MessageEventType,
            )
        if isinstance(event, OneBotV11MessageEventType):
            for seg in event.get_message():
                if seg.type == "at" and seg.data.get("qq") == bot_id:
                    logger.debug("Triggered by @mention (OneBot V11)")
                    return True

    # 检查纯文本是否包含@的CQ码（兼容某些情况）
    mention_pattern = f"[CQ:at,qq={bot_id}]"
    if mention_pattern in message_text:
        logger.debug("Triggered by @mention CQ code")
        return True

    # 方法2: 检查是否提到了机器人昵称
    for nickname in nicknames:
        if nickname in message_text:
            logger.debug(f"Triggered by nickname: {nickname}")
            return True

    # 方法3: 私聊情况下自动响应
    if bot_type == "onebot_v11" and _onebot_v11_available:
        if TYPE_CHECKING:
            from nonebot.adapters.onebot.v11 import (
                MessageEvent as OneBotV11MessageEventType,
            )
        else:
            from nonebot.adapters.onebot.v11 import (
                MessageEvent as OneBotV11MessageEventType,
            )
        if isinstance(event, OneBotV11MessageEventType):
            # 此时 event 类型已收窄，可以安全访问 message_type
            if hasattr(event, "message_type") and event.message_type == "private":
                logger.debug("Triggered by private message (OneBot V11)")
                return True

    # 如果都没有触发，则不响应
    return False


def extract_actual_message(bot: BaseBot, event: Event) -> str:
    """提取去除@和昵称后的实际消息内容"""
    message_text = get_plain_text(bot, event)
    bot_type = get_bot_type(bot)
    bot_id = bot.self_id

    # 去除@部分
    if bot_type == "onebot_v11" and _onebot_v11_available:
        if TYPE_CHECKING:
            from nonebot.adapters.onebot.v11 import (
                MessageEvent as OneBotV11MessageEventType,
            )
        else:
            from nonebot.adapters.onebot.v11 import (
                MessageEvent as OneBotV11MessageEventType,
            )
        if isinstance(event, OneBotV11MessageEventType):
            # 构建不包含@的新消息
            new_message_parts: list[str] = []
            for seg in event.get_message():
                if not (seg.type == "at" and seg.data.get("qq") == bot_id):
                    if seg.type == "text":
                        new_message_parts.append(str(seg))
            if new_message_parts:
                message_text = "".join(new_message_parts)

    # 去除昵称部分（简单去除第一个匹配的昵称）
    for nickname in nicknames:
        if nickname in message_text:
            message_text = message_text.replace(nickname, "", 1).strip()
            break

    # 如果去除后消息为空，返回原消息
    if not message_text.strip():
        return get_plain_text(bot, event)

    return message_text.strip()


async def send_thinking_indicator(
    bot: BaseBot, event: Event
) -> Mapping[str, object] | None:
    """发送"正在输入"提示（仅OneBot V11支持）"""
    bot_type = get_bot_type(bot)

    try:
        if bot_type == "onebot_v11" and _onebot_v11_available:
            # 通过 isinstance 收窄类型后，类型检查器能正确推断
            if TYPE_CHECKING:
                from nonebot.adapters.onebot.v11 import Bot as OneBotV11BotType
                from nonebot.adapters.onebot.v11 import (
                    MessageEvent as OneBotV11MessageEventType,
                )
            else:
                from nonebot.adapters.onebot.v11 import Bot as OneBotV11BotType
                from nonebot.adapters.onebot.v11 import (
                    MessageEvent as OneBotV11MessageEventType,
                )

                if isinstance(bot, OneBotV11BotType) and isinstance(
                    event, OneBotV11MessageEventType
                ):
                    # 此时类型检查器知道 event 是 OneBotV11MessageEventType
                    if event.group_id:  # 直接访问，类型已收窄
                        result = await bot.send_group_msg(
                            group_id=event.group_id, message="..."
                        )
                        return {"message_id": result["message_id"]}
                if hasattr(event, "group_id") and event.group_id:
                    result = await bot.send_group_msg(
                        group_id=event.group_id, message="🤔 诺喵莉正在思考中..."
                    )
                    return {"message_id": result["message_id"]}
                elif hasattr(event, "user_id") and event.user_id:
                    result = await bot.send_private_msg(
                        user_id=event.user_id, message="🤔 诺喵莉正在思考中..."
                    )
                    return {"message_id": result["message_id"]}
    except Exception as e:
        logger.debug(f"Failed to send thinking indicator: {e}")

    return None


async def delete_message(bot: BaseBot, message_id: str | int) -> bool:
    """统一删除消息"""
    bot_type = get_bot_type(bot)
    try:
        if bot_type == "onebot_v11" and _onebot_v11_available:
            if TYPE_CHECKING:
                from nonebot.adapters.onebot.v11 import Bot as OneBotV11BotType
            else:
                from nonebot.adapters.onebot.v11 import Bot as OneBotV11BotType

            if isinstance(bot, OneBotV11BotType):
                # 确保 message_id 是 int
                if isinstance(message_id, str):
                    if message_id.isdigit():
                        msg_id = int(message_id)
                    else:
                        logger.warning(
                            f"Invalid message_id format for delete: {message_id}"
                        )
                        return False
                else:
                    msg_id = message_id
                await bot.delete_msg(message_id=msg_id)
                return True
        # TODO: 处理 QQ 官方适配器的删除消息（如果支持）
    except Exception as e:
        logger.debug(f"Failed to delete message: {e}")
    return False


@chat.handle()
async def handle_chat(
    bot: BaseBot,
    event: Event,
    matcher: Matcher,
) -> None:
    """处理聊天消息（兼容QQ官方和OneBot V11）"""

    # 检测机器人类型
    bot_type = get_bot_type(bot)
    if bot_type == "unknown":
        logger.debug(f"Skipped: unknown bot type {type(bot)}")
        return

    logger.debug(f"Processing message from {bot_type} bot")

    # 跳过机器人自己的消息
    if event.get_user_id() == bot.self_id:
        logger.info(f"Skipped: bot's own message from {event.get_user_id()}")
        return

    # 统一获取用户ID和消息文本
    user_id = get_user_id(bot, event)
    message_text = get_plain_text(bot, event)

    # 检查是否是@机器人 或 提到昵称的消息
    if not is_mentioned(bot, event):
        logger.debug(f"Skipped: not mentioned or nickname called by user {user_id}")
        return

    # 提取实际要处理的消息（去除@和昵称）
    actual_message = extract_actual_message(bot, event)
    logger.info(
        f"Processing message from {user_id}: '{actual_message}' (original: '{message_text}')"
    )

    # 如果实际消息为空，可能只是@了机器人，可以回复一个友好的提示
    if not actual_message:
        actual_message = "你好呀"
        logger.debug(
            f"Empty message after extraction, using default: '{actual_message}'"
        )

    # 检查插件配置是否加载成功
    if not plugin_config or not chat_processor:
        logger.info("Skipped: plugin not initialized")
        return

    # 检查是否有API密钥
    if not plugin_config.api_key:
        logger.info("Skipped: no API key")
        return

    # 发送正在输入的提示（仅OneBot V11支持）
    thinking_msg = None
    try:
        # 发送思考提示
        thinking_msg = await send_thinking_indicator(bot, event)

        # 使用异步处理器处理消息
        start_time = time.time()
        # ===== 关键修改：必须确保 ChatProcessor.process_message 接受 BaseBot 和 Event =====
        response = await chat_processor.process_message(
            actual_message, user_id, bot, event
        )
        end_time = time.time()

        # 记录响应时间
        response_time = end_time - start_time
        logger.info(f"Chat processed in {response_time:.2f}s for user {user_id}")

        # 移除"正在输入中"的消息
        if thinking_msg and "message_id" in thinking_msg:
            # 从 thinking_msg 字典中取出 message_id，类型检查器会推断为 object，需要断言或cast
            msg_id_obj = thinking_msg.get("message_id")
            if msg_id_obj is not None:
                # 假设它是 str 或 int，传递给 delete_message
                # 使用断言帮助类型检查器
                if isinstance(msg_id_obj, (str, int)):
                    _ = await delete_message(bot, msg_id_obj)
                else:
                    logger.warning(
                        f"Unexpected type for message_id: {type(msg_id_obj)}"
                    )

        # 发送回复
        if response and response.strip():
            await matcher.finish(response)  # pyright: ignore[reportUnknownMemberType]

    except FinishedException:
        # 正常结束，重新抛出让 NoneBot 处理
        raise
    except Exception as e:
        logger.error(f"Chat plugin error: {e}")
        # 尝试发送错误提示
        try:
            error_msg = "喵…诺喵莉刚才走神了，能再说一遍吗？(>_<)"
            await matcher.finish(error_msg)  # pyright: ignore[reportUnknownMemberType]
        except Exception:
            pass


# 导出配置信息供bot.py使用
__all__: list[str] = []
