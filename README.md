# Nonebot_AyaSanKo

---

一个基于 NoneBot2 框架的QQ机器人项目
_构建此项目的系统因为是Windows，可能对Linux的兼容性稍许影响._

---

## 正在开发的插件

- `status_plugin` 查询机器人状态的插件，可用`/status`指令查询
- `chat_plugin` 集成了人工智能的辅助聊天插件，无需指令响应
- `manager_plugin` 全局管理插件指令、过滤关键词、重新获取`.env`的新内容`/reload`、清理上下文`/clear`
- (还有更多，尚未推出...)

---

## 如何运行AyaSanKo机器人？

### 1. 环境准备

```bash
# 确保Python 3.10+(因为大部分插件代码基于PythonAPI3.10)
python --version

# 安装pipx (pip的替代物,速度慢可以去换PyPI源)
python -m pip install --user pipx

# 添加到系统的 PATH 环境变量中
python -m pipx ensurepath

# 安装NoneBot2 (pipx的源就是pip的PyPI源)
pipx install nb-cli
```

### 2. 下载本项目到你的电脑

```bash
git clone https://github.com/Laptis-Dev/Nonebot_AyaSanKo.git
```

### 3. 配置机器人

```bash
# 进入刚Clone好的项目文件夹
cd Nonebot_AyaSanKo
# 创建 `.env` 文件并添加以下配置：
# Linux
vi .env
# Windows
notepad .env
```

将下面的模板复制粘贴到`.env`文件中

```env
# Nonebot基础配置
# 驱动器是机器人运行的基石，如要正常运行请不要修改它↓
DRIVER=~fastapi+~httpx+~websockets

# LogPile 日志输出等级，可以为INFO
LOGPILE_LEVEL=INFO

# localstore插件的缓存路径
LOCALSTORE_CACHE_DIR=data/nonebot/cache

# localstore插件的配置路径
LOCALSTORE_CONFIG_DIR=data/nonebot/config

# localstore插件的数据路径
LOCALSTORE_DATA_DIR=data/nonebot/data

# 超级用户拥有对Bot的最高权限，此处填写QQ号
SUPERUSERS=[""]

# 用不着，因为Chat插件会以CHAT__NICKNAME变量识别昵称
# NICKNAME=[""]

# NoneBot2监听的IP或主机名，如果要对公网开放，请改成0.0.0.0
HOST=127.0.0.1

# NoneBot2监听的端口,如果说你想以Nonebot作为服务端;
# 那么请确保客户端连接的端口与服务端的8080(示例)端口一致
PORT=8080

# LogPile日志保留天数
LOGPILE_RETENTION=1

# 命令起始字符，插件会说无用
# COMMAND_START=["", "/", "#"]

# 命令分割字符，插件依然会说无用
# COMMAND_SEP=[".", " "]

# Chat_Plugin配置
# API_Key
CHAT__API_KEY=<api_key>

# API Base Url
CHAT__API_BASE=<api_base_url>

# Model
CHAT__MODEL=<model>

# 初始Prompt，用于决定人格
SYSTEM_PROMPT=你是一个有用的AI

# 机器人昵称，直接叫昵称也可以响应你，亚托莉是一个示例
CHAT__NICKNAME=["亚托莉"]

# 模型参数配置
# 最大Token数（可选，默认1000）
# 1 个中文字符 ≈ 0.6 个 token
# 1 个英文字符 ≈ 0.3 个 token
CHAT__MAX_TOKENS=1000

# 温度系数（可选，默认1.0，值越大越“有创意”;越小则更“严格”）
CHAT__TEMPERATURE=1.0

# 连接API超时时间（单位:秒，可选，默认30）
CHAT__TIMEOUT=30

# 全局开关（true=开启过滤，false=关闭过滤，注意小写）
MANAGER__GLOBAL_SWITCH=true

# 违禁词列表（支持 JSON 数组格式，推荐）
MANAGER__BAN_KEYWORDS=["看看腿"]

# 群聊白名单（只允许这些群号与机器人互动，多个用逗号分隔或 JSON 数组）
MANAGER__GROUP_WHITELIST=<群号>
# 或者使用 JSON 数组格式：
# MANAGER__GROUP_WHITELIST=[XXX,XXX,XXX]

# 用户黑名单（禁止这些用户与机器人互动，无论私聊还是群聊）
MANAGER__USER_BLACKLIST=<QQ号>
# 同理，MANAGER__USER_BLACKLIST=[XXX,XXX]

# 允许的命令（以 / 开头的命令，只有列表中的命令才会被放行）
MANAGER__COMMANDS=/reload, /status, /clear

# OneBot 适配器配置
# 例如使用NapCat连接到Nonebot所需要的令牌(token)
# 默认ayasanko，若要修改请保持客户端与服务端令牌一致
ONEBOT_ACCESS_TOKEN=ayasanko
```

_vi编辑器: 编辑完按ESC键，输入`:wq`保存并退出，若出现无法保存的情况请输入`:qa!`即可强制退出_
~~_notepad编辑器: 不会保存就去私吧_~~

另外，此项目的设计默认启用反向WebSocket服务端，服务端端口请见`.env`文件中的`PORT`变量值，另外连接到服务端ws需要另外填写`token`，默认是`ayasanko`；

如要使用NapCat、OneBot等协议端，请使用反向WebSocket Client端

拿NapCat，具体教程请见[基于NapCat+NoneBot2的QQ机器人相关介绍和部署](https://catarium.me/posts/20251031)

### 4. 启动机器人

```bash
# 先返回到项目根目录
# Windows
.venv\Scripts\activate
python bot.py
# Linux(兼容性未知，若报错请及时反馈到Issue!)
source .venv/Scripts/activate
python bot.py
# 请暂时别用nb run直接启动项目，兼容性未知！
```

---

### 基本使用

1. `/status` 查询机器人运行状态
2. `/reload` 重新获取`.env`中的`CHAT__`环境变量值，目前此功能尚未完善
3. `/clear` 清理上下文，重置到初始人格

### 特性

- **"@"检测**：支持QQ原生@检测和CQ码匹配
- **错误处理**：API调用失败时提供友好的错误提示

### 配置验证机制

- **类型转换**：自动转换字符串类型的数字配置
- **错误处理**：配置格式错误时使用默认值并记录警告
- **日志记录**：配置加载失败时记录详细错误信息

### 环境变量值优先级

1. .env中的环境变量（如果存在）
2. 代码中的默认值`Default`（如果环境变量不存在或格式错误）

### 调试模式

#### 启用详细日志：

```python
# 在代码中添加调试日志，另外.env的LOGPILE_LEVEL要改成DEBUG
logger.debug("当前配置: %s", config)
```

#### 开发环境设置

```bash
# 安装开发依赖
pip install -U pyright pytest mypy

# 运行类型检查
pyright plugins/*/*.py
mypy plugins/*/*.py

# 运行测试
.venv/Scripts/activate #win
source .venv/Scripts/activate #linux
python bot.py
```

### 代码规范

- 遵循PEP 8代码风格
- 使用TypeScript类型注解
- 编写详细的文档字符串

---

## 许可证

- [MIT License](https://github.com/Laptis-Dev/Nonebot_AyaSanKo?tab=MIT-1-ov-file#)

---

## 相关链接

- [NoneBot2 Docs](https://nonebot.dev/docs/)
- [NoneBot2 API](https://nonebot.dev/docs/api/)
- [QQ机器人"开放"平台](https://q.qq.com)
- [OneBot_V11](https://github.com/botuniverse/onebot-11)
- [NapCat](https://napneko.github.io/guide/napcat)
