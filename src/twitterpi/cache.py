import json

from aiopath import AsyncPath
from datetime import datetime
from pathlib import Path
from pydantic.json import custom_pydantic_encoder
from twitterpi.dto import Tweet, User
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
        for folder in ("tweets", "followers", "seen"):
            folder_path: Path = base_dir / account_name / folder
            folder_path.mkdir(exist_ok=True, parents=True)
            setattr(self, f"{folder}_base_dir", AsyncPath(folder_path))

    async def get_tweet(self) -> Optional[Tweet]:
        """ TODO: docstring
        """

        tweet = None
        tweet_path: AsyncPath = await anext(self.tweets_base_dir.glob("*.json"))

        if tweet_path is not None:
            contents: str = await tweet_path.read_text()
            content_dict = json.loads(contents)
            tweet = Tweet(**content_dict)
        
        return tweet
    
    async def insert_tweets(self, tweets: list[Tweet]):
        """ TODO: docstring
        """

        for tweet in tweets:
            tweet_path: AsyncPath = self.tweets_base_dir / f"{tweet.id}.json"
            tweet_json: str = json.dumps(tweet, default=lambda d: custom_pydantic_encoder(ENCODER_DICT, d))
            await tweet_path.write_text(tweet_json)

    async def get_random_followers(self, random_amount: int) -> Optional[list[User]]:
        """ TODO: docstring
        """

        followers: list[User] = []
        for _ in range(random_amount):
            follower_path: AsyncPath = await anext(self.followers_base_dir.glob("*.json"))
            if follower_path is None:
                break
            contents: str = await follower_path.read_text()
            content_dict = json.loads(contents)
            followers.append(User(**content_dict))
        return followers
    
    async def insert_followers(self, followers: list[User]):
        """ TODO: docstring
        """

        for follower in followers:
            follower_path: AsyncPath = self.followers_base_dir / f"{follower.id}.json"
            follower_json: str = json.dumps(follower, default=lambda d: custom_pydantic_encoder(ENCODER_DICT, d))
            await follower_path.write_text(follower_json)
    
    async def check_tweet_seen(self, tweet: Tweet) -> bool:
        """ TODO: docstring
        """

        tweet_path: AsyncPath = self.tweets_base_dir / f"{tweet.id}.json"
        seen = await tweet_path.exists()
        return seen
    
    async def remove_tweet(self, account_name: str, tweet: Tweet):
        """ TODO: docstring
        """

        tweet_path: AsyncPath = self.tweets_base_dir / f"{tweet.id}.json"
        seen_path: AsyncPath = self.seen_base_dir / f"{tweet.id}.json"

        await seen_path.touch()
        await tweet_path.unlink()
