import aiohttp
import binascii
import random
import time
import typing as ty
import string

from aiohttp import ClientResponse
from aiohttp.typedefs import StrOrURL
from hashlib import sha1
from hmac import HMAC

VALID_CHARS = set(string.ascii_letters + string.digits + "-_.~")


class OAuth1ClientSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        self.consumer_key = kwargs.pop("consumer_key")
        self.consumer_secret = kwargs.pop("consumer_secret")
        self.access_token = kwargs.pop("access_token")
        self.access_token_secret = kwargs.pop("access_token_secret")
        super().__init__(*args, **kwargs)

    async def _request(self, *args: list, **kwargs: dict) -> ClientResponse:
        """ TODO: docstring
        """
        method = kwargs.get("method", args[0])
        url = kwargs.get("str_or_url", args[1])
        params = kwargs.get("params", None)
        auth_header = {
            "Authorization": self.__create_auth_header(method, url, params),
            "UserAgent": "OAuth gem v0.4.4",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        existing_headers = kwargs.pop("headers", {})
        existing_headers.update(auth_header)
        print(args)
        print(kwargs)
        print(existing_headers)
        response = await super()._request(headers=existing_headers, *args, **kwargs)
        return response
    
    def __create_auth_header(self, method: str, url: StrOrURL, params: dict = None) -> str:
        """ Build OAuth header authentication string.
            https://developer.twitter.com/en/docs/basics/authentication/oauth-1-0a/authorizing-a-request
        """
        oauth = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_nonce": self.__generate_nonce(),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": int(time.time()),
            "oauth_token": self.access_token,
            "oauth_version": 1.0,
        }

        if params:
            oauth.update(params)
        
        oauth_string = []
        for key in sorted(oauth):
            sanitized_key = self.__percent_encode(str(key))
            sanitized_value = self.__percent_encode(str(oauth[key]))
            oauth_string.append(f"{sanitized_key}={sanitized_value}")




        if data:
            oauth.update(data)

        sanitized_oauth = {}
        flat_oauth = []
        for key in sorted(oauth):
            key = self.__percent_encode(str(key))
            value = self.__percent_encode(str(oauth[key]))
            flat_oauth.append("{}={}".format(key, value))
            if key != "include_entities":
                sanitized_oauth[key] = value

        if data:
            for key in data:
                sanitized_oauth.pop(key)

        signature_base_string = "&".join([
            method.upper(),
            self.__percent_encode(url),                  
            self.__percent_encode("&".join(flat_oauth))
        ])

        signing_key = "&".join([self.consumer_secret, self.access_token_secret])
        sanitized_oauth["oauth_signature"] = self.__percent_encode(
            self.__generate_hmac(signing_key, signature_base_string))

        return "OAuth {}".format(
            ", ".join([
                '{}="{}"'.format(key, sanitized_oauth[key])
                for key in sorted(sanitized_oauth)
            ]))
    
    def __generate_hmac(self, key: str, message: str) -> str:
        """ HMAC-SHA1 implementation
            https://github.com/python/cpython/blob/3.8/Lib/hmac.py
        """

        hmac = HMAC(key.encode(), message.encode(), sha1)
        return hmac.hexdigest()
        # return binascii.b2a_base64(hmac).decode()[:-1]


        # key = key.encode()
        # message = message.encode()
        # if len(key) > self.SHA1_BLOCK_SIZE:
        #     key = sha1(key).digest()
        # key += (b'\x00' * (self.SHA1_BLOCK_SIZE - len(key)))
        # key = key.ljust(self.SHA1_BLOCK_SIZE, b'\0')
        # outer, inner = sha1(), sha1()
        # inner.update(bytes((x ^ 0x36) for x in key))
        # outer.update(bytes((x ^ 0x5C) for x in key))
        # inner.update(message)
        # outer.update(inner.digest())
        # hmac = outer.digest()
        # return binascii.b2a_base64(hmac).decode()[:-1]
    
    def __percent_encode(self, dirty_string: str) -> str:
        """ Substitue characters in the given `dirty_string` that aren't in the regex
            `[A-Za-z0-9-_.~]` with their hexadecimal unicode code point.
        """
        return "".join([
            c if c in VALID_CHARS else f"%{ord(c):X}"
            for c in dirty_string])
    
    def __generate_nonce(self) -> str:
        """ Generate a 32 character, strictly alpha-numeric string.
        """
        random.seed(time.time())
        alpha_num = sum(map(list, (range(48, 58),range(65, 91), range(97, 123))), [])
        nonce = []
        for _ in range(32):
            rand_index = len(alpha_num)
            while rand_index >= len(alpha_num):
                rand_index = random.getrandbits(6)
            nonce.append(chr(alpha_num[rand_index]))
        return "".join(nonce)