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

class OAuth1ClientTests(unittest.IsolatedAsyncioTestCase):
    @patch.object(aiohttp, "ClientSession", Mock(spec=aiohttp.ClientSession))
    async def test___create_signature_base_string__verify_return_value(self):
        method = "post"
        url = "https://api.twitter.com/1.1/statuses/update.json"
        parameter_string = (
            "include_entities=true&"
            "oauth_consumer_key=xvz1evFS4wEEPTGEFPHBog&"
            "oauth_nonce=kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg&"
            "oauth_signature_method=HMAC-SHA1&"
            "oauth_timestamp=1318622958&"
            "oauth_token=370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb&"
            "oauth_version=1.0&"
            "status=Hello%20Ladies%20%2B%20Gentlemen%2C%20a%20signed%20OAuth%20request%21"
        )

        expected_signature_base_string = (
            "POST&"
            "https%3A%2F%2Fapi.twitter.com%2F1.1%2Fstatuses%2Fupdate.json&"
            "include_entities%3Dtrue%26"
            "oauth_consumer_key%3Dxvz1evFS4wEEPTGEFPHBog%26"
            "oauth_nonce%3DkYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg%26"
            "oauth_signature_method%3DHMAC-SHA1%26"
            "oauth_timestamp%3D1318622958%26"
            "oauth_token%3D370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb%26"
            "oauth_version%3D1.0%26"
            "status%3DHello%2520Ladies%2520%252B%2520Gentlemen%252C%2520a%2520signed%2520OAuth%2520request%2521"
        )

        async with OAuth1ClientSession(**KEY_RING) as session:
            actual_signature_base_string = session._OAuth1ClientSession__create_signature_base_string(
                method, url, parameter_string)

        self.assertEqual(actual_signature_base_string, expected_signature_base_string)

if __name__ == "__main__":
    unittest.main()
