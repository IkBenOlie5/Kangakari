import os

from kangakari import Bot, __version__


def main():
    if os.name != "nt":
        import uvloop

        uvloop.install()

    bot = Bot(__version__)
    bot.run()


if __name__ == "__main__":
    main()
