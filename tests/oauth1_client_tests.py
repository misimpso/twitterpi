import aiohttp
import unittest

from twitterpi.oauth1_client import OAuth1ClientSession
from unittest.mock import Mock, patch


KEY_RING = {
    "consumer_key": "xvz1evFS4wEEPTGEFPHBog",
    "consumer_secret": "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw",
    "access_token": "370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb",
    "access_token_secret": "LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE",
}

class OAuth1ClientTests(unittest.TestCase):

    patch.object(aiohttp.ClientSession, "__init__")
    def setUp(self):
        self.oauth1client = OAuth1ClientSession(**KEY_RING)