import asyncio
import random

from time import time
from twitterpi.api import Api
from twitterpi.cache import Cache
from twitterpi.dto import Directive, Tweet, User
from typing import Optional


SLEEP_AMOUNTS = list(range(15, 30, 2))


async def random_sleep():
    """ TODO: docstring
    """
    plus_minus = 1 + random.random()
    if int(time()) % 2 == 0:
        plus_minus *= -1
    sleep_amount = random.choice(SLEEP_AMOUNTS) + plus_minus
    print(f"zZz Sleeping for [{sleep_amount:.2f}] seconds zZz")
    await asyncio.sleep(sleep_amount)


class Account:
    normal_comments: list[str] = None
    tagged_comments: list[str] = None

    def __init__(self, screen_name: str, api: Api, cache: Cache):
        """ TODO: docstring
        """

        self.screen_name: str = screen_name
        self.api = api
        self.cache = cache
    
    async def start(self):
        """ TODO: docstring
        """

        # search_terms = ['#win OR #giveaway', 'csgogiveaway']

        # last_latest_tweet_id = None
        # tweet_ids: set[int] = set()
        # tweet_queue: list[Tweet] = []

        while True:
            tweet: Tweet = await self.get_tweet()
            await self.interact(tweet)
            await self.remove_seen_tweet(tweet)
            await random_sleep()
    
    async def parse(self, tweet_text: str) -> Directive:
        """ TODO: docstring
        """

        directive = Directive()
        tweet_text = tweet_text.lower()

        for keyword in ("rt", "retweet", "re-tweet"):
            if keyword in tweet_text:
                directive.retweet = True
                break
        
        for keyword in ("favorite", "favourite", "fav", "like"):
            if keyword in tweet_text:
                directive.favorite = True
                break
        
        for keyword in ("flw", "follow"):
            if keyword in tweet_text:
                directive.follow = True
                break

        directive.tag = ("tag" in tweet_text)
        directive.comment = ("comment" in tweet_text)

        return directive
    
    async def interact(self, tweet: Tweet):
        """ TODO: docstring
        """

        actions: list[tuple] = []
        directive: Directive = await self.parse(tweet.text)

        print(f"Interacting with tweet ... [@{tweet.author.screen_name} {tweet.text[:20]}{' ...' if len(tweet.text) > 20 else ''} || {directive}]")
        
        if directive.retweet:
            actions.append((self.api.retweet, {"tweet_id": tweet.id}))

        if directive.favorite:
            actions.append((self.api.favorite_tweet, {"tweet_id": tweet.id}))

        if directive.follow:
            actions.append((self.follow_user, {"user": tweet.author}))
            for mention in tweet.mentions:
                actions.append((self.follow_user, {"user": mention}))

        if directive.tag:           
            actions.append((self.tagged_comment, {"tweet": tweet}))

        elif directive.comment:
            normal_comment: str = random.choice(self.normal_comments)
            normal_comment = f"@{tweet.author.screen_name} {normal_comment}"
            actions.append((self.api.comment, {"tweet_id": tweet.id, "text": normal_comment}))

        if not actions:
            print("Nothing to act upon.")
            return

        random.shuffle(actions)
        
        for action in actions:
            endpoint, kwargs = action
            await endpoint(**kwargs)
            await random_sleep()
        
        print("Tweet interacted!")

    async def get_tweet(self) -> Optional[Tweet]:
        """ TODO: docstring
        """

        # Get tweet from database
        tweet: Tweet = await self.cache.get_tweet()

        if not tweet:
            # Get tweets from API and insert into database
            search_terms = ['#win OR #giveaway', 'csgogiveaway']
            for search_term in search_terms:
                new_tweets: list[Tweet] = await self.api.get_tweets(search_term)
                await self.cache.insert_tweets(tweets=new_tweets)
            tweet: Tweet = await self.cache.get_tweet()
        return tweet
    
    async def tagged_comment(self, tweet: Tweet):
        """ TODO: docstring
        """

        random_amount: int = random.randint(1, 3)
        rand_followers: list[User] = await self.cache.get_random_followers(n=random_amount)

        if not rand_followers:
            followers: list[User] = await self.api.get_followers(self.screen_name)
            await self.cache.insert_followers(followers=followers)
            rand_followers: list[User] = await self.cache.get_random_followers(n=random_amount)
        
        follower_string = " ".join([f".@{follower.screen_name}"for follower in rand_followers])
        tagged_comment: str = random.choice(self.tagged_comments)
        tagged_comment = tagged_comment.format(follower_string)

        await self.api.comment(tweet_id=tweet.id, text=tagged_comment)
    
    async def follow_user(self, user: User):
        """ TODO: docstring
        """

        await self.api.follow_user(user_id=user.id)
        await self.cache.insert_followers([user])
    
    async def remove_seen_tweet(self, tweet: Tweet):
        """ TODO: docstring
        """

        await self.cache.remove_tweet(tweet)
