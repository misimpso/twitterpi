import json
import random

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
    """ TODO: docstring
    """

    v = default
    try:
        v = await gen.__anext__()
    except StopAsyncIteration:
        pass
    return v


class Cache:
    def __init__(self, account_name: str):
        """ TODO: docstring
        """

        base_dir: Path = Path(__file__).parent / "cache"
        for folder in ("new_tweets", "seen"):
            folder_path: Path = base_dir / account_name / folder
            folder_path.mkdir(exist_ok=True, parents=True)
            setattr(self, f"{folder}_dir", AsyncPath(folder_path))

    # QUERIES ---
    async def get_tweet(self) -> Optional[Tweet]:
        """ TODO: docstring
        """

        tweet = None
        tweet_path: Optional[AsyncPath] = await anext(self.new_tweets_dir.glob("*.json"))

        if tweet_path is not None:
            contents: str = await tweet_path.read_text()
            content_dict = json.loads(contents)
            tweet = Tweet(**content_dict)
        
        return tweet

    async def check_tweet_seen(self, tweet: Tweet) -> bool:
        """ TODO: docstring
        """

        tweet_path: AsyncPath = self.seen_dir / f"{tweet.id}.json"
        return await tweet_path.exists()
    
    async def check_replies_populated(self) -> bool:
        """ TODO: docstring
        """

        reply_path: Optional[AsyncPath] = await anext(self.replies_dir.glob("*.json"))
        return reply_path != None

    async def check_tweet_replied(self, tweet: Tweet) -> bool:
        """ TODO: docstring
        """

        tweet_path: AsyncPath = self.replies_dir / f"{tweet.id}.json"
        return await tweet_path.exists()

    # INSERTIONS ---
    async def insert_new_tweets(self, tweets: list[Tweet]):
        """ TODO: docstring
        """

        for tweet in tweets:
            tweet_path: AsyncPath = self.new_tweets_dir / f"{tweet.id}.json"
            tweet_json: str = json.dumps(tweet, default=lambda d: custom_pydantic_encoder(ENCODER_DICT, d))
            await tweet_path.write_text(tweet_json)

    async def insert_seen_tweet(self, tweet: Tweet):
        """ TODO: docstring
        """

        seen_path: AsyncPath = self.seen_dir / f"{tweet.id}.json"
        await seen_path.touch()

    # DELETIONS ---
    async def remove_new_tweet(self, tweet: Tweet):
        """ TODO: docstring
        """

        tweet_path: AsyncPath = self.new_tweets_dir / f"{tweet.id}.json"
        await tweet_path.unlink()
