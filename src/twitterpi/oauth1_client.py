import aiohttp
import random
import string
import time

from hashlib import sha1
from hmac import HMAC
from typing import Optional
from urllib.parse import quote

ALPHA_NUM = list(string.ascii_letters + string.digits)


class OAuth1ClientSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        self.consumer_key = kwargs.pop("consumer_key")
        self.consumer_secret = kwargs.pop("consumer_secret")
        self.access_token = kwargs.pop("access_token")
        self.access_token_secret = kwargs.pop("access_token_secret")
        super().__init__(*args, **kwargs)

    async def _request(self, *args: list, **kwargs: dict) -> aiohttp.ClientResponse:
        """ TODO: docstring
        """

        method = kwargs.get("method", args[0])
        url = str(kwargs.get("str_or_url", args[1]))
        params = kwargs.get("params", None)

        auth_header = {
            "Authorization": self.__generate_auth_header(method, url, params),
            "User-Agent": "OAuth gem v0.4.4",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        existing_headers = kwargs.pop("headers", {})
        existing_headers.update(auth_header)
        response = await super()._request(headers=existing_headers, *args, **kwargs)
        return response
    
    def __generate_auth_header(self, method: str, url: str, request_params: Optional[dict] = None) -> str:
        """ TODO: docstring
        """

        oauth_params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_nonce": self.__generate_nonce(),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": self.access_token,
            "oauth_version": str(1.0),
        }
        oauth_params["oauth_signature"] = self.__generate_signature(
            method, url, oauth_params, request_params)
        
        auth_header = []
        for key in sorted(oauth_params):
            key, value = map(quote, [key, oauth_params[key]])
            auth_header.append(f'{key}="{value}"')

        return f"OAuth {', '.join(auth_header)}"
    
    def __generate_signature(
            self,
            method: str,
            url: str,
            oauth_params: dict,
            request_params: Optional[dict] = None) -> str:
        """ TODO: docstring
            https://developer.twitter.com/en/docs/authentication/oauth-1-0a/creating-a-signature
        """

        parameter_string = self.__create_parameter_string(oauth_params, request_params)
        signature_base_string = self.__create_signature_base_string(method, url, parameter_string)
        signing_key = "&".join(map(quote, [self.consumer_key, self.access_token_secret]))
        hmac = HMAC(signature_base_string.encode(), signing_key.encode(), sha1)
        return hmac.hexdigest()
    
    def __create_parameter_string(self, oauth_params: dict, request_params: Optional[dict] = None) -> str:
        """ TODO: docstring
        """

        if request_params is None:
            request_params = {}
        
        params = {**oauth_params, **request_params}
        
        parameter_string = []
        for key in sorted(params):
            key = quote(key)
            value = params[key]
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, (int, float)):
                value = str(value)
            elif isinstance(value, str):
                value = quote(value)
            parameter_string.append(f'{key}={value}')
        
        return "&".join(parameter_string)

    def __create_signature_base_string(self, method: str, url: str, parameter_string: str) -> str:
        """ TODO: docstring
        """

        return "&".join([method.upper(), quote(url, safe=""), quote(parameter_string, safe="")])
    
    def __generate_nonce(self) -> str:
        """ Generate a 32 character, strictly alpha-numeric string.
        """

        random.seed(time.time())
        return "".join([random.choice(ALPHA_NUM) for _ in range(32)])
