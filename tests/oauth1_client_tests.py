import aiohttp
import string
import unittest

from hashlib import sha1
from hmac import HMAC
from twitterpi.oauth1_client import OAuth1ClientSession
from unittest.mock import Mock, patch


ALPHA_NUM = set(string.ascii_letters + string.digits)

# Values from Twitter example
# https://developer.twitter.com/en/docs/authentication/oauth-1-0a/creating-a-signature
KEY_RING = {
    "consumer_key": "xvz1evFS4wEEPTGEFPHBog",
    "consumer_secret": "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw",
    "access_token": "370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb",
    "access_token_secret": "LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE",
}
METHOD = "POST"
URL = "https://api.twitter.com/1.1/statuses/update.json"
REQUEST_PARAMS = {"include_entities": True, "status": "Hello Ladies + Gentlemen, a signed OAuth request!"}
PARAMETER_STRING = (
    "include_entities=true&"
    "oauth_consumer_key=xvz1evFS4wEEPTGEFPHBog&"
    "oauth_nonce=kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg&"
    "oauth_signature_method=HMAC-SHA1&"
    "oauth_timestamp=1318622958&"
    "oauth_token=370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb&"
    "oauth_version=1.0&"
    "status=Hello%20Ladies%20%2B%20Gentlemen%2C%20a%20signed%20OAuth%20request%21"
)
SIGNATURE_BASE_STRING = (
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
SIGNING_KEY = b"kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw&LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE"
SIGNATURE = "hCtSmYh+iHYCEqBWrE7C7hYmtUk="
AUTH_HEADER = (
    'OAuth oauth_consumer_key="xvz1evFS4wEEPTGEFPHBog", '
    'oauth_nonce="kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg", '
    'oauth_signature="hCtSmYh%2BiHYCEqBWrE7C7hYmtUk%3D", '
    'oauth_signature_method="HMAC-SHA1", '
    'oauth_timestamp="1318622958", '
    'oauth_token="370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb", '
    'oauth_version="1.0"'
)


class OAuth1ClientTests(unittest.IsolatedAsyncioTestCase):

    @patch.object(aiohttp, "ClientSession", Mock(spec=aiohttp.ClientSession))
    @patch("twitterpi.oauth1_client.time")
    async def test___generate_auth_header__verify_return_value(self, mock_time: Mock):
        """ Verify `__generate_auth_header` returns expected auth header string.
        """

        nonce = "kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg"
        timestamp = 1318622958
        mock_time.return_value = timestamp
        async with OAuth1ClientSession(**KEY_RING) as session:
            session._OAuth1ClientSession__generate_nonce = Mock(return_value=nonce)
            session._OAuth1ClientSession__generate_signature = Mock(return_value=SIGNATURE)
            actual_auth_header = session._OAuth1ClientSession__generate_auth_header(METHOD, URL, REQUEST_PARAMS)
    
        self.assertEqual(actual_auth_header, AUTH_HEADER)
    
    @patch.object(aiohttp, "ClientSession", Mock(spec=aiohttp.ClientSession))
    async def test___generate_signature__verify_return_value(self):
        """ Verify `__generate_signature` returns expected signature string.
        """

        oauth_params = {
            "oauth_consumer_key": KEY_RING["consumer_key"],
            "oauth_nonce": "kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg",
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": "1318622958",
            "oauth_token": KEY_RING["access_token"],
            "oauth_version": "1.0",
        }

        async with OAuth1ClientSession(**KEY_RING) as session:
            session._OAuth1ClientSession__create_parameter_string = Mock(return_value=PARAMETER_STRING)
            session._OAuth1ClientSession__create_signature_base_string = Mock(return_value=SIGNATURE_BASE_STRING)
            actual_signature = session._OAuth1ClientSession__generate_signature(METHOD, URL, oauth_params, REQUEST_PARAMS)
        
        self.assertEqual(actual_signature, SIGNATURE)
    
    @patch.object(aiohttp, "ClientSession", Mock(spec=aiohttp.ClientSession))
    @patch("twitterpi.oauth1_client.b2a_base64")
    @patch("twitterpi.oauth1_client.HMAC")
    async def test___generate_signature__verify_methods_called_with_expected_arguments(self, mock_hmac: Mock, mock_b64: Mock):
        """ Verify `__generate_signature` calls methods with expected arguments.
        """

        mock_hmac.mock_add_spec(HMAC, spec_set=True)
        mock_hmac_obj = mock_hmac.return_value

        oauth_params = {
            "oauth_consumer_key": KEY_RING["consumer_key"],
            "oauth_nonce": "kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg",
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": "1318622958",
            "oauth_token": KEY_RING["access_token"],
            "oauth_version": "1.0",
        }

        expected_signing_key = "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw&LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE"

        async with OAuth1ClientSession(**KEY_RING) as session:
            session._OAuth1ClientSession__create_parameter_string = Mock(return_value=PARAMETER_STRING)
            session._OAuth1ClientSession__create_signature_base_string = Mock(return_value=SIGNATURE_BASE_STRING)
            session._OAuth1ClientSession__generate_signature(METHOD, URL, oauth_params, REQUEST_PARAMS)
        
            mock_hmac.assert_called_once_with(key=expected_signing_key.encode(), msg=SIGNATURE_BASE_STRING.encode(), digestmod=sha1)
            mock_b64.assert_called_once_with(mock_hmac_obj.digest(), newline=False)
    
    @patch.object(aiohttp, "ClientSession", Mock(spec=aiohttp.ClientSession))
    async def test___create_parameter_string__verify_return_value(self):
        """ Verify `__create_parameter_string` returns expected parameter string.
        """

        oauth_params = {
            "oauth_consumer_key": KEY_RING["consumer_key"],
            "oauth_nonce": "kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg",
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": 1318622958,
            "oauth_token": KEY_RING["access_token"],
            "oauth_version": 1.0,
        }

        async with OAuth1ClientSession(**KEY_RING) as session:
            actual_parameter_string = session._OAuth1ClientSession__create_parameter_string(oauth_params, REQUEST_PARAMS)

        self.assertEqual(actual_parameter_string, PARAMETER_STRING)

    @patch.object(aiohttp, "ClientSession", Mock(spec=aiohttp.ClientSession))
    async def test___create_signature_base_string__verify_return_value(self):
        """ Verify `__create_signature_base_string` returns expected signature base string.
        """

        async with OAuth1ClientSession(**KEY_RING) as session:
            actual_signature_base_string = session._OAuth1ClientSession__create_signature_base_string(METHOD, URL, PARAMETER_STRING)

        self.assertEqual(actual_signature_base_string, SIGNATURE_BASE_STRING)

    @patch.object(aiohttp, "ClientSession", Mock(spec=aiohttp.ClientSession))
    async def test___generate_nonce__verify_return_value(self):
        """ Verify `__generate_nonce` generates 32 cchar long, alpha-numeric strings.
        """

        required_nonce_length = 32
        async with OAuth1ClientSession(**KEY_RING) as session:
            for _ in range(10):
                nonce = session._OAuth1ClientSession__generate_nonce()
                self.assertEqual(len(nonce), required_nonce_length)
                for c in nonce:
                    if c not in ALPHA_NUM:
                        self.fail(f"Generated nonce is not strictly alpha-numeric. [{nonce}]")


if __name__ == "__main__":
    unittest.main()
