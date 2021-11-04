import aiohttp
import random
import string
import urllib

from binascii import b2a_base64
from hashlib import sha1
from hmac import HMAC
from time import time
from typing import Optional


ALPHA_NUM: list[str] = list(string.ascii_letters + string.digits)

def prcnt_encd(s: str) -> str:
    """ Percent encode given string `s`.

    Characters not in set `[A-Za-z0-9\-\.\_\~]` will be converted to their ascii hex value.
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


class OAuth1ClientSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        """ TODO: docstring
        """
        self.consumer_key = kwargs.pop("consumer_key")
        self.consumer_secret = kwargs.pop("consumer_secret")
        self.access_token = kwargs.pop("access_token")
        self.access_token_secret = kwargs.pop("access_token_secret")

        super().__init__(*args, **kwargs)

    async def _request(self, *args: tuple, **kwargs: dict) -> aiohttp.ClientResponse:
        """ TODO: docstring
        """

        method: str = kwargs.get("method", args[0])
        url: str = str(kwargs.get("str_or_url", args[1]))
        params: Optional[dict] = kwargs.get("params", None)
        data: Optional[dict] = kwargs.get("data", None)

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
        existing_headers = kwargs.pop("headers", {})
        existing_headers.update(auth_header)

        # params = urllib.parse.urlencode(params)
        # print(params)

        response = await super()._request(headers=existing_headers, *args, **kwargs)
        return response
    
    def __generate_auth_header(self, method: str, url: str, request_params: Optional[dict] = None) -> str:
        """ TODO: docstring
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
    
    def __generate_signature(self, method: str, url: str, oauth_params: dict, request_params: Optional[dict] = None) -> str:
        """ TODO: docstring
            https://developer.twitter.com/en/docs/authentication/oauth-1-0a/creating-a-signature
        """

        parameter_string = self.__create_parameter_string(oauth_params, request_params)
        signature_base_string = self.__create_signature_base_string(method, url, parameter_string)
        signing_key = "&".join(map(prcnt_encd, [self.consumer_secret, self.access_token_secret]))
        hmac = HMAC(key=signing_key.encode(), msg=signature_base_string.encode(), digestmod=sha1)
        return b2a_base64(hmac.digest(), newline=False).decode()
    
    def __create_parameter_string(self, oauth_params: dict, request_params: Optional[dict] = None) -> str:
        """ TODO: docstring
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
        """ TODO: docstring
        """

        return "&".join([method.upper(), prcnt_encd(url), prcnt_encd(parameter_string)])
    
    def __generate_nonce(self) -> str:
        """ Generate a 32 character, strictly alpha-numeric string.
        """

        random.seed(time())
        return "".join([random.choice(ALPHA_NUM) for _ in range(32)])
