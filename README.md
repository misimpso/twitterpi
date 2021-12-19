# twitterpi
Asynchronous, multi-user Twitter Giveaway Bot.

[![Tests](https://github.com/misimpso/twitterpi/actions/workflows/test.yml/badge.svg)](https://github.com/misimpso/twitterpi/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/misimpso/twitterpi/branch/main/graph/badge.svg?token=0KKPHCSYTJ)](https://codecov.io/gh/misimpso/twitterpi)

## Description
Python application for interacting with TwitterAPI to operate multiple giveaway bots at once. Account credentials and settings are read from a `credential.toml` and `settings.toml` files respectively. Tweets matching search criteria are saved to and read from disk. Requests use custom async OAuth 1.0 session and custom rate limiter.

## Usage
``` shell
$ twitterpi --help
usage: twitterpi [-h] [-c CREDS_PATH] [-s SETTINGS_PATH] [-o LOG_PATH] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

Twitter Giveaway Bot

optional arguments:
  -h, --help            show this help message and exit
  -c CREDS_PATH, --creds-path CREDS_PATH
                        Path to account credentials file. (default: /path/to/site-packages/twitterpi/conf/credentials.toml)
  -s SETTINGS_PATH, --settings-path SETTINGS_PATH
                        Path to account settings file. (default: /path/to/site-packages/twitterpi/conf/settings.toml)
  -o LOG_PATH, --log-path LOG_PATH
                        Path to output log file. (default: /path/to/site-packages/twitterpi/logs/twitterpi.log)
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Desired log level. (default: INFO)
```

## Pre-requisites
You'll need access to the [Twitter API](https://developer.twitter.com/en/products/twitter-api), and an environment running Python >3.6.

Edit the `/path/to/site-packages/twitterpi/conf/credentials.toml.sample` with your API consumer / API keys, e.g:
``` toml
[YourAccountName]
consumer_key = "XXXXXXXXXXXXXXXXXXXXXXXXX"
consumer_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
access_token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
access_token_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```
You can add multiple accounts to this credentials file. When populated, remove `.sample` suffix.

Make sure you set the birthdate of your account or your follow requests will fail on certain age-restricted users (e.g. alcohol brands).
