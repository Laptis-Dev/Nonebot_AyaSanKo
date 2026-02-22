# Nonebot_AyaSanKo OpenSource

基于 NoneBot 2 框架开发的 QQ 机器人项目，提供插件化架构和丰富的功能扩展。

## 🚀 快速开始

### 环境要求

- Python 3.10+
- QQ 开发者账号（在 QQ 开放平台获取）

### 启动步骤

1. **补全 Python 依赖项**

   ```bash
   pip install -e .
   ```

   或安装开发环境依赖（包含代码检查工具）：

   ```bash
   pip install -e ".[dev]"
   ```

2. **配置环境变量**
   创建 `.env` 文件并填入以下配置：

   ```ini
   # 环境配置
   ENVIRONMENT=dev
   DRIVER=~fastapi+~httpx+~websockets+~aiohttp
   HOST=127.0.0.1
   PORT=8081

   # QQ官方机器人适配器配置
   # 在QQ开放平台获取以下信息: https://q.qq.com/#/app/bot
   QQ_BOT_APPID=你的应用ID
   QQ_BOT_TOKEN=你的访问令牌
   QQ_BOT_SECRET=你的客户端密钥

   # QQ机器人连接配置
   QQ_BOT_HTTP_API_URL=https://api.sgroup.qq.com
   QQ_BOT_WS_URL=wss://sbot.qq.com/ws
   use_websocket=true
   ```

   **获取 QQ 机器人配置：**
   1. 访问 [QQ 开放平台](https://q.qq.com/#/app/bot)
   2. 创建机器人应用
   3. 获取 `APPID`、`TOKEN`、`SECRET`
   4. 填入上述 `.env` 文件对应位置

3. **启动机器人**
   ```bash
   nb run --reload
   ```

## 📦 项目结构

```
* /                      # 项目根目录
├── *                    # 主要文件和目录
│   ├── plugins/         # 插件开发目录
│   ├── package.json     # 前端依赖配置
│   ├── pyproject.toml   # 项目配置
│   ├── LICENSE          # 许可证文件
│   └── README.md        # 项目说明
└── .*                    # 隐藏文件和目录
    ├── .env              # 环境配置
    ├── .github/          # GitHub 工作流
    ├── .venv/           # Python 虚拟环境
    └── .vscode/         # VS Code 配置
```

## 🔧 配置说明

### 环境变量配置 (.env)

```ini
ENVIRONMENT=dev
DRIVER=~fastapi+~httpx+~websockets+~aiohttp
HOST=127.0.0.1
PORT=8081

# QQ 机器人配置
QQ_BOT_APPID=你的应用ID
QQ_BOT_TOKEN=你的访问令牌
QQ_BOT_SECRET=你的客户端密钥
QQ_BOT_HTTP_API_URL=https://api.sgroup.qq.com
QQ_BOT_WS_URL=wss://sbot.qq.com/ws
use_websocket=true
```

### QQ 机器人获取配置

1. 访问 [QQ 开放平台](https://q.qq.com/#/app/bot)
2. 创建机器人应用
3. 获取 `APPID`、`TOKEN`、`SECRET`
4. 配置服务器地址和回调

## 🛠️ 可用驱动

项目支持多种驱动方式：

- **FastAPI** - 高性能 Web 框架
- **HTTPX** - 异步 HTTP 客户端
- **WebSockets** - WebSocket 协议支持
- **AioHTTP** - 异步 HTTP 服务器/客户端

## 📚 插件开发

### 基本插件结构

```python
from nonebot import on_command
from nonebot.adapters.qq import Bot, Message
from nonebot.matcher import Matcher

@on_command("命令名")
async def handle_command(bot: Bot, matcher: Matcher):
    await matcher.send("回复消息")
```

### 插件元数据

```python
__plugin_meta__ = PluginMetadata(
    name="插件名称",
    description="插件描述",
    usage="使用方法",
    type="application"
)
```

## 🔌 当前插件

### 运行状态监控 (`status_monitor.py`)

**命令列表：**

- `/status` - 获取完整状态信息
- `/status simple` - 获取简化状态信息
- `/status interval [秒数]` - 设置定时状态刷新（5-300秒）

**功能特性：**

- CPU、内存、磁盘使用率监控
- 系统运行时间统计
- 机器人进程状态
- 网络连接信息
- 详细系统参数展示

## 🛠️ 开发工具

### 代码检查

```bash
# Ruff 代码检查和格式化
ruff check .
ruff format .

# 类型检查
mypy .
pyright .
```

### 调试模式

使用 `--reload` 参数启用热重载：

```bash
nb run --reload
```

## 📄 许可证

[查看 LICENSE 文件](LICENSE)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 支持

- [NoneBot 文档](https://nonebot.dev/)
- [QQ 开放平台文档](https://q.qq.com/wiki/)
- [Issues 提交](https://github.com/your-repo/issues)

---

**注意：** 请妥善保管 `.env` 文件中的敏感信息，不要将其提交到版本控制系统。
