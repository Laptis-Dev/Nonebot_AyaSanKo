import nonebot
from nonebot.adapters.qq import Adapter as QQAdapter

from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter


nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(QQAdapter)  # pyright: ignore[reportUnknownMemberType]

driver.register_adapter(ONEBOT_V11Adapter)  # pyright: ignore[reportUnknownMemberType]
# fmt: off
_ = nonebot.load_builtin_plugins("echo", "single_session")
_ = nonebot.load_from_toml("pyproject.toml")
_ = nonebot.load_plugins("src/plugins", "./plugins")
# fmt: on

if __name__ == "__main__":
    nonebot.run()
