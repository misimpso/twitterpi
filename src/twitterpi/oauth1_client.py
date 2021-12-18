import random
import string
import urllib

from aiohttp import ClientSession
from contextlib import asynccontextmanager
from binascii import b2a_base64
from hashlib import sha1
from hmac import HMAC
from time import time
from typing import Optional


ALPHA_NUM: list[str] = list(string.ascii_letters + string.digits)


def prcnt_encd(s: str) -> str:
    """ Percent encode given string `s`.

    Characters not in set `[A-Za-z0-9-._~]` will be converted to their ascii hex value.
    https://developer.twitter.com/en/docs/authentication/oauth-1-0a/percent-encoding-parameters

    Args:
        s (str): String to be percent encoded.

    Returns:
        Percent encoded string.

    Example:
    >>> strings = ("Ladies + Gentlemen", "An encoded string!", "Dogs, Cats & Mice", "☃")
    >>> for s in strings:
    ...     print(prcnt_encd(s))
    Ladies%20%2B%20Gentlemen
    An%20encoded%20string%21
    Dogs%2C%20Cats%20%26%20Mice
    %E2%98%83
    """

    return urllib.parse.quote(s, safe="")


class OAuth1ClientSession:

    def __init__(
            self,
            consumer_key: str,
            consumer_secret: str,
            access_token: str,
            access_token_secret: str):
        """ Constructor for OAuth1ClientSession class.

        Args:
            consumer_key (str): Account consumer key.
            consumer_secret (str): Account consumer secret key.
            access_token (str): Account access token.
            access_token_secret (str): Account access token secret.
        """

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

    @asynccontextmanager
    async def get(self, url: str, params: dict = None, data: dict = None):
        """ TODO: docstring
        """

        async with self._request(method="GET", url=url, params=params, data=data) as response:
            yield response

    @asynccontextmanager
    async def post(self, url: str, params: dict = None, data: dict = None):
        """ TODO: docstring
        """

        async with self._request(method="POST", url=url, params=params, data=data) as response:
            yield response

    @asynccontextmanager
    async def _request(self, method: str, url: str, params: dict = None, data: dict = None):
        """ Async method for making OAuth 1.0 request.

        Args:
            args (tuple): Positional arguments.
            kwargs (dict): Key-word arguments.

        Returns:
            obj: aiohttp.ClientResponse: Returned response object.
        """

        all_parameters = {}
        if params:
            all_parameters.update(params)
        if data:
            all_parameters.update(data)

        auth_header = {
            "Authorization": self.__generate_auth_header(method, url, all_parameters),
            "User-Agent": "OAuth gem v0.4.4",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        async with ClientSession() as client:
            async with client.request(method, url, params=params, data=data, headers=auth_header) as response:
                yield response

    def __generate_auth_header(self, method: str, url: str, request_params: Optional[dict] = None) -> str:
        """ Use given arguments, `method`, `url`, and `request_params`, along with the account credentials, to generate
            an OAuth 1.0 header str.

        API Reference:
            https://developer.twitter.com/en/docs/authentication/oauth-1-0a/authorizing-a-request

        Args:
            method (str): Request method type.
            url (str): URL request is being made to.
            request_parameters (dict | None, default = None): Parameters sent along with request.

        Returns:
            str: OAuth header string.
        """

        oauth_params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_nonce": self.__generate_nonce(),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time())),
            "oauth_token": self.access_token,
            "oauth_version": "1.0",
        }

        oauth_params["oauth_signature"] = self.__generate_signature(method, url, oauth_params, request_params)

        auth_header = []
        for key, value in sorted(oauth_params.items()):
            key, value = map(prcnt_encd, [key, value])
            auth_header.append(f'{key}="{value}"')

        return f"OAuth {', '.join(auth_header)}"

    def __generate_signature(
            self, method: str, url: str, oauth_params: dict, request_params: Optional[dict] = None) -> str:
        """ Create base64-encoded HMAC-SHA1 signature string from given arguments.

        API Reference:
            https://developer.twitter.com/en/docs/authentication/oauth-1-0a/creating-a-signature

        Args:
            method (str): Request method type.
            url (str): URL request is being made to.
            oauth_params (dict[str, str]): OAuth parameters.
            request_parameters (dict | None, default = None): Parameters sent along with request.

        Returns:
            str: Base64-encoded HMAC-SHA1 signature string.
        """

        parameter_string = self.__create_parameter_string(oauth_params, request_params)
        signature_base_string = self.__create_signature_base_string(method, url, parameter_string)
        signing_key = "&".join(map(prcnt_encd, [self.consumer_secret, self.access_token_secret]))
        hmac = HMAC(key=signing_key.encode(), msg=signature_base_string.encode(), digestmod=sha1)
        return b2a_base64(hmac.digest(), newline=False).decode()

    def __create_parameter_string(self, oauth_params: dict, request_params: Optional[dict] = None) -> str:
        """ Create percent-encoded, ampersand-deliminated parameter string from key, value pairs in given arguments.

        API Reference:
            https://developer.twitter.com/en/docs/authentication/oauth-1-0a/creating-a-signature

        Args:
            oauth_params (dict[str, str]): OAuth parameters.
            request_parameters (dict | None, default = None): Parameters sent along with request.

        Return:
            str: Percent-encoded, ampersand-deliminated parameter string.
        """

        if request_params is None:
            request_params = {}

        params = {**oauth_params, **request_params}

        parameter_string = []
        for key, value in sorted(params.items()):
            key, value = map(prcnt_encd, [key, value])
            parameter_string.append(f'{key}={value}')

        return "&".join(parameter_string)

    def __create_signature_base_string(self, method: str, url: str, parameter_string: str) -> str:
        """ Create percent-encoded, ampersand-deliminated signature base string from given arguments.

        API Reference:
            https://developer.twitter.com/en/docs/authentication/oauth-1-0a/creating-a-signature

        Args:
            method (str): Request method type.
            url (str): URL request is being made to.
            parameter_string (str): Return value of `__create_parameter_string`.

        Returns:
            str: Percent-encoded, ampersand-deliminated signature base string.
        """

        return "&".join([method.upper(), prcnt_encd(url), prcnt_encd(parameter_string)])

    def __generate_nonce(self) -> str:
        """ Generate a random 32 character, strictly alpha-numeric string.

        API Reference:
            https://developer.twitter.com/en/docs/authentication/oauth-1-0a/creating-a-signature

        Returns:
            str: 32 character nonce.
        """

        random.seed(time())
        return "".join([random.choice(ALPHA_NUM) for _ in range(32)])
