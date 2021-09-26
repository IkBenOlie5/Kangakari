import os

from kangakari import Bot
from kangakari import __version__


def main() -> None:
    if os.name != "nt":
        # uvloop doesn't work with lavasnek_rs yet
        """import uvloop

        uvloop.install()
        """

    bot = Bot(__version__)
    bot.run(asyncio_debug=True)


if __name__ == "__main__":
    main()
