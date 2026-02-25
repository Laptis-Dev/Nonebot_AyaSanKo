from nonebot import on_command
from nonebot.adapters.qq import Bot, MessageEvent
import datetime
import sys
from typing import List, Dict

status = on_command("status", priority=10, block=True)

@status.handle()
async def handle_status(bot: Bot, event: MessageEvent):
    """处理状态查询命令"""
    from nonebot import get_driver, get_bots, get_loaded_plugins
    
    # 获取驱动器信息
    driver = get_driver()
    config = driver.config
    
    # 获取机器人连接状态
    bots = get_bots()
    bot_status: List[Dict[str, str]] = []
    
    for bot_id, bot_instance in bots.items():
        bot_info = {
            "bot_id": bot_id,
            "type": type(bot_instance).__name__,
            "is_connected": "True"  # 如果bot实例存在且能响应，说明已连接
        }
        bot_status.append(bot_info)
    
    # 获取插件信息
    plugins = get_loaded_plugins()
    plugin_list: List[str] = []
    for plugin in plugins:
        if hasattr(plugin, 'name') and plugin.name:
            plugin_list.append(plugin.name)
    
    # 构建状态消息
    status_msg = f"🤖 机器人运行状态报告\n"
    status_msg += f"{'='*20}\n"
    status_msg += f"📅 查询时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # 系统配置 - 从pyproject.toml获取信息
    status_msg += f"⚙️ 系统配置:\n"
    status_msg += f"   - 项目名称: {getattr(config, 'project_name', getattr(config, 'name', 'Nonebot_AyaSanKo'))}\n"
    status_msg += f"   - 项目版本: {getattr(config, 'version', '0.1.0')}\n"
    status_msg += f"   - Python版本: {sys.version.split()[0]}\n\n"
    
    # 机器人状态
    status_msg += f"🔌 机器人连接状态:\n"
    for i, bot_info in enumerate(bot_status, 1):
        status_str = "✅ 已连接" if bot_info["is_connected"] else "❌ 未连接"
        status_msg += f"   - 机器人{i} ({bot_info['bot_id']}): {status_str}\n"
    
    # 插件状态
    status_msg += f"\n📦 已加载插件 ({len(plugin_list)}个):\n"
    if plugin_list:
        for i, plugin_name in enumerate(plugin_list, 1):
            status_msg += f"   {i}. {plugin_name}\n"
    else:
        status_msg += "   暂无加载的插件\n"
    
    # 适配器状态
    status_msg += f"\n🔌 已注册适配器:\n"
    from nonebot import get_adapters
    adapters = get_adapters()
    for i, adapter in enumerate(adapters, 1):
        adapter_name = getattr(adapter, 'name', str(adapter))
        status_msg += f"   {i}. {adapter_name}\n"
    
    # 使用最新的API发送消息
    await bot.send(event, status_msg)