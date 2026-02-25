# Nonebot_AyaSanKo - AI聊天机器人

基于 NoneBot2 框架的智能聊天机器人插件，集成 BigModel GLM-4.5-Air API，支持QQ群聊智能对话。

## 根据QQ官方的文档，使用AI接入API未经备案，将受到封禁的后果，请用户慎重使用。
[t032FI8PMYJNuuOcZ6fJET9dXYEPF5ywkCqiYcz-Xcfg_USyCulJzXlG8KLexwj1C11GAQVKB0tSaRjiv0wiMqHX1MwglfFwXwlPbEA3aWF2AgDP-j8zxcq9vcUAIgtL21uabAjSRI9INbyemMqJruRnoNfS99_cHaGFiLtzT1iH5ZY1W9hkwNJRbGJDSMPAFoN](https://pd.qq.com/g/20dnumts4z/post/B_e542d268c1a607001441152197297526170X60?subc=1409545)

## 🚀 功能特性

- **智能对话**：基于GLM-4.5-Air大语言模型，提供高质量的AI回复
- **@触发**：在QQ群聊中被@时自动触发对话
- **类型安全**：完整的TypeScript类型定义和运行时验证
- **配置灵活**：支持环境变量配置，易于部署和扩展
- **错误处理**：完善的异常处理和日志记录机制

## 📦 安装配置

### 0. Fork仓库后的配置（重要）

如果您Fork了此仓库，为了使自动部署工作流正常运行，需要完成以下步骤：

#### 添加GitHub Secrets

在您Fork的仓库中，进入 **Settings → Secrets and variables → Actions**，添加以下 Secrets：

| Secret名称     | 说明             | 获取方式                                      |
| -------------- | ---------------- | --------------------------------------------- |
| `QQ_BOTS`      | QQ机器人配置JSON | 见下方示例                                    |
| `CHAT_API_KEY` | BigModel API密钥 | [BigModel开放平台](https://open.bigmodel.cn/) |

**QQ_BOTS 配置示例：**

```json
[
  {
    "id": "你的机器人QQ号",
    "token": "QQ机器人token",
    "secret": "QQ机器人secret",
    "intent": {
      "c2c_group_at_messages": true
    },
    "use_websocket": true
  }
]
```

将上述JSON内容保存为Secret `QQ_BOTS`。

#### 验证工作流

- 在 **Actions** 标签页检查工作流状态
- 确保 `Debug Setup` 工作流成功运行
- 检查部署日志确认机器人已启动

### 1. 环境准备

```bash
# 确保Python 3.10+
python --version

# 安装NoneBot2
pip install nonebot2[fastapi]
pip install nonebot-adapter-qq
```

### 2. 项目初始化

```bash
# 创建NoneBot项目
nb create

# 安装插件
nb plugin install nonebot-adapter-qq
```

### 3. 配置环境变量

创建 `.env` 文件并添加以下配置：

```env
# BigModel API配置
CHAT__API_KEY=your_api_key_here
CHAT__API_BASE=https://open.bigmodel.cn/api/paas/v4
CHAT__MODEL=glm-4.5-air

# 模型参数配置
CHAT__MAX_TOKENS=1000
CHAT__TEMPERATURE=1.0
CHAT__TIMEOUT=30
```

**配置说明：**

- `CHAT__API_KEY`: BigModel API密钥（必需）
- `CHAT__API_BASE`: API基础地址（可选，默认使用官方地址）
- `CHAT__MODEL`: 使用的模型名称（可选，默认使用glm-4.5-air）
- `CHAT__MAX_TOKENS`: 最大令牌数（可选，默认1000）
- `CHAT__TEMPERATURE`: 回复温度（可选，默认1.0）
- `CHAT__TIMEOUT`: API超时时间（秒，可选，默认30）

### 4. 启动机器人

```bash
nb run
```

## 🎯 使用方法

### 基本使用

1. 在QQ群中 @机器人 并发送消息
2. 机器人会自动调用GLM-4.5-Air API生成回复
3. 支持多轮对话，上下文理解能力强

### 高级特性

- **@检测**：支持QQ原生@检测和CQ码匹配
- **错误处理**：API调用失败时提供友好的错误提示
- **状态提示**：显示"思考中..."状态，提升用户体验

## 🔧 配置详解

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

## 🐛 故障排除

### 常见问题

**1. API密钥错误**

```bash
# 检查环境变量是否正确设置
echo $CHAT__API_KEY
```

**2. 配置加载失败**
查看日志输出，检查环境变量格式是否正确：

```bash
# 示例错误信息
[WARNING] 环变量 abc 无法转换为整数，使用默认值 1000
[ERROR] 配置加载失败: invalid literal for int() with base 10: 'abc'
```

**3. 连接超时**

- 检查网络连接
- 调整 `CHAT__TIMEOUT` 值
- 确认API地址正确

### 调试模式

启用详细日志：

```python
# 在代码中添加调试日志
logger.debug("当前配置: %s", config)
```

## 📝 开发文档

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

### 代码质量

- ✅ 类型检查：通过pyright严格检查
- ✅ 错误处理：完善的异常捕获机制
- ✅ 日志记录：使用nonebot.logger统一日志
- ✅ 配置验证：运行时配置验证和默认值处理

## 🤝 贡献指南

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

## 📄 许可证

MIT License

## 🔗 相关链接

- [NoneBot2文档](https://nonebot.dev/)
- [BigModel API文档](https://open.bigmodel.cn/)
- [GLM-4.5-Air模型介绍](https://open.bigmodel.cn/modelcenter/api/gl4)
