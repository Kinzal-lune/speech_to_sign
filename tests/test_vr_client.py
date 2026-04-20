from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from speech_to_sign.vr_client import VRClient


class TestVRClient(unittest.TestCase):
    def test_http_success(self) -> None:
        client = VRClient(
            endpoint="http://127.0.0.1:5000/sign-sequence",
            timeout=1.0,
            socket_host="127.0.0.1",
            socket_port=8765,
            socket_enabled=False,
        )
        response = Mock()
        response.status_code = 200
        response.raise_for_status = Mock()

        with patch("speech_to_sign.vr_client.requests") as mocked_requests:
            mocked_requests.post.return_value = response
            result = client.send(["SIGN_HELLO"], "hello")

        self.assertTrue(result.sent)
        self.assertEqual(result.channel, "http")

    def test_http_retries_then_fails(self) -> None:
        client = VRClient(
            endpoint="http://127.0.0.1:5000/sign-sequence",
            timeout=1.0,
            socket_host="127.0.0.1",
            socket_port=8765,
            socket_enabled=False,
            retries=2,
            retry_backoff_seconds=0,
        )

        with patch("speech_to_sign.vr_client.requests") as mocked_requests:
            mocked_requests.post.side_effect = RuntimeError("network down")
            result = client.send(["SIGN_HELLO"], "hello")

        self.assertFalse(result.sent)
        self.assertEqual(mocked_requests.post.call_count, 3)
        self.assertEqual(result.attempts, 3)


if __name__ == "__main__":
    unittest.main()
