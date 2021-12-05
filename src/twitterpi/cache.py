import json

from aiopath import AsyncPath
from datetime import datetime
from pathlib import Path
from pydantic.json import custom_pydantic_encoder
from twitterpi.dto import Tweet
from twitterpi.dto.tweet import _twitter_datetime_format
from typing import Any, Optional, AsyncGenerator

ENCODER_DICT = {
    datetime: lambda d: d.strftime(_twitter_datetime_format),
}


async def anext(gen: AsyncGenerator, default: Any = None) -> Any:
    """ Helper method for getting next item from given async generator `gen`. Return given `default` value if generator
        is empty (throws StopAsyncIteration error).
    
    Args:
        gen (obj: AsyncGenerator): Async generator to get item from.
        default (Any, default = None): Default value to return if generator is empty (throws StopAsyncIteration error).
    
    Returns:
        Any: Returned item from generator or given default value.
    """

    v = default
    try:
        v = await gen.__anext__()
    except StopAsyncIteration:
        pass
    return v


class Cache:
    def __init__(self, account_name: str):
        """ Constructor for Cache class.

        Create folders for `new_tweets` and `seen` tweets for given `account_name`.

        Args:
            account_name (str): Name of the account which cache dirs will be based off of.
        """

        base_dir: Path = Path(__file__).parent / "cache"
        for folder in ("new_tweets", "seen"):
            folder_path: Path = base_dir / account_name / folder
            folder_path.mkdir(exist_ok=True, parents=True)
            setattr(self, f"{folder}_dir", AsyncPath(folder_path))

    # QUERIES ---
    async def get_tweet(self) -> Optional[Tweet]:
        """ Get a tweet from the new tweets directory.

        Return:
            (obj: Tweet | None): Tweet retrieved from directory.
        """

        tweet = None
        tweet_path: Optional[AsyncPath] = await anext(self.new_tweets_dir.glob("*.json"))

        if tweet_path is not None:
            contents: str = await tweet_path.read_text()
            content_dict = json.loads(contents)
            tweet = Tweet(**content_dict)
        
        return tweet

    async def check_tweet_seen(self, tweet: Tweet) -> bool:
        """ Check if given `tweet` object has been seen before.

        Return:
            bool: Flag whether tweet exists.
        """

        tweet_path: AsyncPath = self.seen_dir / f"{tweet.id}.json"
        return await tweet_path.exists()

    # INSERTIONS ---
    async def insert_new_tweets(self, tweets: list[Tweet]):
        """ Insert given list of `tweets` into the new tweets directory.

        Args:
            tweets (list[obj: Tweet]): List of Tweet objects to insert.
        """

        for tweet in tweets:
            tweet_path: AsyncPath = self.new_tweets_dir / f"{tweet.id}.json"
            tweet_json: str = json.dumps(tweet, default=lambda d: custom_pydantic_encoder(ENCODER_DICT, d))
            await tweet_path.write_text(tweet_json)

    async def insert_seen_tweet(self, tweet: Tweet):
        """ Insert file for given `tweet` into the seen tweets directory.

        Args:
            tweet (obj: Tweet): Tweet that has been interacted with and is no-longer new.
        """

        seen_path: AsyncPath = self.seen_dir / f"{tweet.id}.json"
        await seen_path.touch()

    # DELETIONS ---
    async def remove_new_tweet(self, tweet: Tweet):
        """ Remove given `tweet` from new tweets directory.

        Args:
            tweet (obj: Tweet): Tweet that is no-longer new.
        """

        tweet_path: AsyncPath = self.new_tweets_dir / f"{tweet.id}.json"
        await tweet_path.unlink()
