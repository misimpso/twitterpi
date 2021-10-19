from pyrate_limiter import Duration, Limiter, RequestRate
from twitterpi.dto import tweet
from twitterpi.dto.tweet import Tweet
from twitterpi.dto.user import User
from twitterpi.oauth1_client import OAuth1ClientSession
from typing import Optional


BASE_URL = "https://api.twitter.com/1.1/"
URLS = {
    "favorite": f"{BASE_URL}favorites/create.json",
    "follow": f"{BASE_URL}friendships/create.json",
    "retweet": f"{BASE_URL}statuses/retweet/{{}}.json",
    "search": f"{BASE_URL}search/tweets.json",
    "tweet": f"{BASE_URL}statuses/update.json",
}

SEARCH_LIMITER = Limiter(RequestRate(180, Duration.MINUTE * 15))
STATUS_LIMITER = Limiter(RequestRate(300, Duration.HOUR * 3))
FAVORITE_LIMITER = Limiter(RequestRate(1000, Duration.DAY))
FOLLOW_LIMITER = Limiter(RequestRate(400, Duration.DAY))


class Actions:
    def __init__(self, consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str):
        self.key_ring = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "access_token": access_token,
            "access_token_secret": access_token_secret,
        }

    @SEARCH_LIMITER.ratelimit("search", delay=True)
    async def search(self, search_term: str, last_latest_tweet_id: Optional[int]) -> list[Tweet]:
        """ TODO: docstring
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets
        """
        print(f"Searching tweets [Search Term: {search_term}] ...")

        params = {
            "count": 50,
            "include_entities": True,
            "q": search_term,
            "result_type": "mixed",
        }

        if last_latest_tweet_id is not None:
            params["since_id"] = last_latest_tweet_id

        tweets = []
        async with OAuth1ClientSession(**self.key_ring) as session:
            async with session.get(URLS["search"], params=params) as response:
                response.raise_for_status()
                response_json = await response.json()
                for tweet in response_json["statuses"]:
                    author = User(id=tweet["user"]["id"], name=tweet["user"]["name"])
                    mentions = [
                        User(id=u["id"], name=u["name"])
                        for u in tweet["entities"]["user_mentions"]
                    ]
                    tweets.append(
                        Tweet(
                            id=tweet["id"],
                            created_at=tweet["created_at"],
                            text=tweet["text"],
                            author=author,
                            mentions=mentions,
                        ))

        print(f"Received [{len(tweets)}] Tweets!")
        return tweets
    
    @FAVORITE_LIMITER.ratelimit("favorite", delay=True)
    async def favorite(self, tweet_id: int):
        """ TODO: docstring
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-favorites-create
        """

        params = {
            "id": tweet_id
        }

        print(f"Favoriting tweet [TweetId: {tweet_id}] ...")
        async with OAuth1ClientSession(**self.key_ring) as session:
            async with session.post(URLS["favorite"], params=params) as response:
                if response.status == 403:
                    message = await response.text()
                    if message == "You have already favorited this status.":
                        return
                response.raise_for_status()
        print("Tweet favorited!")
    
    @FOLLOW_LIMITER.ratelimit("follow", delay=True)
    async def follow(self, user_id: int):
        """ TODO: docstring
        """

        params = {
            "user_id": user_id
        }

        print(f"Following user [UserId: {user_id}] ...")
        async with OAuth1ClientSession(**self.key_ring) as session:
            async with session.post(URLS["follow"], params=params) as response:
                if response.status == 403:
                    json = await response.json()
                    print(json)
                response.raise_for_status()
        print("User followed!")

    @STATUS_LIMITER.ratelimit("retweet", delay=True)
    async def retweet(self, tweet_id: int):
        """ TODO: docstring
        """

        print(f"Retweeting [TweetId: {tweet_id}] ...")
        async with OAuth1ClientSession(**self.key_ring) as session:
            async with session.post(URLS["retweet"].format(tweet_id)) as response:
                if response.status == 403:
                    message = await response.text()
                    if message == "You have already retweeted this Tweet.":
                        return
                response.raise_for_status()
        print("Tweet retweeted!")
    
    @STATUS_LIMITER.ratelimit("tag", delay=True)
    async def tag(self, tweet_id: int):
        """ TODO: docstring
        """

        params = {
            "in_reply_to_status_id": tweet_id
        }

        print(f"Commenting with tags [TweetId: {tweet_id}] ...")
        async with OAuth1ClientSession(**self.key_ring) as session:
            async with session.post(URLS["tweet"], params=params) as response:
                response.raise_for_status()
        print("Tweet commented on with tags!")
    
    @STATUS_LIMITER.ratelimit("comment", delay=True)
    async def comment(self, tweet_id: int):
        """ TODO: docstring
        """

        params = {
            "in_reply_to_status_id": tweet_id
        }

        print(f"Commenting [TweetId: {tweet_id}] ...")
        async with OAuth1ClientSession(**self.key_ring) as session:
            async with session.post(URLS["tweet"], params=params) as response:
                response.raise_for_status()
        print("Tweet commented on!")

