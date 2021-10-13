import aiohttp
import asyncio
import toml

from twitterpi.account import Account
from pathlib import Path

CREDS_PATH = Path(__file__).parent / "conf" / "credentials.toml"


class TwitterBot:
    def load_accounts(self, creds_path: Path) -> list[Account]:
        """ TODO: docstring
        """
        creds_dict = self.__read_creds_file(creds_path)
        accounts = self.__initialize_accounts(creds_dict)
        return accounts
    
    def run(self, accounts: list[Account]):
        """ TODO: docstring
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[account.start() for account in accounts]))

    # async def main(self, accounts: list[Account]):
    #     """ TODO: docstring
    #     """
    #     for account in accounts:
    #         await account.start()

        
    def __read_creds_file(self, creds_path: Path) -> dict[str, str]:
        """ TODO: docstring
        """
        print(f"Loading account credentials ... [Path: {creds_path}]")
        if not creds_path.is_file():
            raise FileNotFoundError(f"Cannot load account credentials. [{creds_path}]")
        account_creds = {}
        with creds_path.open("r") as f:
            account_creds = toml.load(f)
        print("Account credentials loaded!")
        return account_creds
    
    def __initialize_accounts(self, accounts_dict: dict) -> list[Account]:
        """ TODO: docstring
        """
        print("Initializing accounts ...")
        accounts = []
        for name, creds in accounts_dict.items():
            accounts.append(
                Account(
                    name=name,
                    consumer_key=creds["consumer_key"],
                    consumer_secret=creds["consumer_secret"],
                    access_token=creds["access_token"],
                    access_token_secret=creds["access_token_secret"],
                ))
        print(f"Accounts initialized! {[a.name for a in accounts]}")
        return accounts


if __name__ == "__main__":
    bot = TwitterBot()
    accounts = bot.load_accounts(CREDS_PATH)
    bot.run(accounts)
