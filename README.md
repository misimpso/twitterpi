# twitter_pi
Twitter Pi

For each account:
    Search for latest tweets matching criteria.
        - Save returned tweets to memory for easy reference.
        - Refresh tweets in memory if data is old.
    Interact with a lastest tweet at random.
        - RT / Like / Follow, etc
        - Move tweet id from todo dataset to done.
        - Sleep for random period of time.

Each request needs to be wrapped in a rate limit checker, and bearer token refresher.
