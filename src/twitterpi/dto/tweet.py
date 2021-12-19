from dataclasses import field
from datetime import datetime
from pydantic import validator
from pydantic.dataclasses import dataclass
from twitterpi.dto.user import User
from typing import Union

_twitter_datetime_format = "%a %b %d %H:%M:%S +0000 %Y"


@dataclass
class Tweet:
    id: int
    created_at: datetime
    text: str

    author: User
    mentions: list[User] = field(default_factory=list)

    @validator("created_at", pre=True)
    def parse_twitter_datetime(cls, value: Union[str, datetime]) -> datetime:
        """ Parse given `value` as a Twitter datatime.

        Args:
            value (str | obj: Datetime): Datetime object or string to parse.

        Returns:
            obj: datetime
        """

        if isinstance(value, str):
            return datetime.strptime(value, _twitter_datetime_format)

        elif isinstance(value, datetime):
            return value

        raise TypeError(f"Unexpected type for given argument `value`. [{value=}, {type(value).__name__}]")
