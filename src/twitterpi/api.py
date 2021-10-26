from pyrate_limiter import Duration, Limiter, RequestRate
from twitterpi.dto import Tweet, User
from twitterpi.oauth1_client import OAuth1ClientSession
from typing import Optional


BASE_URL = "https://api.twitter.com/1.1/"
URLS = {
    "favorite_tweet": f"{BASE_URL}favorites/create.json",
    "follow_user": f"{BASE_URL}friendships/create.json",
    "get_followers": f"{BASE_URL}followers/list.json",
    "retweet": f"{BASE_URL}statuses/retweet/{{}}.json",
    "search": f"{BASE_URL}search/tweets.json",
    "tweet": f"{BASE_URL}statuses/update.json",
}

SEARCH_LIMITER = Limiter(RequestRate(180, Duration.MINUTE * 15))
STATUS_LIMITER = Limiter(RequestRate(300, Duration.HOUR * 3))
FAVORITE_TWEET_LIMITER = Limiter(RequestRate(1000, Duration.DAY))
FOLLOW_TWEET_LIMITER = Limiter(RequestRate(400, Duration.DAY))
GET_FOLLOWERS_LIMITER = Limiter(RequestRate(15, Duration.MINUTE * 15))


class Api:
    def __init__(
            self,
            consumer_key: str,
            consumer_secret: str,
            access_token: str,
            access_token_secret: str):
        """ TODO: docstring
        """

        self.key_ring = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "access_token": access_token,
            "access_token_secret": access_token_secret,
        }

    @SEARCH_LIMITER.ratelimit("search", delay=True)
    async def get_tweets(self, search_term: str, last_latest_tweet_id: Optional[int] = None) -> list[Tweet]:
        """ TODO: docstring
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets
        """
        print(f"Searching tweets [Search Term: {search_term}] ...")

        params = {
            "count": 50,
            "include_entities": True,
            "q": search_term,
            "result_type": "mixed",
            "tweet_mode": "extended",
        }

        if last_latest_tweet_id is not None:
            params["since_id"] = last_latest_tweet_id

        tweets: list[Tweet] = []
        async with OAuth1ClientSession(**self.key_ring) as session:
            async with session.get(URLS["search"], params=params) as response:
                response.raise_for_status()
                response_json = await response.json()
                for tweet in response_json["statuses"]:
                    author = User(id=tweet["user"]["id"], screen_name=tweet["user"]["screen_name"])
                    mentions = [User(id=u["id"], screen_name=u["screen_name"]) for u in tweet["entities"]["user_mentions"]]
                    tweets.append(
                        Tweet(
                            id=tweet["id"],
                            created_at=tweet["created_at"],
                            text=tweet["full_text"],
                            author=author,
                            mentions=mentions,
                        ))

        print(f"Received [{len(tweets)}] Tweets!")
        return tweets
    
    @FAVORITE_TWEET_LIMITER.ratelimit("favorite_tweet", delay=True)
    async def favorite_tweet(self, tweet_id: int):
        """ TODO: docstring
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-favorites-create
        """

        params = {
            "id": tweet_id
        }

        print(f"Favoriting tweet [TweetId: {tweet_id}] ...")
        async with OAuth1ClientSession(**self.key_ring) as session:
            async with session.post(URLS["favorite_tweet"], params=params) as response:
                if response.status == 403:
                    message = await response.text()
                    if message == "You have already favorited this status.":
                        print(message)
                        return
                response.raise_for_status()
        print("Tweet favorited!")
    
    @FOLLOW_TWEET_LIMITER.ratelimit("follow_user", delay=True)
    async def follow_user(self, user_id: int):
        """ TODO: docstring
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-create
        """

        params = {
            "user_id": user_id
        }

        print(f"Following user [UserId: {user_id}] ...")
        async with OAuth1ClientSession(**self.key_ring) as session:
            async with session.post(URLS["follow_user"], params=params) as response:
                if response.status == 403:
                    json = await response.json()
                    print(json)
                response.raise_for_status()
        print("User followed!")

    @STATUS_LIMITER.ratelimit("retweet", delay=True)
    async def retweet(self, tweet_id: int):
        """ TODO: docstring
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-retweet-id
        """

        print(f"Retweeting [TweetId: {tweet_id}] ...")
        async with OAuth1ClientSession(**self.key_ring) as session:
            async with session.post(URLS["retweet"].format(tweet_id)) as response:
                if response.status == 403:
                    response_json: dict = await response.json()
                    for error in response_json.get("errors", []):
                        message = error.get("message", None)
                        if message == "You have already retweeted this Tweet.":
                            print(message)
                            return
                    print(response_json)
                response.raise_for_status()
        print("Tweet retweeted!")
        
    @STATUS_LIMITER.ratelimit("comment", delay=True)
    async def comment(self, tweet_id: int, text: str):
        """ TODO: docstring
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update
        """

        params = {
            "in_reply_to_status_id": tweet_id,
            "status": text,
        }

        print(f"Commenting [TweetId: {tweet_id}] ...")
        async with OAuth1ClientSession(**self.key_ring) as session:
            async with session.post(URLS["tweet"], params=params) as response:
                if response.status >= 400:
                    response_json = await response.json()
                    print(response_json)
                response.raise_for_status()
        print("Tweet commented on!")

    @GET_FOLLOWERS_LIMITER.ratelimit("get_followers", delay=True)
    async def get_followers(self, screen_name: str) -> list[User]:
        """ TODO: docstring
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-list
        """

        params = {
            "screen_name": screen_name,
            "count": 100,
            "skip_status": True,
        }

        followers: list[User] = []
        print(f"Getting followers ... [Screen Name: {screen_name}]")
        async with OAuth1ClientSession(**self.key_ring) as session:
            async with session.get(URLS["get_followers"], params=params) as response:
                response_json = await response.json()
                if response.status >= 400:
                    print(response_json)
                response.raise_for_status()
                for user in response_json["users"]:
                    followers.append(User(id=user["id"], screen_name=user["screen_name"]))
        
        print(f"Got [{len(followers)}] Followers!")
        return followers
