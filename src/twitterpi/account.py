import logging
import random

from asyncio import sleep
from time import time
from twitterpi.api import Api
from twitterpi.cache import Cache
from twitterpi.dto import Directive, Tweet, User
from typing import Optional


SLEEP_AMOUNTS = list(range(15, 30, 2))


class Account:
    normal_comments: list[str] = None
    tagged_comments: list[str] = None

    def __init__(self, screen_name: str, api: Api, cache: Cache):
        """ TODO: docstring
        """

        self.logger = logging.getLogger(screen_name)
        self.screen_name: str = screen_name
        self.api = api
        self.cache = cache
    
    async def start(self):
        """ TODO: docstring
        """

        while True:
            tweet: Tweet = await self.get_tweet()

            if not await self.cache.check_tweet_seen(tweet):
                await self.interact(tweet)
            else:
                self.logger.info("Tweet already seen.")

            await self.cache.remove_new_tweet(tweet)
            await self.cache.insert_seen_tweet(tweet)

            await sleep(5.0)
    
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

        return directive
    
    async def interact(self, tweet: Tweet):
        """ TODO: docstring
        """

        actions: list[tuple] = []
        directive: Directive = await self.parse(tweet.text)

        self.logger.info(f"Interacting with Tweet [https://twitter.com/{tweet.author.screen_name}/status/{tweet.id}]")        
        for line in tweet.text.split("\n"):
            self.logger.info(f" │ {line}")
        self.logger.info(f" └─────── {directive}")
        
        if directive.retweet:
            actions.append((self.api.retweet, {"tweet_id": tweet.id}))

        if directive.favorite:
            actions.append((self.api.favorite_tweet, {"tweet_id": tweet.id}))

        if directive.follow:
            actions.append((self.follow_user, {"user": tweet.author}))
            for mention in tweet.mentions:
                actions.append((self.follow_user, {"user": mention}))

        if not actions:
            self.logger.info("Nothing to act upon.")
            return
        
        if directive.retweet and not (directive.favorite or directive.follow):
            self.logger.info("Not enough directives to act upon.")
            return

        random.shuffle(actions)
        
        for action in actions:
            endpoint, kwargs = action
            await endpoint(**kwargs)
        
        self.logger.info("Tweet interacted!")

    async def get_tweet(self) -> Optional[Tweet]:
        """ TODO: docstring
        """

        # Get tweet from database
        tweet: Tweet = await self.cache.get_tweet()

        if not tweet:
            # Get tweets from API and insert into database
            search_terms = [
                '#win OR #giveaway -filter:retweets -filter:replies',
                '#csgogiveaway -filter:retweets -filter:replies'
            ]

            for search_term in search_terms:
                new_tweets: list[Tweet] = await self.api.get_tweets(search_term)
                await self.cache.insert_new_tweets(tweets=new_tweets)
                await self.random_sleep()

            tweet: Tweet = await self.cache.get_tweet()
        return tweet

    async def follow_user(self, user: User):
        """ TODO: docstring
        """

        await self.api.follow_user(user_id=user.id)
