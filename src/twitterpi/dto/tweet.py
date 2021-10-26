from dataclasses import field
from datetime import datetime
from pydantic import validator
from pydantic.dataclasses import dataclass
from twitterpi.dto.user import User

_twitter_datetime_format = "%a %b %d %H:%M:%S +0000 %Y"


@dataclass
class Tweet:
    id: int
    created_at: datetime
    text: str

    author: User
    mentions: list[User] = field(default_factory=list)

    @validator('created_at', pre=True)
    def parse_datetime(cls, v: str) -> datetime:
        """ TODO: docstring
        """

        return datetime.strptime(v, _twitter_datetime_format)
