import asyncio
import logging
import logging.config
import toml

from contextlib import closing
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from pathlib import Path
from queue import SimpleQueue as Queue
from twitterpi.account import Account
from twitterpi.api import Api
from twitterpi.cache import Cache
from typing import Any

CONF_PATH = Path(__file__).parent / "conf"
CREDS_PATH = CONF_PATH / "credentials.toml"
SETTINGS_PATH = CONF_PATH / "settings.toml"
LOGGING_CONFIG_PATH = CONF_PATH / "logging.conf"
LOG_PATH = Path(__file__).parent / "logs" / "twitterpi.log"


def read_toml(file_path: Path) -> dict[str, Any]:
        """ Utility method to read and return contents of .toml file from given `file_path`.

        Args:
            file_path (obj: Path): File path to read from.
        
        Returns:
            dict[str, Any]: Dictionary of file contents.
        """

        contents: dict[str, Any] = {}
        with file_path.open("r") as f:
            contents: dict[str, Any] = toml.load(f)
        return contents


class TwitterBot:
    """ Main class for kicking off the Twitter bot accounts.
    """
    
    logger = logging.getLogger(__name__)

    def load_accounts(self, creds_path: Path, settings_path: Path) -> list[Account]:
        """ Read account credentials from given `creds_path` and instantiate Api, Cache, and Account objects.

        Args:
            creds_path (obj: Path): Path of account credentials file.
            settings_path (obj: Path): Path of account settings file.
        
        Returns:
            list[obj: Account]: List of Account objects.
        """

        account_creds: dict[str, Any] = read_toml(creds_path)
        account_settings: dict[str, Any] = read_toml(settings_path)

        if account_creds.keys() != account_settings.keys():
            raise RuntimeError(
                "Account credentials and settings files don't have matching sections. ",
                f"[Creds: {list(account_creds.keys())}, Settings: {list(account_settings.keys())}]",
            )

        accounts: list[Account] = []
        for account_name in account_creds:

            creds: dict[str, str] = account_creds[account_name]
            settings: dict[str, list[str]] = account_settings[account_name]

            api = Api(
                consumer_key=creds["consumer_key"],
                consumer_secret=creds["consumer_secret"],
                access_token=creds["access_token"],
                access_token_secret=creds["access_token_secret"],
            )
            cache = Cache(account_name=account_name)

            account = Account(
                screen_name=account_name,
                api=api,
                cache=cache,
                search_terms=settings["search_terms"],
                filter_terms=settings["filters"],
            )

            accounts.append(account)
        return accounts

    def setup_logging(self, logging_level: int = logging.INFO):
        """ TODO: docstring
        """

        if not LOG_PATH.parent.exists():
            LOG_PATH.parent.mkdir(parents=True)

        logging.basicConfig(
            level=logging_level,
            format="[%(asctime)s : %(levelname)s] [%(name)s] %(message)s",
            filename=LOG_PATH,
            filemode="a+",
        )

        formatter = logging.Formatter("[%(asctime)s : %(levelname)s] [%(name)s] %(message)s")

        handlers: list[logging.handler] = []

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging_level)
        stream_handler.setFormatter(formatter)
        handlers.append(stream_handler)

        file_handler = RotatingFileHandler(LOG_PATH, "a+", 1024 * 1024, 30)
        file_handler.setLevel(logging_level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

        queue = Queue()
        queue_handler = QueueHandler(queue)
        logging.getLogger().addHandler(queue_handler)

        listener = QueueListener(queue, *handlers, respect_handler_level=True)
        listener.start()
    
    def run(self, accounts: list[Account]):
        """ Kickstart asyncio loop with each account from given `accounts` argument.

        Args:
            accounts (list[obj: Account]): List of instantiated Account objects.
        """

        with closing(asyncio.get_event_loop()) as loop:
            loop.run_until_complete(asyncio.gather(*[account.start() for account in accounts]))


def main():
    """ Instantiate the Account objects from credentials file, load comment stubs, and start asyncio loop.
    """

    bot = TwitterBot()
    bot.setup_logging()
    accounts = bot.load_accounts(CREDS_PATH, SETTINGS_PATH)
    bot.run(accounts)


if __name__ == "__main__":
    main()