# fmt: off
from nonebot import get_driver, on_command, require
from nonebot.adapters import Event
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.message import event_preprocessor
from nonebot.permission import SUPERUSER
from nonebot.adapters import Bot as BaseBot
from types import ModuleType
from .config import get_config, reload_config

driver = get_driver()


@driver.on_startup
async def on_startup() -> None:
    logger.info("管理器插件已启动")


@event_preprocessor
async def global_preprocessor(event: Event) -> None:
    """在所有事件处理之前执行，过滤不符合条件的消息"""
    try:
        text = event.get_plaintext()
    except ValueError:
        return

    stripped = text.strip()
    cfg = get_config()

    # 命令直接放行，不走过滤逻辑
    if stripped in cfg.commands:
        logger.debug(f"检测到命令 {stripped}，放行")
        return

    if not cfg.global_switch:
        logger.debug("全局开关关闭，忽略所有消息")
        raise IgnoredException("全局关闭")

    for keyword in cfg.ban_keywords:
        if keyword in text:
            logger.debug(f"消息包含违禁词 '{keyword}'，忽略")
            raise IgnoredException("违禁词过滤")

    user_id = event.get_user_id()
    if user_id.isdigit() and int(user_id) in cfg.user_blacklist:
        logger.debug(f"用户 {user_id} 在黑名单中，忽略")
        raise IgnoredException("用户黑名单")

    group_id: object = getattr(event, "group_id", None)
    if group_id is not None and isinstance(group_id, int):
        if cfg.group_whitelist and group_id not in cfg.group_whitelist:
            logger.debug(f"群 {group_id} 不在白名单中，忽略")
            raise IgnoredException("群不在白名单")

clear_cmd = on_command("/clear", permission=SUPERUSER, priority=10, block=True)

@clear_cmd.handle()
async def handle_clear(bot: BaseBot, event: Event) -> None:
    superusers = driver.config.superusers
    if event.get_user_id() not in superusers:
        await bot.send(event, "权限不足")  # pyright: ignore[reportUnknownMemberType]
        return

    try:
        chat_mod: ModuleType = require("chat_plugin")  # type: ignore[assignment]
        clear_fn = getattr(chat_mod, "clear_context", None)
        if callable(clear_fn):
            plain = event.get_plaintext().strip()
            arg = plain.removeprefix("/clear").strip()
            count: object = clear_fn(arg) if arg else clear_fn()  # type: ignore[no-any-return]
            await bot.send(event, f"已清除 {count} 位用户的上下文")  # pyright: ignore[reportUnknownMemberType]
        else:
            await bot.send(event, "chat_plugin 不支持清除上下文")  # pyright: ignore[reportUnknownMemberType]
    except Exception as e:
        await bot.send(event, f"清除失败: {e}")  # pyright: ignore[reportUnknownMemberType]


def check_permission(event: Event) -> bool:
    """供其他插件调用的权限查询接口"""
    cfg = get_config()
    if not cfg.global_switch:
        return False
    try:
        text = event.get_plaintext()
    except ValueError:
        return True  # 非文本事件不做关键词过滤
    for keyword in cfg.ban_keywords:
        if keyword in text:
            return False
    user_id = event.get_user_id()
    if user_id.isdigit() and int(user_id) in cfg.user_blacklist:
        return False
    group_id: object = getattr(event, "group_id", None)
    if group_id is not None and isinstance(group_id, int):
        if cfg.group_whitelist and group_id not in cfg.group_whitelist:
            return False
    return True

# ---------- reload 命令 ----------
reload_cmd = on_command("/reload", permission=SUPERUSER, priority=4, block=True)


@reload_cmd.handle()
async def reload_handle() -> None:
    # finish() 放在 try 块外，避免 FinishedException 被误捕获
    try:
        new_config = reload_config()
        logger.info(f"配置重新加载成功，白名单: {new_config.group_whitelist}")
        msg = "配置重新加载成功！"
    except Exception as e:
        logger.error(f"配置重新加载失败: {e}")
        msg = f"配置重新加载失败: {e}"
    await reload_cmd.finish(msg)  # pyright: ignore[reportUnknownMemberType]


__all__ = ["check_permission"]
# fmt: on
