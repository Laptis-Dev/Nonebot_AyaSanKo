import asyncio
import platform
from datetime import datetime, timezone

import psutil

# 常量定义
MIN_INTERVAL_SECONDS = 5
MAX_INTERVAL_SECONDS = 300
from nonebot import on_command
from nonebot.adapters.qq import Bot, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="运行状态监控",
    description="监控机器人运行状态，包括CPU、内存、在线时间等信息",
    usage="/status",
    type="application",
)

status_matcher = on_command(
    "status",
    aliases={"运行状态", "系统状态"},
    priority=10,
    block=True
)


@status_matcher.handle()
async def handle_status(
    _bot: Bot,
    matcher: Matcher,
    _args: Message = CommandArg()
) -> None:
    """处理状态查询命令"""
    try:
        # 获取系统信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # 获取启动时间
        start_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
        uptime = datetime.now(timezone.utc) - start_time

        # 获取进程信息
        process = psutil.Process()
        process_cpu = process.cpu_percent()
        process_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 构建状态消息
        status_msg = f"""
🤖 机器人运行状态报告 🤖

💻 系统信息：
├─ 操作系统: {platform.system()} {platform.release()}
├─ CPU使用率: {cpu_percent}%
├─ 内存使用率: {memory.percent}%
│  ├─ 总内存: {memory.total / 1024 / 1024 / 1024:.2f} GB
│  ├─ 已使用: {memory.used / 1024 / 1024 / 1024:.2f} GB
│  └─ 可用内存: {memory.available / 1024 / 1024 / 1024:.2f} GB
├─ 磁盘使用率: {disk.percent}%
│  ├─ 总空间: {disk.total / 1024 / 1024 / 1024:.2f} GB
│  └─ 可用空间: {disk.free / 1024 / 1024 / 1024:.2f} GB
└─ 系统运行时间: {uptime.days}天 {uptime.seconds // 3600}小时 {
    (uptime.seconds % 3600) // 60
}分钟

🤖 机器人进程状态：
├─ CPU使用率: {process_cpu}%
├─ 内存占用: {process_memory:.2f} MB
├─ Python版本: {platform.python_version()}
└─ 运行状态: ✅ 在线

⚡ 性能指标：
├─ CPU核心数: {psutil.cpu_count()}
├─ 负载平均值: {psutil.getloadavg()[0]:.2f} (1分钟)
├─ 交换内存使用: {psutil.swap_memory().percent}%
└─ 网络连接数: {len(psutil.net_connections())}
"""

        # 发送状态消息
        await matcher.send(status_msg)

    except Exception as e:
        error_msg = f"获取状态信息时出错: {e!s}"
        await matcher.send(error_msg)


@status_matcher.handle()
async def handle_status_detail(
    _bot: Bot,
    matcher: Matcher,
    _args: Message = CommandArg()
) -> None:
    """处理详细状态查询命令"""
    try:
        # 获取详细系统信息
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)

        # 获取网络信息
        net_io = psutil.net_io_counters()
        disk_io = psutil.disk_io_counters()

        # 获取进程详细信息
        process = psutil.Process()
        process_info = process.memory_info()
        process_threads = process.num_threads()
        process_open_files = len(process.open_files())

        # 计算运行时间
        start_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
        uptime = datetime.now(timezone.utc) - start_time

        detailed_status = f"""
🔍 详细运行状态报告 🔍

🖥️ 系统详细信息：
├─ 操作系统: {platform.system()} {platform.release()} ({platform.version()})
├─ 处理器信息:
│  ├─ 物理核心: {cpu_count}
│  ├─ 逻辑核心: {cpu_count_logical}
│  ├─ 当前频率: {cpu_freq.current:.2f} MHz
│  └─ CPU使用率: {psutil.cpu_percent(interval=1)}%
├─ 内存信息:
│  ├─ 总内存: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.2f} GB
│  ├─ 已使用: {psutil.virtual_memory().used / 1024 / 1024 / 1024:.2f} GB
│  ├─ 可用内存: {psutil.virtual_memory().available / 1024 / 1024 / 1024:.2f} GB
│  └─ 缓存: {psutil.virtual_memory().cached / 1024 / 1024 / 1024:.2f} GB
├─ 磁盘信息:
│  ├─ 总空间: {psutil.disk_usage('/').total / 1024 / 1024 / 1024:.2f} GB
│  ├─ 已使用: {psutil.disk_usage('/').used / 1024 / 1024 / 1024:.2f} GB
│  └─ 可用空间: {psutil.disk_usage('/').free / 1024 / 1024 / 1024:.2f} GB
└─ 系统运行时间: {uptime.days}天 {uptime.seconds // 3600}小时 {
    (uptime.seconds % 3600) // 60
}分钟

📊 进程详细信息：
├─ 内存使用:
│  ├─ RSS: {process_info.rss / 1024 / 1024:.2f} MB
│  ├─ VMS: {process_info.vms / 1024 / 1024:.2f} MB
│  └─ 共享内存: {process_info.shared / 1024 / 1024:.2f} MB
├─ 线程信息:
│  ├─ 线程数: {process_threads}
│  └─ 打开文件数: {process_open_files}
├─ CPU信息:
│  ├─ CPU使用率: {process.cpu_percent()}%
│  └─ 子进程数: {len(process.children())}
└─ 工作目录: {process.cwd()}

🌐 网络信息：
├─ 网络IO:
│  ├─ 发送字节: {net_io.bytes_sent / 1024 / 1024:.2f} MB
│  └─ 接收字节: {net_io.bytes_recv / 1024 / 1024:.2f} MB
└─ 磁盘IO:
   ├─ 读取次数: {disk_io.read_count if disk_io else 'N/A'}
   └─ 写入次数: {disk_io.write_count if disk_io else 'N/A'}

🎯 系统负载:
├─ 1分钟平均负载: {psutil.getloadavg()[0]:.2f}
├─ 5分钟平均负载: {psutil.getloadavg()[1]:.2f}
├─ 15分钟平均负载: {psutil.getloadavg()[2]:.2f}
└─ 交换内存使用率: {psutil.swap_memory().percent}%
"""

        await matcher.send(detailed_status)

    except Exception as e:
        error_msg = f"获取详细状态信息时出错: {e!s}"
        await matcher.send(error_msg)


# 注册带参数的命令
status_simple = on_command(
    "status simple",
    aliases={"简单状态"},
    priority=10,
    block=True
)


@status_simple.handle()
async def handle_simple_status(
    _bot: Bot,
    matcher: Matcher,
    _args: Message = CommandArg()
) -> None:
    """处理简化状态查询命令"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        simple_status = f"""
📊 快速状态:
🖥️ CPU: {cpu_percent}% | 💾 内存: {memory.percent}% | 🔄 状态: ✅在线
"""

        await matcher.send(simple_status)

    except Exception as e:
        await matcher.send(f"获取状态失败: {e!s}")


# 注册更新间隔命令
status_interval = on_command(
    "status interval",
    aliases={"状态刷新"},
    priority=10,
    block=True
)


@status_interval.handle()
async def handle_status_interval(
    _bot: Bot,
    matcher: Matcher,
    _args: Message = CommandArg()
) -> None:
    """处理定时状态查询"""
    try:
        text = _args.extract_plain_text()
        interval = int(text.strip()) if text else 30

        if interval < MIN_INTERVAL_SECONDS or interval > MAX_INTERVAL_SECONDS:
            await matcher.send("刷新间隔必须在5-300秒之间")
            return

        await matcher.send(f"开始每{interval}秒自动刷新状态...")

        while True:
            await asyncio.sleep(interval)

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            current_time = datetime.now(timezone.utc).strftime("%H:%M:%S")
            status_update = f"🔄 实时状态更新 - CPU: {cpu_percent}% | 内存: {memory}%"
            status_msg = f"{status_update} | 时间: {current_time}"
            await matcher.send(status_msg)

    except Exception as e:
        await matcher.send(f"定时刷新状态时出错: {e!s}")
