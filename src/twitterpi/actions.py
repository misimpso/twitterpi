from twitterpi.oauth1_client import OAuth1ClientSession
from twitterpi.dto import Tweet, User
from typing import Optional


BASE_URL = "https://api.twitter.com/1.1/"
URLS = {
    "favorite": f"{BASE_URL}favorites/create.json",
    "follow": f"{BASE_URL}friendships/create.json",
    "retweet": f"{BASE_URL}statuses/retweet/:{{}}.json",
    "search_posts": f"{BASE_URL}search/tweets.json",
    "tweet": f"{BASE_URL}statuses/update.json",
}


class Actions:
    def __init__(self, consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str):
        self.key_ring = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "access_token": access_token,
            "access_token_secret": access_token_secret,
        }

    # def _check_bearer(func: Callable) -> Callable:
    #     """ TODO: docstring
    #     """
    #     async def wrapper(*args, **kwargs):
    #         this = args[0]
    #         if this.bearer_token is None:
    #             await this.get_bearer()
    #         result = await func(*args, **kwargs)
    #         return result
    #     return wrapper
    
    # async def get_bearer(self):
    #     """ TODO: docstring
    #     https://developer.twitter.com/en/docs/authentication/api-reference/token
    #     """
    #     auth = aiohttp.BasicAuth(login=self.consumer_key, password=self.consumer_secret)
    #     params = {"grant_type": "client_credentials"}
    #     async with aiohttp.ClientSession() as session:
    #         print(session.headers)
    #         async with session.post(URLS["token"], auth=auth, params=params) as response:
    #             response.raise_for_status()
    #             response_json = await response.json()
    #             self.bearer_token = response_json["access_token"]

    async def search(self, search_term: str, last_latest_tweet_id: Optional[int]) -> list[Tweet]:
        """ TODO: docstring
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets
        """

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
            async with session.get(URLS["search_posts"], params=params) as response:
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
        return tweets
