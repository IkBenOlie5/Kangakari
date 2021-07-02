from pathlib import Path

import hikari
import lightbulb
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from kangakari import Config


class Bot(lightbulb.Bot):
    def __init__(self, version) -> None:
        self._plugins = [p.stem for p in Path(".").glob("./kangakari/core/plugins/*.py")]
        self._dynamic = "./kangakari/data/dynamic"
        self._static = "./kangakari/data/static"

        self.version = version

        self.scheduler = AsyncIOScheduler()
        self.config = Config()

        super().__init__(
            token=self.config.TOKEN,
            owner_ids=self.config.OWNER_IDS,
            intents=hikari.Intents.ALL,
            prefix=lightbulb.when_mentioned_or(self.resolve_prefix),
            insensitive_commands=True,
            ignore_bots=True,
        )

    def resolve_prefix(self, bot, message):
        return "!"
