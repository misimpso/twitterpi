import unittest

from aiopath import AsyncPath
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from twitterpi.cache import Cache
from twitterpi.dto import Tweet, User
from types import SimpleNamespace

TEST_ACCOUNT_NAME = "Dennis"
NOW = datetime.now()
TEST_AUTHOR = User(id=0, screen_name="Kevin")
TEST_TWEETS = [
    Tweet(id=1, created_at=NOW, text="Test-1", author=TEST_AUTHOR, mentions=[]),
    Tweet(id=2, created_at=NOW, text="Test-2", author=TEST_AUTHOR, mentions=[User(id=0, screen_name="Mikey")]),
    Tweet(id=3, created_at=NOW, text="Test-3", author=TEST_AUTHOR, mentions=[
        User(id=0, screen_name="Carson"),
        User(id=0, screen_name="Dileep"),
        User(id=0, screen_name="Petr"),
    ]),
]


class CacheTests(unittest.IsolatedAsyncioTestCase):

    async def test_get_tweet__verify_expected_return_value_when_tweets_should_exist(self):
        """ Verify `get_tweet` returns Tweet object when tweets should exist.
        """

        with TemporaryDirectory() as temp_dir:

            cache = Cache(account_name=TEST_ACCOUNT_NAME, base_dir=Path(str(temp_dir)))
            await cache.insert_new_tweets(TEST_TWEETS)

            tweet: Tweet = await cache.get_tweet()
            self.assertIsInstance(tweet, Tweet)

    async def test_get_tweet__verify_expected_return_value_when_tweets_shouldnt_exist(self):
        """ Verify `get_tweet` returns None when tweets shouldn't exist.
        """

        with TemporaryDirectory() as temp_dir:

            cache = Cache(account_name=TEST_ACCOUNT_NAME, base_dir=Path(str(temp_dir)))
            tweet = await cache.get_tweet()
            self.assertIsNone(tweet)

    async def test_check_tweet_seen__verify_return_value_when_file_shouldnt_exist(self):
        """ Verify `check_tweet_seen` returns False when file shouldn't exist.
        """

        with TemporaryDirectory() as temp_dir:

            tweet = SimpleNamespace(id=0)
            cache = Cache(account_name=TEST_ACCOUNT_NAME, base_dir=Path(str(temp_dir)))
            exists: bool = await cache.check_tweet_seen(tweet)
            self.assertFalse(exists)

    async def test_check_tweet_seen__verify_return_value_when_file_should_exists(self):
        """ Verify `check_tweet_seen` returns True when file should exist.
        """

        with TemporaryDirectory() as temp_dir:

            tweet = SimpleNamespace(id=0)
            cache = Cache(account_name=TEST_ACCOUNT_NAME, base_dir=Path(str(temp_dir)))
            tweet_path: AsyncPath = cache.seen_dir / f"{tweet.id}.json"
            await tweet_path.touch()

            exists: bool = await cache.check_tweet_seen(tweet)
            self.assertTrue(exists)

    async def test_insert_new_tweets__verify_tweets_inserted(self):
        """ Verify `insert_new_tweets` finds files after insertion.
        """

        with TemporaryDirectory() as temp_dir:

            cache = Cache(account_name=TEST_ACCOUNT_NAME, base_dir=Path(str(temp_dir)))
            await cache.insert_new_tweets(TEST_TWEETS)

            for tweet in TEST_TWEETS:
                tweet_path: AsyncPath = cache.new_tweets_dir / f"{tweet.id}.json"
                exists: bool = await tweet_path.exists()
                self.assertTrue(exists)

    async def test_insert_seen_tweet__verify_tweet_inserted(self):
        """ Verify `insert_seen_tweet` finds file after insertion.
        """

        with TemporaryDirectory() as temp_dir:

            tweet = SimpleNamespace(id=0)
            cache = Cache(account_name=TEST_ACCOUNT_NAME, base_dir=Path(str(temp_dir)))
            await cache.insert_seen_tweet(tweet)

            tweet_path: AsyncPath = cache.seen_dir / f"{tweet.id}.json"
            exists: bool = await tweet_path.exists()
            self.assertTrue(exists)

    async def test_remove_new_tweet__verify_tweet_removed(self):
        """ Verify `remove_new_tweet` cannot find file after deletion.
        """

        with TemporaryDirectory() as temp_dir:

            tweet = SimpleNamespace(id=0)
            cache = Cache(account_name=TEST_ACCOUNT_NAME, base_dir=Path(str(temp_dir)))
            tweet_path: AsyncPath = cache.new_tweets_dir / f"{tweet.id}.json"
            await tweet_path.touch()

            await cache.remove_new_tweet(tweet)

            exists = await tweet_path.exists()
            self.assertFalse(exists)


if __name__ == "__main__":
    unittest.main()
