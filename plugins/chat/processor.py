"""
聊天处理器 - 异步化改造
支持并发控制、任务队列、重试机制和性能监控
"""

import asyncio
import time
from dataclasses import dataclass, field
from asyncio import Future, PriorityQueue
from typing import cast
from nonebot.log import logger
from nonebot.adapters.qq import Bot, MessageEvent
from .config import ChatConfig


@dataclass(order=True)
class ChatTask:
    """聊天任务"""

    priority: int = 0
    message: str = ""
    user_id: str = ""
    start_time: float = 0.0
    result: Future[str] = field(default_factory=Future)

    def __post_init__(self):
        if self.start_time == 0.0:
            self.start_time = time.time()

    async def execute(self, processor: "ChatProcessor"):
        """执行任务"""
        # processor参数类型检查确保不为None，移除不必要的None检查

        async with processor.semaphore:
            try:
                # 调用API获取结果
                api_response = await processor.call_bigmodel_api(self.message)
                if not self.result.done():
                    self.result.set_result(api_response)
                else:
                    logger.warning("Task already completed, skipping result set")
            except Exception as e:
                logger.error(f"API call failed: {e}")
                if not self.result.done():
                    self.result.set_exception(e)


class UserTaskQueue:
    """用户独立任务队列"""

    user_id: str
    processor: "ChatProcessor"
    queue: PriorityQueue[ChatTask]
    processing: bool
    current_task: ChatTask | None

    def __init__(self, user_id: str, processor: "ChatProcessor"):
        self.user_id = user_id
        self.processor = processor
        self.queue = PriorityQueue[ChatTask]()
        self.processing = False
        self.current_task = None

    async def add_task(self, task: ChatTask):
        """添加任务到队列"""
        await self.queue.put(task)
        if not self.processing:
            _ = asyncio.create_task(self._process_queue())  # type: ignore

    async def _process_queue(self):
        """处理队列中的任务"""
        self.processing = True
        try:
            while not self.queue.empty():
                task = await self.queue.get()
                self.current_task = task
                try:
                    await task.execute(self.processor)  # 传递真实的processor实例
                except Exception as e:
                    logger.error(f"Task execution failed for user {self.user_id}: {e}")
                    task.result.set_exception(e)
                finally:
                    self.current_task = None
        finally:
            self.processing = False


class ChatProcessor:
    """聊天处理器 - 异步化改造"""

    config: ChatConfig
    user_queues: dict[str, UserTaskQueue]
    semaphore: asyncio.Semaphore
    metrics: dict[str, object]

    def __init__(self, config: ChatConfig):
        self.config = config
        self.user_queues = {}
        self.semaphore = asyncio.Semaphore(config.max_concurrent or 5)
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time": 0.0,
            "current_queue_length": 0,
        }

    async def process_message(
        self, message: str, user_id: str, _bot: Bot, _message_event: MessageEvent
    ) -> str:
        """处理消息"""
        # 获取或创建用户队列
        if user_id not in self.user_queues:
            self.user_queues[user_id] = UserTaskQueue(user_id, self)

        # 创建任务
        task = ChatTask(
            message=message,
            user_id=user_id,
            start_time=time.time(),
            result=asyncio.Future(),
        )

        # 添加到队列
        await self.user_queues[user_id].add_task(task)

        # 等待任务完成
        try:
            result = await task.result
            return result
        except Exception as e:
            logger.error(f"Task failed for user {user_id}: {e}")
            raise

    async def call_bigmodel_api(self, message: str) -> str:
        """调用BigModel API（带重试机制）"""
        import httpx

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": message}],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                f"{self.config.api_base}/chat/completions",
                headers=headers,
                json=payload,
            )

            raw_data = cast(object, response.json())
            if not isinstance(raw_data, dict):
                logger.error("API返回格式错误：响应不是字典类型")
                raise Exception("API返回格式错误：响应不是字典类型")
            data = cast(dict[str, object], raw_data)

            if "choices" not in data:
                logger.error("API返回格式错误：缺少choices字段")
                raise Exception("API返回格式错误")

            choices_raw = data["choices"]
            if not isinstance(choices_raw, list):
                logger.error("API返回格式错误：choices不是列表类型")
                raise Exception("API返回格式错误")
            choices_data = cast(list[object], choices_raw)
            if len(choices_data) == 0:
                logger.error("API返回格式错误：choices列表为空")
                raise Exception("API返回格式错误")

            choices: list[object] = choices_data
            if not isinstance(choices[0], dict):
                logger.error("API返回格式错误：choices[0]不是字典")
                raise Exception("API返回格式错误")

            if "message" not in choices[0] or not isinstance(
                choices[0]["message"], dict
            ):
                logger.error("API返回格式错误：message结构异常")
                raise Exception("API返回格式错误")

            if "content" not in choices[0]["message"]:
                logger.error("API返回格式错误：缺少content字段")
                raise Exception("API返回格式错误")

            content_raw = cast(object, choices[0]["message"]["content"])
            if not isinstance(content_raw, str):
                logger.error("API返回格式错误：content不是字符串类型")
                raise Exception("API返回格式错误")
            content: str = content_raw
            result: str = content
            logger.info(f"API response received: {result[:50]}...")
            return result

    async def get_queue_length(self, user_id: str) -> int:
        """获取用户队列长度"""
        if user_id not in self.user_queues:
            return 0
        return self.user_queues[user_id].queue.qsize()

    def get_metrics(self) -> dict[str, object]:
        """获取性能指标"""
        return self.metrics.copy()

    def cleanup_expired_queues(self) -> None:
        """清理空闲队列"""
        expired_users: list[str] = []

        for user_id, user_queue in self.user_queues.items():
            # 队列为空且没有正在执行的任务时,标记为过期
            if user_queue.queue.empty() and user_queue.current_task is None:
                expired_users.append(user_id)

        for user_id in expired_users:
            del self.user_queues[user_id]
            logger.info(f"Cleaned up expired queue for user {user_id}")
