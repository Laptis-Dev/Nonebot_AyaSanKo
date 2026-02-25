# Nonebot_AyaSanKo

一个基于 NoneBot2 框架的QQ机器人项目.

## 正在开发的插件

- status_plugin 查询机器人状态的插件，可用/status指令查询
- chat_plugin 集成了人工智能的辅助聊天插件，无需指令响应
- (尚未计划...)

### 1. 环境准备

```bash
# 确保Python 3.10+(插件代码所用的PythonAPI几乎都基于3.10)
python --version

# 安装pipx (pip的替代物)
python -m pip install --user pipx

# 添加到系统的 PATH 环境变量中
python -m pipx ensurepath

# 安装NoneBot2
pipx install nb-cli
```

### 2. 下载本项目

```bash
git clone https://github.com/Laptis-Dev/Nonebot_AyaSanKo.git
```

### 3. 配置环境变量

创建 `.env` 文件并添加以下配置：

```env
# Nonebot基础配置(对不起了密集恐惧患者/(ㄒoㄒ)/~~)

DRIVER=~fastapi+~httpx+~websockets
LOGPILE_LEVEL=INFO # LogPile 日志输出等级，可以为列表
LOCALSTORE_CACHE_DIR=data/nonebot/cache #重定向localstore插件的缓存路径
LOCALSTORE_CONFIG_DIR=data/nonebot/config #重定向localstore插件的配置路径
LOCALSTORE_DATA_DIR=data/nonebot/data #重定向localstore插件的数据路径
SUPERUSERS=[""] # 超级用户拥有对Bot的最高权限
NICKNAME=[""] # 机器人的昵称,消息以昵称开头可以代替艾特(似乎QQ官方机器人除外)
HOST=127.0.0.1 # NoneBot2监听的IP或主机名,如果要对公网开放，请改成 0.0.0.0
PORT=8080 #NoneBot2监听的端口,请保证该端口号与连接端配置相同或与端口映射配置相关
LOGPILE_RETENTION=7 # LogPile 日志保留天数
COMMAND_START=["", "/", "#"] # 命令起始字符
COMMAND_SEP=[".", " "] # 命令分割字符

# Chat插件配置
CHAT__API_KEY=your_api_key_here #API密钥（必需）
CHAT__API_BASE=https://open.bigmodel.cn/api/paas/v4 #示例
CHAT__MODEL=glm-4.5-air #示例

# 模型参数配置
CHAT__MAX_TOKENS=1000 #最大令牌数（可选，默认1000）
CHAT__TEMPERATURE=1.0 #回复温度（可选，默认1.0）
CHAT__TIMEOUT=30 #API超时时间（秒，可选，默认30）

# OneBot 适配器配置

# ONEBOT_ACCESS_TOKEN=你的访问令牌
# ONEBOT_SECRET=你的签名

# OneBot V11 正向 Universal WebSocket 配置
# 参考 https://onebot.adapters.nonebot.dev/docs/guide/setup#%E6%AD%A3%E5%90%91-websocket-%E8%BF%9E%E6%8E%A5
# 请确保你的 NoneBot 使用的是 ForwardDriver，否则无法使用此连接方式。
# ONEBOT_WS_URLS=["ws://127.0.0.1:5700"]

# OneBot V11 HTTP POST 配置
# 参考 https://onebot.adapters.nonebot.dev/docs/guide/setup#http-post
# 请确保你的 NoneBot 使用的是 ForwardDriver 和 ReverseDriver，否则无法使用此连接方式。
# ONEBOT_API_ROOTS={"Bot QQ号": "http://127.0.0.1:5700/"}

# OneBot V12 正向 WebSocket 配置
# 参考 https://onebot.adapters.nonebot.dev/docs/guide/setup#%E6%AD%A3%E5%90%91-websocket-%E8%BF%9E%E6%8E%A5-1
# 请确保你的 NoneBot 使用的是 ForwardDriver，否则无法使用此连接方式。
# ONEBOT_V12_WS_URLS=["ws://127.0.0.1:5700"]

# OneBot V12 HTTP Webhook 配置
# 参考 https://onebot.adapters.nonebot.dev/docs/guide/setup#http-webhook
# 请确保你的 NoneBot 使用的是 ForwardDriver 和 ReverseDriver，否则无法使用此连接方式。
# ONEBOT_V12_API_ROOTS={"Bot QQ号": "http://127.0.0.1:5700/"}
```

另外，Nonebot默认启用反向WS，如要使用NapCat、OneBot等协议端，请使用WS Client

拿NapCat，具体教程请见[基于NapCat+NoneBot2的QQ机器人相关介绍和部署](https://catarium.me/posts/20251031)

### 4. 启动机器人

```bash
nb run
```

### 基本使用

1. 在QQ群中 @机器人 并发送消息，使用/status可以查询机器人运行状态
2. 机器人会自动调用API生成回复
3. 支持上下文，实现多轮对话

### 高级特性

- **@检测**：支持QQ原生@检测和CQ码匹配
- **错误处理**：API调用失败时提供友好的错误提示

### 环境变量命名规则

支持两种命名格式：

- `CHAT__API_KEY`（推荐，符合NoneBot2规范）
- `CHAT_API_KEY`（兼容格式）

### 配置验证机制

- **类型转换**：自动转换字符串类型的数字配置
- **错误处理**：配置格式错误时使用默认值并记录警告
- **日志记录**：配置加载失败时记录详细错误信息

### 配置优先级

1. 环境变量值（如果存在）
2. 默认值（如果环境变量不存在或格式错误）

### 调试模式

启用详细日志：

```python
# 在代码中添加调试日志
logger.debug("当前配置: %s", config)
```

## 开发文档

### 核心组件

#### ChatConfig类

```python
class ChatConfig(BaseModel):
    api_key: str | None
    api_base: str
    model: str
    max_tokens: int
    temperature: float
    timeout: int
```

#### 类型守卫

- `is_send_response()`: 验证发送响应格式
- `is_api_response()`: 验证API响应格式

#### 安全转换函数

- `safe_int()`: 安全转换整数环境变量
- `safe_float()`: 安全转换浮点数环境变量

## 给予贡献

欢迎提交Issue和Pull Request！

### 开发环境设置

```bash
# 安装开发依赖
pip install pyright pytest

# 运行类型检查
pyright plugins/status/__init__.py
pyright plugins/chat/__init__.py
pyright plugins/chat/config.py
pyright plugins/chat/processor.py

# 运行测试
nb run
or
python bot.py
```

### 代码规范

- 遵循PEP 8代码风格
- 使用TypeScript类型注解
- 编写详细的文档字符串

## 许可证

- [MIT License](https://github.com/Laptis-Dev/Nonebot_AyaSanKo?tab=MIT-1-ov-file#)

## 相关链接

- [NoneBot2文档](https://nonebot.dev/)
