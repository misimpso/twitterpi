import unittest

from time import perf_counter
from twitterpi.limiter import Limiter
from unittest.mock import AsyncMock, patch

REQUESTS_PER_DAY = 100
SECONDS_IN_A_DAY: int = 60 * 60 * 24
SECONDS_PER_REQUEST = SECONDS_IN_A_DAY / REQUESTS_PER_DAY

CALL_TIMES = []


class LimiterTests(unittest.IsolatedAsyncioTestCase):

    @patch("twitterpi.limiter.sleep", new_callable=AsyncMock)
    def setUp(self, mock_sleep: AsyncMock):
        """ Constructor for test fixture.

            Mock out `asyncio.sleep` and create Limiter object.
        """

        self.mock_sleep = mock_sleep
        self.limiter = Limiter(requests_per_day=REQUESTS_PER_DAY)

    async def add_current_time(self):
        """ Test method to get the time between calls.
        """

        current_time = perf_counter()
        CALL_TIMES.append(current_time)

    async def test_acquire__verify_expected_sleep_time(self):
        """ Verify `Limiter.acquire` will calculate expected sleep time given an expected `requests_per_day` value.
        """

        for _ in range(20):
            self.limiter.acquire(self.add_current_time)

        # Make sure the sum of the time spent "sleeping" and the elapsed time between calls, is more
        # than `seconds_per_request`.
        for i, call in enumerate(self.mock_sleep.call_args_list):
            sleep_time: float = call[0][0]
            elapsed_call_time: float = (CALL_TIMES[i + 1] - CALL_TIMES[i])
            self.assertGreaterEqual((sleep_time + elapsed_call_time), SECONDS_PER_REQUEST)

if __name__ == "__main__":
    unittest.main()
