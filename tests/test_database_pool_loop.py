# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, Mock, patch

from backend import database


class DatabasePoolLoopTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        database._pool = None
        database._pool_loop = None

    async def asyncTearDown(self):
        database._pool = None
        database._pool_loop = None

    async def test_init_db_reuses_pool_on_same_loop(self):
        loop = object()
        pool = AsyncMock()

        with patch("backend.database.asyncio.get_running_loop", return_value=loop):
            with patch("backend.database.aiomysql.create_pool", new=AsyncMock(return_value=pool)) as create_pool:
                with patch("backend.database.DB_AUTO_CREATE", False):
                    with patch("backend.database.bootstrap_initial_admin", new=AsyncMock()):
                        await database.init_db()
                        await database.init_db()

        create_pool.assert_awaited_once()
        pool.close.assert_not_called()
        pool.wait_closed.assert_not_awaited()

    async def test_init_db_recreates_pool_when_loop_changes(self):
        first_loop = object()
        second_loop = object()
        first_pool = AsyncMock()
        second_pool = AsyncMock()
        first_pool.close = Mock()
        second_pool.close = Mock()

        with patch("backend.database.asyncio.get_running_loop", side_effect=[first_loop, second_loop]):
            with patch("backend.database.aiomysql.create_pool", new=AsyncMock(side_effect=[first_pool, second_pool])) as create_pool:
                with patch("backend.database.DB_AUTO_CREATE", False):
                    with patch("backend.database.bootstrap_initial_admin", new=AsyncMock()):
                        await database.init_db()
                        await database.init_db()

        self.assertEqual(create_pool.await_count, 2)
        first_pool.close.assert_called_once()
        first_pool.wait_closed.assert_awaited_once()
        self.assertIs(database._pool, second_pool)
        self.assertIs(database._pool_loop, second_loop)

    async def test_init_db_ignores_closed_loop_when_disposing_old_pool(self):
        first_loop = object()
        second_loop = object()
        first_pool = AsyncMock()
        second_pool = AsyncMock()
        first_pool.close = Mock()
        first_pool.wait_closed = AsyncMock(side_effect=RuntimeError("Event loop is closed"))
        second_pool.close = Mock()

        with patch("backend.database.asyncio.get_running_loop", side_effect=[first_loop, second_loop]):
            with patch("backend.database.aiomysql.create_pool", new=AsyncMock(side_effect=[first_pool, second_pool])) as create_pool:
                with patch("backend.database.DB_AUTO_CREATE", False):
                    with patch("backend.database.bootstrap_initial_admin", new=AsyncMock()):
                        await database.init_db()
                        await database.init_db()

        self.assertEqual(create_pool.await_count, 2)
        first_pool.close.assert_called_once()
        first_pool.wait_closed.assert_awaited_once()
        self.assertIs(database._pool, second_pool)
        self.assertIs(database._pool_loop, second_loop)

    async def test_init_db_suppresses_sql_notes_during_schema_bootstrap(self):
        loop = object()
        pool = AsyncMock()
        pool.close = Mock()
        conn = AsyncMock()
        cur = AsyncMock()

        acquire_cm = AsyncMock()
        acquire_cm.__aenter__.return_value = conn
        pool.acquire = Mock(return_value=acquire_cm)

        cursor_cm = AsyncMock()
        cursor_cm.__aenter__.return_value = cur
        conn.cursor = Mock(return_value=cursor_cm)

        with patch("backend.database.asyncio.get_running_loop", return_value=loop):
            with patch("backend.database.aiomysql.create_pool", new=AsyncMock(return_value=pool)):
                with patch("backend.database.DB_AUTO_CREATE", True):
                    with patch("backend.database.bootstrap_initial_admin", new=AsyncMock()) as bootstrap_admin:
                        await database.init_db()

        executed_sql = [call.args[0] for call in cur.execute.await_args_list]
        self.assertEqual(executed_sql[0], "SET sql_notes = 0")
        self.assertEqual(executed_sql[-1], "SET sql_notes = 1")
        bootstrap_admin.assert_awaited_once()
