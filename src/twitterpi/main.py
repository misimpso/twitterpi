import argparse
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
from twitterpi.oauth1_client import OAuth1ClientSession
from typing import Any

CONF_DIR = Path(__file__).parent / "conf"
CREDS_PATH = CONF_DIR / "credentials.toml"
SETTINGS_PATH = CONF_DIR / "settings.toml"
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

            oauth_session = OAuth1ClientSession(
                consumer_key=creds["consumer_key"],
                consumer_secret=creds["consumer_secret"],
                access_token=creds["access_token"],
                access_token_secret=creds["access_token_secret"],
            )

            api = Api(oauth_session=oauth_session)

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

    def setup_logging(self, log_path: Path, log_level: str):
        """ Instantiate the logging for the application.

        Args:
            log_ath (obj: Path): Path to output log file.
            log_level (str): Desired log level.
        """

        if not log_path.parent.exists():
            log_path.parent.mkdir(parents=True)

        logging.basicConfig(
            level=log_level,
            format="[%(asctime)s : %(levelname)s] [%(name)s] %(message)s",
            filename=log_path,
            filemode="a+",
        )

        formatter = logging.Formatter("[%(asctime)s : %(levelname)s] [%(name)s] %(message)s")

        handlers: list[logging.handler] = []

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(formatter)
        handlers.append(stream_handler)

        file_handler = RotatingFileHandler(log_path, "a+", 1024 * 1024, 30)
        file_handler.setLevel(log_level)
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
    """ Load account credentials and settings, setup logging, and start Twitter bots.
    """

    parser = argparse.ArgumentParser(description="Twitter Giveaway Bot")
    parser.add_argument("-c", "--creds-path", type=Path, dest="creds_path", default=CREDS_PATH, required=False, help="Path to account credentials file.")
    parser.add_argument("-s", "--settings-path", type=Path, dest="settings_path", default=SETTINGS_PATH, required=False, help="Path to account settings file.")
    parser.add_argument("-o", "--log-path", type=Path, dest="log_path", default=LOG_PATH, required=False, help="Path to output log file.")
    parser.add_argument("-l", "--log-level", type=str, dest="log_level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"), required=False, help="Desired log level.")

    args = parser.parse_args()

    bot = TwitterBot()
    bot.setup_logging(log_path=args.log_path, log_level=args.log_level)
    accounts = bot.load_accounts(creds_path=args.creds_path, settings_path=args.settings_path)
    bot.run(accounts)


if __name__ == "__main__":
    main()