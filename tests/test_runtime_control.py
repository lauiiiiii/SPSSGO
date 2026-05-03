# -*- coding: utf-8 -*-
import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from backend import runtime_control


class RuntimeControlTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        runtime_control._RATE_LIMIT_STATE.clear()
        runtime_control._LOCAL_SESSION_LOCKS.clear()
        runtime_control._REDIS_CLIENT = None
        runtime_control._REDIS_DISABLED_UNTIL = 0.0

    async def test_hit_rate_limit_uses_local_fallback(self):
        with patch("backend.runtime_control.get_redis_client", new=AsyncMock(return_value=None)):
            result1 = await runtime_control.hit_rate_limit("login", "user-a", limit=2, window_seconds=60)
            result2 = await runtime_control.hit_rate_limit("login", "user-a", limit=2, window_seconds=60)
            result3 = await runtime_control.hit_rate_limit("login", "user-a", limit=2, window_seconds=60)

        self.assertTrue(result1.allowed)
        self.assertTrue(result2.allowed)
        self.assertFalse(result3.allowed)
        self.assertEqual(result3.count, 3)
        self.assertEqual(result3.remaining, 0)

    async def test_session_write_lock_rejects_parallel_writer(self):
        entered = asyncio.Event()
        release = asyncio.Event()

        async def holder():
            async with runtime_control.session_write_lock("sess-1", holder="holder-a"):
                entered.set()
                await release.wait()

        with patch("backend.runtime_control.get_redis_client", new=AsyncMock(return_value=None)):
            task = asyncio.create_task(holder())
            await entered.wait()

            with self.assertRaises(HTTPException) as ctx:
                async with runtime_control.session_write_lock("sess-1", holder="holder-b", wait_timeout=0):
                    pass

            self.assertEqual(ctx.exception.status_code, 409)
            release.set()
            await task

    async def test_get_redis_client_disables_unhealthy_client(self):
        fake_client = AsyncMock()
        fake_client.ping.side_effect = RuntimeError("redis unavailable")
        fake_client.aclose = AsyncMock()

        with patch("backend.runtime_control.from_url", return_value=fake_client):
            client = await runtime_control.get_redis_client()

        self.assertIsNone(client)
        fake_client.ping.assert_awaited_once()
        fake_client.aclose.assert_awaited_once()
        self.assertGreater(runtime_control._REDIS_DISABLED_UNTIL, 0.0)
