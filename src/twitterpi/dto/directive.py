from dataclasses import dataclass


@dataclass
class Directive:
    retweet: bool = False
    favorite: bool = False
    follow: bool = False

    def parse_tweet(cls, tweet_text: str):
        """ Set class variables based on keywords present in given `tweet_text`.

        Args:
            tweet_text (str): String of tweet text.
        """

        tweet_text = tweet_text.lower()

        for keyword in ("rt", "retweet", "re-tweet"):
            if keyword in tweet_text:
                cls.retweet = True
                break

        for keyword in ("favorite", "favourite", "fav", "like"):
            if keyword in tweet_text:
                cls.favorite = True
                break

        for keyword in ("flw", "follow"):
            if keyword in tweet_text:
                cls.follow = True
                break
