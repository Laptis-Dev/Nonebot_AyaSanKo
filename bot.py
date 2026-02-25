import nonebot
from nonebot.adapters.qq import Adapter as QQAdapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(QQAdapter)  # pyright: ignore[reportUnknownMemberType]

_ = nonebot.load_builtin_plugins('echo')
_ = nonebot.load_from_toml("pyproject.toml")
_ = nonebot.load_plugins("./plugins")

if __name__ == "__main__":
    nonebot.run()