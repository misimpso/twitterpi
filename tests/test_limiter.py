import asyncio
import unittest

from contextlib import closing
from time import perf_counter
from twitterpi.limiter import Limiter
from unittest.mock import Mock, patch

SECONDS_IN_A_DAY: int = 60 * 60 * 24


class LimiterTests(unittest.TestCase):

    @patch("twitterpi.limiter.sleep")
    def test_acquire__verify_expected_sleep_time(self, mock_sleep: Mock):
        """ Verify `Limiter.acquire` will calculate expected sleep time given an expected `requests_per_day` value.
        """

        requests_per_day = 100
        seconds_per_request = SECONDS_IN_A_DAY / requests_per_day

        mock_logger = Mock()
        test_limiter = Limiter(requests_per_day=requests_per_day)
        call_times: float = []

        async def add_current_time(self):
            """ Test method to get the time between calls
            """

            current_time = perf_counter()
            call_times.append(current_time)

        mock_func = test_limiter.acquire(add_current_time)

        with closing(asyncio.get_event_loop()) as loop:
            loop.run_until_complete(
                asyncio.gather(*[
                    mock_func(mock_logger)
                    for _ in range(5)
                ])
            )

        # Make sure the sum of the time spent "sleeping" and the elapsed time between calls, is more
        # than `seconds_per_request`.
        for i, call in enumerate(mock_sleep.call_args_list):
            sleep_time: float = call[0][0]
            elapsed_call_time: float = (call_times[i + 1] - call_times[i])
            self.assertGreaterEqual((sleep_time + elapsed_call_time), seconds_per_request)


if __name__ == "__main__":
    unittest.main()
