import logging

from asyncio import sleep
from time import perf_counter


SECONDS_IN_A_DAY: int = 60 * 60 * 24


class Limiter:
    def __init__(self, name, requests_per_day: float):
        """ TODO: docstring
        """

        self.logger = logging.getLogger(name)
        self.requests_per_day = requests_per_day
        self._last_call_time = 0
        self.interval = (1 / requests_per_day) * SECONDS_IN_A_DAY
    
    def acquire(self, func):
        """ TODO: docstring
        """

        async def wrapper(*args, **kwargs):
            """ TODO: docstring
            """

            current_time = perf_counter()
            sleep_time = self.interval - (current_time - self._last_call_time)
            if sleep_time > 0:
                self.logger.info(f"Sleeping for [{sleep_time:.2f}] seconds.")
                await sleep(sleep_time)
            self._last_call_time = perf_counter()
            return await func(*args, **kwargs)
        return wrapper
