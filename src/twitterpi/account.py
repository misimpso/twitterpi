import asyncio
import random

from heapq import heapify, heappop
from twitterpi.actions import Actions
from twitterpi.dto.directive import Directive
from twitterpi.dto.tweet import Tweet


class Account(Actions):
    def __init__(self, name: str, consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str):
        self.name = name
        super().__init__(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )
    
    async def start(self):
        """ TODO: docstring
        """

        search_terms = ['#win OR #giveaway', 'csgogiveaway']

        last_latest_tweet_id = None
        tweet_ids: set[int] = set()
        tweet_queue: list[Tweet] = []

        while True:

            # Search for new tweets and add them to the queue
            if len(tweet_queue) == 0:
                for search_term in search_terms:
                    new_tweets: list[Tweet] = await self.search(search_term, last_latest_tweet_id)
                    for new_tweet in new_tweets:
                        if new_tweet.id not in tweet_ids:
                            tweet_queue.append(new_tweet)
                            tweet_ids.add(new_tweet.id)
                heapify(tweet_queue)
                last_latest_tweet_id = tweet_queue[-1].created_at
            
            # Get tweet
            tweet: Tweet = heappop(tweet_queue)
            tweet_ids.remove(tweet.id)

            # Parse / Interact
            directive: Directive = self.parse(tweet.text)
            await self.interact(directive, tweet)

            # Sleep
            print("Sleeping for [10] seconds.")
            await asyncio.sleep(10)
    
    def parse(self, tweet_text: str) -> Directive:
        """ TODO: docstring
        """

        directive = Directive()
        tweet_text = tweet_text.lower()

        for keyword in ("rt", "retweet", "re-tweet"):
            if keyword in tweet_text:
                directive.retweet = True
                break
        
        for keyword in ("favorite", "fav", "like"):
            if keyword in tweet_text:
                directive.favorite = True
                break
        
        directive.follow = ("follow" in tweet_text)
        directive.tag = ("tag" in tweet_text)
        directive.comment = ("comment" in tweet_text)

        return directive
    
    async def interact(self, directive: Directive, tweet: Tweet):
        """ TODO: docstring
        """

        print(f"Interacting with tweet ... [{tweet.id}, {directive}]")
        actions = []
        if directive.retweet:
            actions.append(("retweet", {"tweet_id": tweet.id}))

        if directive.favorite:
            actions.append(("favorite", {"tweet_id": tweet.id}))

        if directive.follow:
            actions.append(("follow", {"user_id": tweet.author.id}))
            for user in tweet.mentions:
                actions.append(("follow", {"user_id": user.id}))

        if directive.tag:
            actions.append(("tag", {"tweet_id": tweet.id}))
        elif directive.comment:
            actions.append(("comment", {"tweet_id": tweet.id}))

        random.shuffle(actions)
        sleep_amounts = [5.2, 6.7, 9.8, 10.4, 12.3, 15.7]
        plus_minus = 1 + random.random()

        for i, action in enumerate(actions):
            sleep_amount = random.choice(sleep_amounts)
            sleep_amount += plus_minus * [-1, 1][i % 2 == 0]
            print(f"Sleeping for [{sleep_amount}] seconds ...")
            await asyncio.sleep(sleep_amount)

            endpoint, kwargs = action

            await getattr(self, endpoint)(**kwargs)
        
        print("Tweet interacted!")
