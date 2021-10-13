# twitter_pi
Async, multi-user Twitter Giveaway Bot for running on Raspberry Pi

## Description

## Pre-requisites
You'll need access to the [Twitter API](https://developer.twitter.com/en/products/twitter-api), and an environment running Python >3.6.

Edit the `conf/test_credentials.toml` with your API consumer / API keys, e.g:
``` toml
[YourAccountName]
consumer_key = "XXXXXXXXXXXXXXXXXXXXXXXXX"
consumer_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
access_token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
access_token_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```
You can add multiple accounts to this credentials file.

## Process
- For each account:
    - Search for latest tweets matching criteria.
        - Save returned tweets to memory for easy reference.
        - Refresh tweets in memory if data is old.
    - Interact with a lastest tweet at random.
        - RT / Like / Follow, etc
        - Move tweet id from todo dataset to done.
        - Sleep for random period of time.

Each request needs to be wrapped in a rate limit checker, and bearer token refresher.
