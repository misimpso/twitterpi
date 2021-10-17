from dataclasses import field
from datetime import datetime
from pydantic import validator
from pydantic.dataclasses import dataclass
from twitterpi.dto import User

@dataclass(order=True)
class Tweet:
    id: int = field(compare=False)
    created_at: datetime
    text: str = field(compare=False)

    author: User = field(compare=False)
    mentions: list[User] = field(compare=False)

    @validator('created_at', pre=True)
    def parse_datetime(cls, v):
        """ TODO: docstring
        """

        return datetime.strptime(v, "%a %b %d %H:%M:%S +0000 %Y")
