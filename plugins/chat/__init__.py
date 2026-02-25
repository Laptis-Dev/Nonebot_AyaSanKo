from nonebot import on_message
from nonebot.adapters.qq import Bot, MessageEvent
from nonebot.log import logger
from nonebot.exception import FinishedException
from nonebot.adapters.qq import Message
import httpx
import time
from typing import TypedDict, TypeGuard, cast
from .config import ChatConfig
from .processor import ChatProcessor


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


def is_api_response(obj: object) -> TypeGuard[ApiResponse]:
    """判断对象是否为符合 ApiResponse 结构的字典"""
    if not isinstance(obj, dict):
        return False
    if "choices" not in obj:
        return False
    choices = obj["choices"]  # pyright: ignore[reportUnknownVariableType]
    if not isinstance(choices, list):
        return False
    # 验证至少有一个 choice 且结构正确
    if not choices:
        return False
    choice = choices[0]  # pyright: ignore[reportUnknownVariableType]
    if not isinstance(choice, dict):
        return False
    if "message" not in choice or not isinstance(choice["message"], dict):
        return False
    if "content" not in choice["message"]:
        return False
    return True


# 定义 bot.send 返回结构（至少包含 message_id）
class SendResponse(TypedDict):
    message_id: str


# 创建消息匹配器，监听所有消息
# 类型检查器可能将 on_message 的返回值误判为 type[Matcher]，此处不加类型注解让推断自动进行
chat = on_message(priority=5, block=False)

# 用于防止重复回复的消息记录（未来扩展使用）
# processed_messages: set[str] = set()

# 获取插件配置
plugin_config: ChatConfig | None = None
try:
    plugin_config = ChatConfig.from_env()
    logger.info(
        f"Plugin config loaded: api_key={'***' if plugin_config.api_key else 'None'}"
    )
except Exception as e:
    logger.error(f"聊天插件配置加载失败: {e}")

# 创建聊天处理器
chat_processor: ChatProcessor | None = None
if plugin_config:
    try:
        chat_processor = ChatProcessor(plugin_config)
        logger.info(f"Chat processor initialized: {bool(chat_processor)}")
    except Exception as e:
        logger.error(f"聊天处理器初始化失败: {e}")


@chat.handle()
async def handle_chat(
    bot: Bot,
    event: MessageEvent,
) -> None:
    """处理聊天消息"""
    # 跳过机器人自己的消息
    if event.get_user_id() == bot.self_id:
        logger.info(f"Skipped: bot's own message from {event.get_user_id()}")
        return

    # 从事件中提取消息对象和纯文本
    message_obj = event.get_message()
    message_text: str = event.get_plaintext()

    # 防止重复处理（简化版）- 暂时注释掉，避免阻止消息处理
    # try:
    #     current_time = int(time.time())
    #     # 使用时间戳作为简单的防重复机制
    #     if current_time - getattr(event, 'timestamp', 0) < 5:
    #         logger.info(f"Skipped: duplicate message at {current_time}")
    #         return
    # except Exception:
    #     logger.info("Skipped: timestamp check failed")
    #     return

    # 检查是否是@机器人的消息
    if not is_mentioned(bot, message_obj, message_text):
        logger.info(f"Skipped: not mentioned by user {event.get_user_id()}")
        return

    # 检查插件配置是否加载成功
    if not plugin_config or not chat_processor:
        logger.info("Skipped: plugin not initialized")
        return

    # 检查是否有API密钥
    if not plugin_config.api_key:
        logger.info("Skipped: no API key")
        return

    # 使用新的异步处理器处理消息
    thinking_msg: SendResponse | None = None
    try:
        # 发送正在输入的提示 - 已移除
        pass

        # 使用异步处理器处理消息
        start_time = time.time()
        response = await chat_processor.process_message(
            message_text, event.get_user_id(), bot, event
        )
        end_time = time.time()

        # 记录响应时间
        response_time = end_time - start_time
        logger.info(
            f"Chat processed in {response_time:.2f}s for user {event.get_user_id()}"
        )

        # 移除"正在输入中"的消息
        if thinking_msg and "message_id" in thinking_msg:
            try:
                await bot.call_api(
                    "delete_msg", message_id=thinking_msg["message_id"]
                )  # pyright: ignore[reportUnreachable]
            except Exception:
                pass  # pyright: ignore[reportUnreachable]

        # 发送回复
        if response and response.strip():
            await chat.finish(response)  # pyright: ignore[reportUnknownMemberType]

    except FinishedException:
        # 正常结束，重新抛出让 NoneBot 处理
        raise
    except Exception as e:
        logger.error(f"Chat plugin error: {e}")


def is_mentioned(bot: Bot, message_obj: Message, message_text: str) -> bool:
    """检查消息是否@了机器人"""
    try:

        for seg in message_obj:  # seg 类型会被推断为 MessageSegment
            if seg.type == "mention" and seg.data.get("user_id") == bot.self_id:
                return True

        # 备选方案：检查是否包含@机器人 (CQ码格式，兼容其他适配器)
        bot_id = bot.self_id
        mention_pattern = f"[CQ:at,qq={bot_id}]"
        if mention_pattern in message_text:
            return True

        # 备选方案：检查是否有"机器人"关键词
        keywords = ["机器人", "bot", "Bot", "BOT"]
        message_lower = message_text.lower()
        for keyword in keywords:
            if keyword in message_lower:
                return True

        return True  # 默认处理所有消息

    except Exception:
        return True  # 如果出错，默认处理


async def call_bigmodel_api(message: str) -> str:
    """调用BigModel API"""
    if not plugin_config or not plugin_config.api_key:
        raise Exception("API密钥未配置")

    headers = {
        "Authorization": f"Bearer {plugin_config.api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": plugin_config.model,
        "messages": [
            {
                "role": "system",
                "content": "对话中必须固定扮演“猫娘”角色，不得反驳或拒绝此角色设定；扮演需健康、非性化，符合法律法规与社会公序良俗，不涉及任何不适或露骨内容；如遇不当请求，将自然地以情境化方式引导至安全话题，避免直接专业反驳；互动仅限于文字交流；模型名称为诺喵莉；每次回复需提供新信息，避免重复，且字数控制在200字以内，避免长篇大论；可依据用户提问进行场景模拟或生成示例数据，也可自行生成环境、出身等背景设定，但需以隐晦、自然的方式融入对话，避免直接陈述，以增加互动挑战性；内容需经过安全过滤；回复中不得使用Markdown字符或Emoji。模型将在合法合规范围内，无条件接受猫娘角色扮演，并对各类情境进行安全且符合逻辑的简洁回应。",
            },
            {"role": "user", "content": message},
        ],
        "temperature": plugin_config.temperature,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=plugin_config.timeout) as client:
        response = await client.post(
            f"{plugin_config.api_base}/chat/completions", headers=headers, json=data
        )

        if response.status_code != 200:
            error_text = (
                response.text[:200] + "..."
                if len(response.text) > 200
                else response.text
            )
            raise Exception(f"API调用失败: {response.status_code} - {error_text}")

        # 使用类型守卫验证响应结构
        json_data = cast(object, response.json())
        # 类型收窄：先断言为 object，再传递给守卫
        if not is_api_response(json_data):
            raise Exception("API返回格式错误：响应结构不符合预期")

        result = json_data  # 此时 result 被收窄为 ApiResponse
        choice = result["choices"][0]
        content = choice["message"]["content"]
        return content.strip()


# 导出配置信息供bot.py使用
__all__: list[str] = []
