import logging

from aiohttp.client_exceptions import ContentTypeError
from twitterpi.dto import Tweet, User
from twitterpi.limiter import Limiter
from twitterpi.oauth1_client import OAuth1ClientSession

from pprint import pprint


BASE_URL = "https://api.twitter.com/1.1/"
URLS = {
    "favorite_tweet": f"{BASE_URL}favorites/create.json",
    "follow_user": f"{BASE_URL}friendships/create.json",
    "get_user_followers": f"{BASE_URL}followers/list.json",
    "retweet": f"{BASE_URL}statuses/retweet/{{}}.json",
    "search": f"{BASE_URL}search/tweets.json",
    "tweet": f"{BASE_URL}statuses/update.json",
    "lookup": f"{BASE_URL}statuses/show.json",
    "get_user_tweets": f"{BASE_URL}statuses/user_timeline.json",
}

SEARCH_LIMITER = Limiter(requests_per_day=10000)
FAVORITE_LIMITER = Limiter(requests_per_day=1000)
FOLLOW_LIMITER = Limiter(requests_per_day=400)
RETWEET_LIMITER = Limiter(requests_per_day=1200)


class Api:
    def __init__(self, account_name: str, oauth_session: OAuth1ClientSession):
        """ Constructor for Api class.

        Args:
            oauth_session (obj: OAuth1ClientSession): OAuth session class with credentials.
        """

        logger: logging.Logger = logging.getLogger(__name__)
        self.logger = logging.LoggerAdapter(logger, extra={"account_name": account_name})
        self.oauth_session = oauth_session

    @SEARCH_LIMITER.acquire
    async def get_tweets(self, search_term: str) -> list[Tweet]:
        """ Get 50 tweets matching given `search_term`.

        API reference:
            https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets

        Args:
            search_term (str): Search for tweets containing this term.

        Return:
            list[obj: Tweet]: Tweet objects returned from API.
        """

        self.logger.info(f"Searching tweets [Search Term: {search_term}] ...")

        params = {
            "count": "50",
            "include_entities": "true",
            "result_type": "mixed",
            "tweet_mode": "extended",
        }

        data = {
            "q": search_term,
        }

        tweets: list[Tweet] = []
        try:
            async with self.oauth_session.get(URLS["search"], params=params, data=data) as response:
                response_json = {}
                try:
                    response_json: dict = await response.json()
                except ContentTypeError:
                    response_text: str = await response.text()
                    self.logger.error("ContentTypeError from response.")
                    self.logger.error(response_text)
                    self.logger.error(response)

                # if response.status >= 400:
                #     try:
                #         response_json: dict = await response.json()
                #         self.logger.error(response_json)
                #     except ContentTypeError as e:
                #         response_text: str = await response.text()
                #         self.logger.exception("ContentTypeError from response.")
                #         self.logger.exception(response_text)
                #         raise e

                response.raise_for_status()
                for tweet in response_json.get("statuses", []):

                    if tweet["in_reply_to_status_id"] is not None:
                        continue
                    if tweet["in_reply_to_user_id"] is not None:
                        continue
                    if tweet["in_reply_to_screen_name"] is not None:
                        continue

                    author = User(id=tweet["user"]["id"], screen_name=tweet["user"]["screen_name"])
                    mentions = [
                        User(id=mention["id"], screen_name=mention["screen_name"])
                        for mention in tweet["entities"]["user_mentions"]
                    ]
                    tweets.append(
                        Tweet(
                            id=tweet["id"],
                            created_at=tweet["created_at"],
                            text=tweet["full_text"],
                            author=author,
                            mentions=mentions,
                        ))
        except Exception as e:
            self.logger.exception("Unexpected exception [get_tweets]")
            raise e

        self.logger.info(f"Received [{len(tweets)}] Tweets!")
        return tweets

    @FAVORITE_LIMITER.acquire
    async def favorite_tweet(self, tweet_id: int):
        """ Favorite Tweet from given `tweet_id`.

        API Reference:
            https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-favorites-create

        Args:
            tweet_id (int): Id of Tweet to favorite.
        """

        params = {
            "id": str(tweet_id),
        }

        self.logger.info(f"Favoriting tweet [TweetId: {tweet_id}] ...")
        try:
            async with self.oauth_session.post(URLS["favorite_tweet"], params=params) as response:
                if response.status == 403:
                    response_json: dict = await response.json()
                    for error in response_json.get("errors", []):
                        message = error.get("message", None)
                        if message == "You have already favorited this status.":
                            self.logger.info(message)
                            return
                    self.logger.info(response_json)
                if response.status == 404:
                    self.logger.info("Tweet doesn't exist.")
                    return
                response.raise_for_status()
            self.logger.info("Tweet favorited!")
        except Exception as e:
            self.logger.exception("Unexpected exception [favorite_tweet]")
            raise e

    @FOLLOW_LIMITER.acquire
    async def follow_user(self, user: User):
        """ Follow User from given `user` object.

        API Reference:
            https://develper.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-create

        Args:
            user (obj: User): User to follow.
        """  # noqa: E501

        params = {
            "user_id": str(user.id),
        }

        self.logger.info(f"Following user [@{user.screen_name}] ...")
        try:
            async with self.oauth_session.post(URLS["follow_user"], params=params) as response:
                if response.status == 403:
                    response_json: dict = await response.json()
                    for error in response_json.get("errors", []):
                        code = error.get("code", -1)
                        message = error.get("message", None)
                        if message == "Cannot find specified user.":
                            self.logger.info(message)
                            return
                        # You've already requested to follow
                        if code == 160:
                            self.logger.info(message)
                            return
                    self.logger.info(response_json)
                response.raise_for_status()
            self.logger.info("User followed!")
        except Exception as e:
            self.logger.exception("Unexpected exception [follow_user]")
            raise e

    @RETWEET_LIMITER.acquire
    async def retweet(self, tweet_id: int):
        """ Retweet Tweet at given `tweet_id`.

        API Reference:
            https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-retweet-id

        Args:
            tweet_id (int): Tweet Id to retweet.
        """

        self.logger.info(f"Retweeting [TweetId: {tweet_id}] ...")
        try:
            async with self.oauth_session.post(URLS["retweet"].format(tweet_id)) as response:
                if response.status == 403:
                    response_json: dict = await response.json()
                    for error in response_json.get("errors", []):
                        message = error.get("message", None)
                        if message == "You have already retweeted this Tweet.":
                            self.logger.info(message)
                            return
                    self.logger.info(response_json)
                if response.status == 404:
                    self.logger.info("Tweet doesn't exist.")
                    return
                response.raise_for_status()
            self.logger.info("Tweet retweeted!")
        except Exception as e:
            self.logger.exception("Unexpected exception [retweet]")
            raise e

# DEMO METHODS
    async def tweet(self, text: str):
        """ TODO: docstring
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update
        """

        data = {
            "status": text,
        }

        print(f"Tweeting [Status: {text}] ...")
        async with self.oauth_session.post(URLS["tweet"], data=data) as response:
            if response.status in (401, 403):
                response_json: dict = await response.json()
                for error in response_json.get("errors", []):
                    message = error.get("message", None)
                    if message == "Status is a duplicate.":
                        print(message)
                        return
                print(response_json)
            response.raise_for_status()
        print("Tweet made!")

    async def get_tweet_by_id(self, id: int):
        """ TODO: docstring
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update
        """

        params = {
            "include_entities": "true",
        }

        data = {
            "id": str(id),
        }

        async with self.oauth_session.get(URLS["lookup"], params=params, data=data) as response:
            response_json: dict = await response.json()
            pprint(response_json)
            response.raise_for_status()
