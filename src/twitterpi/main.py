import asyncio
import toml
import typing as ty

from pathlib import Path
from twitterpi.account import Account
from twitterpi.api import Api
from twitterpi.cache import Cache

CREDS_PATH = Path(__file__).parent / "conf" / "credentials.toml"
COMMENT_STUBS_PATH = Path(__file__).parent / "conf" / "comment_stubs.toml"


def read_toml(file_path: Path) -> dict[str, ty.Any]:
    """ TODO: doccstring
    """

    contents: dict[str, ty.Any] = {}
    with file_path.open("r") as f:
        contents = toml.load(f)
    return contents


class TwitterBot:
    def load_accounts(self, creds_path: Path) -> list[Account]:
        """ TODO: docstring
        """

        account_creds: dict[str, ty.Any] = read_toml(creds_path)
        accounts: list[Account] = []
        for account_name in account_creds:
            creds = account_creds[account_name]
            api = Api(**creds)
            cache = Cache(account_name)
            accounts.append(Account(screen_name=account_name, api=api, cache=cache))
        return accounts
    
    def load_comments(self, comment_stubs_path: Path):
        """ TODO: docstring
        """

        comment_stubs: dict[str, ty.Any] = read_toml(comment_stubs_path)
        Account.normal_comments = comment_stubs["comments"].split("\n")
        Account.tagged_comments = comment_stubs["tagged_comments"].split("\n")
    
    def run(self, accounts: list[Account]):
        """ TODO: docstring
        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[account.start() for account in accounts]))


def main():
    bot = TwitterBot()
    bot.load_comments(COMMENT_STUBS_PATH)
    accounts = bot.load_accounts(CREDS_PATH)
    bot.run(accounts)


if __name__ == "__main__":
    main()