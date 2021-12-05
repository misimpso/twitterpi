from asyncio import sleep
from time import perf_counter
from typing import Any, Callable, Coroutine


SECONDS_IN_A_DAY: int = 60 * 60 * 24


class Limiter:
    def __init__(self, name: str, requests_per_day: int):
        """ Constructor for Limiter class.

        Args:
            name (str): Name of the limiter.
            requests_per_day (int): Number of requests allowed per day.
        """

        self.requests_per_day = requests_per_day
        self._last_call_time = 0
        self.seconds_per_request = SECONDS_IN_A_DAY / requests_per_day
    
    def acquire(self, func: Coroutine) -> Callable:
        """ Decorator method to rate-limit given awaitable method `func`.
        
            Calculate any required sleep time between current time, last call time, and the requests per day.

        Args:
            func (Coroutine): Wrapped awaitable function.
        
        Returns:
            Coroutine: Wrapper method which calls given `func` after sleeping if needed.
        """

        async def wrapper(*args, **kwargs) -> Any:
            """ Sleep if needed, call wrapped awaitable `func` with given `args` and `kwargs`, and return result.
            
            Args:
                *args(tuple): Args to give to wrapped `func`.
                **kwargs(dict): Keyword arguments to give to wrapped `func`.
            
            Return:
                Return value of awaited `func`.
            """

            # Re-use the wrapped object's logger instance variable.
            # Hack to not need to instantiate a new logger
            logger = args[0].logger

            current_time = perf_counter()
            sleep_time = self.seconds_per_request - (current_time - self._last_call_time)
            if sleep_time > 0:
                logger.info(f"Sleeping for [{sleep_time:.2f}] seconds.")
                await sleep(sleep_time)
            self._last_call_time = perf_counter()
            return await func(*args, **kwargs)

        return wrapper
