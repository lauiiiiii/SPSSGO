# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from backend.admin import user_service as admin_user_service


class AdminUserServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_admin_user_rejects_duplicate_username(self):
        with patch("backend.admin.user_service.get_user_by_username", new=AsyncMock(return_value={"id": 2})):
            with self.assertRaises(HTTPException) as ctx:
                await admin_user_service.create_admin_user({
                    "username": "demo",
                    "password": "secret123",
                    "role": "user",
                })
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_update_admin_user_blocks_demoting_last_admin(self):
        target = {"id": 7, "username": "boss", "role": "admin", "is_active": 1}
        acting_user = {"id": 9, "username": "other", "role": "admin", "is_active": 1}

        with patch("backend.admin.user_service.get_user_by_id", new=AsyncMock(return_value=target)):
            with patch("backend.admin.user_service.count_active_admin_users", new=AsyncMock(return_value=0)):
                with self.assertRaises(HTTPException) as ctx:
                    await admin_user_service.update_admin_user(7, {"role": "user"}, acting_user)

        self.assertEqual(ctx.exception.status_code, 400)

    async def test_toggle_admin_user_revokes_tokens_when_disabling_user(self):
        target = {"id": 12, "username": "demo", "role": "user", "is_active": 1, "created_at": 1.0, "last_login_at": None}
        acting_user = {"id": 1, "username": "root", "role": "admin", "is_active": 1}

        with patch("backend.admin.user_service.get_user_by_id", new=AsyncMock(side_effect=[target, {**target, "is_active": 0}])):
            with patch("backend.admin.user_service.update_user", new=AsyncMock()) as update_user:
                with patch("backend.admin.user_service.revoke_user_refresh_tokens", new=AsyncMock()) as revoke_tokens:
                    result = await admin_user_service.toggle_admin_user_active(12, False, acting_user)

        update_user.assert_awaited_once_with(12, is_active=0)
        revoke_tokens.assert_awaited_once_with(12)
        self.assertEqual(result["is_active"], 0)

    async def test_toggle_admin_user_blocks_disabling_self(self):
        acting_user = {"id": 5, "username": "boss", "role": "admin", "is_active": 1}
        target = {"id": 5, "username": "boss", "role": "admin", "is_active": 1}

        with patch("backend.admin.user_service.get_user_by_id", new=AsyncMock(return_value=target)):
            with self.assertRaises(HTTPException) as ctx:
                await admin_user_service.toggle_admin_user_active(5, False, acting_user)

        self.assertEqual(ctx.exception.status_code, 400)

    async def test_reset_admin_user_password_updates_hash_and_revokes_tokens(self):
        target = {"id": 8, "username": "demo", "role": "user", "is_active": 1}

        with patch("backend.admin.user_service.get_user_by_id", new=AsyncMock(return_value=target)):
            with patch("backend.admin.user_service.hash_password_async", new=AsyncMock(return_value="hashed")) as hash_password:
                with patch("backend.admin.user_service.update_user", new=AsyncMock()) as update_user:
                    with patch("backend.admin.user_service.revoke_user_refresh_tokens", new=AsyncMock()) as revoke_tokens:
                        result = await admin_user_service.reset_admin_user_password(8, "secret123")

        hash_password.assert_awaited_once_with("secret123")
        update_user.assert_awaited_once_with(8, password_hash="hashed")
        revoke_tokens.assert_awaited_once_with(8)
        self.assertEqual(result, {"success": True})
