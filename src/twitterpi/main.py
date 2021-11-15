import asyncio
import logging
import logging.config
import toml

from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from pathlib import Path
from queue import SimpleQueue as Queue
from twitterpi.account import Account
from twitterpi.api import Api
from twitterpi.cache import Cache
from typing import Any

CONF_PATH = Path(__file__).parent / "conf"
COMMENT_STUBS_PATH = CONF_PATH / "comment_stubs.toml"
CREDS_PATH = CONF_PATH / "credentials.toml"
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

    def load_accounts(self, creds_path: Path) -> list[Account]:
        """ Read account credentials from given `creds_path` and instantiate Api, Cache, and Account objects.

        Args:
            creds_path (obj: Path): Path of account credentials file.
        
        Returns:
            list[obj: Account]: List of Account objects.
        """

        account_creds: dict[str, Any] = read_toml(creds_path)
        accounts: list[Account] = []
        for account_name in account_creds:
            creds = account_creds[account_name]
            api = Api(**creds)
            cache = Cache(account_name)
            accounts.append(Account(screen_name=account_name, api=api, cache=cache))
        return accounts
    
    def load_comments(self, comment_stubs_path: Path):
        """ Read comment stubs from given `comment_stubs_path` and set Account `normal_comments` and
            `tagged_comments` static variables. 

        Args:
            comment_stubs_path (obj: Path): Path to file with comment stubs.
        """

        comment_stubs: dict[str, Any] = read_toml(comment_stubs_path)
        Account.normal_comments = comment_stubs["comments"].strip().split("\n")
        Account.tagged_comments = comment_stubs["tagged_comments"].strip().split("\n")
        self.logger.info(f"Loaded [{len(Account.normal_comments)}] comment stubs.")
        self.logger.info(f"Loaded [{len(Account.tagged_comments)}] tagged comment stubs.")

    def setup_logging(self, logging_level: int = logging.INFO):
        """ TODO: docstring
        """

        if not LOG_PATH.parent.exists():
            LOG_PATH.parent.mkdir(parents=True)

        logging.basicConfig(
            level=logging_level,
            format="%(asctime)s - %(levelname)s - %(name)s : %(lineno)d - %(message)s",
            filename=LOG_PATH,
            filemode="a+",
        )

        handlers: list[logging.handler] = []

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging_level)
        handlers.append(stream_handler)

        file_handler = RotatingFileHandler(LOG_PATH, "a+", 1024 * 1024, 30)
        file_handler.setLevel(logging_level)
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

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[account.start() for account in accounts]))


def main():
    """ Instantiate the Account objects from credentials file, load comment stubs, and start asyncio loop.
    """

    bot = TwitterBot()
    bot.setup_logging()
    bot.load_comments(COMMENT_STUBS_PATH)
    accounts = bot.load_accounts(CREDS_PATH)
    bot.run(accounts)


if __name__ == "__main__":
    main()