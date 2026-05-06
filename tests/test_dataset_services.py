# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch

import backend.database  # noqa: F401
from fastapi import HTTPException

from backend.services import dataset_folder_service, dataset_service


class DatasetServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_list_datasets_shapes_counts_from_current_summary(self):
        row = {
            "id": 7,
            "session_id": "sess-1",
            "name": "",
            "research_topic": "满意度项目",
            "original_filename": "survey.xlsx",
            "created_at": 10.0,
            "last_used_at": None,
            "session_status": "created",
            "current_version_id": 3,
            "current_version_no": 2,
            "version_count": 2,
            "result_count": 5,
            "current_summary": {"total_rows": 120.0, "total_cols": 8},
        }

        with patch("backend.services.dataset_service.list_datasets_for_owner", new=AsyncMock(return_value=[row])) as list_rows:
            with patch("backend.services.dataset_service.count_datasets_for_owner", new=AsyncMock(return_value=12)) as count_rows:
                result = await dataset_service.list_datasets_for_user(
                    {"id": 1, "role": "user"},
                    q=" 满意度 ",
                    sort="bad-sort",
                    page=2,
                    page_size=20,
                )

        list_rows.assert_awaited_once_with(
            1,
            is_admin=False,
            limit=20,
            offset=20,
            query="满意度",
            sort="recent",
            in_folder=None,
        )
        count_rows.assert_awaited_once_with(1, is_admin=False, query="满意度", in_folder=None)
        item = result["datasets"][0]
        self.assertEqual(item["name"], "满意度项目")
        self.assertEqual(item["row_count"], 120)
        self.assertEqual(item["column_count"], 8)
        self.assertEqual(result["total"], 12)
        self.assertEqual(result["page"], 2)
        self.assertEqual(result["page_size"], 20)
        self.assertEqual(result["sort"], "recent")

    async def test_rename_dataset_rejects_blank_name(self):
        with self.assertRaises(HTTPException) as ctx:
            await dataset_service.rename_dataset_for_user(1, "   ", {"id": 1, "role": "user"})

        self.assertEqual(ctx.exception.status_code, 400)

    async def test_rename_dataset_blocks_other_user_dataset(self):
        with patch("backend.services.dataset_service.get_dataset", new=AsyncMock(return_value={"id": 1, "owner_id": 9})):
            with self.assertRaises(HTTPException) as ctx:
                await dataset_service.rename_dataset_for_user(1, "新名称", {"id": 1, "role": "user"})

        self.assertEqual(ctx.exception.status_code, 404)

    async def test_delete_dataset_deletes_linked_session(self):
        dataset = {"id": 3, "owner_id": 1, "session_id": "sess-3"}

        with patch("backend.services.dataset_service.get_dataset", new=AsyncMock(return_value=dataset)):
            with patch("backend.services.dataset_service.delete_session", new=AsyncMock()) as delete_session:
                result = await dataset_service.delete_dataset_for_user(3, {"id": 1, "role": "user"})

        delete_session.assert_awaited_once_with("sess-3")
        self.assertEqual(result["session_id"], "sess-3")

    async def test_batch_delete_datasets_rejects_empty_list(self):
        with self.assertRaises(HTTPException) as ctx:
            await dataset_service.batch_delete_datasets_for_user([], {"id": 1, "role": "user"})
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_batch_delete_datasets_rejects_oversized_list(self):
        with self.assertRaises(HTTPException) as ctx:
            await dataset_service.batch_delete_datasets_for_user(["s"] * 501, {"id": 1, "role": "user"})
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_batch_delete_datasets_skips_missing_and_deletes_owned(self):
        datasets = [
            {"id": 1, "owner_id": 1, "session_id": "s1"},
            {"id": 2, "owner_id": 9, "session_id": "s2"},  # 无权限
            {"id": 3, "owner_id": 1, "session_id": "s3"},
        ]

        def _get_dataset_for_session(sid):
            return next((d for d in datasets if d["session_id"] == sid), None)

        with patch("backend.services.dataset_service.get_dataset_for_session", new=AsyncMock(side_effect=_get_dataset_for_session)):
            with patch("backend.services.dataset_service.delete_session", new=AsyncMock()) as delete_session:
                result = await dataset_service.batch_delete_datasets_for_user(
                    ["s1", "s2", "s3", "s4"], {"id": 1, "role": "user"}
                )

        self.assertEqual(result["count"], 2)
        self.assertEqual(sorted(result["deleted"]), ["s1", "s3"])
        self.assertEqual(len(result["failed"]), 2)
        failed_sids = {f["session_id"] for f in result["failed"]}
        self.assertEqual(failed_sids, {"s2", "s4"})
        delete_session.assert_any_await("s1")
        delete_session.assert_any_await("s3")


class DatasetFolderServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_folder_rejects_blank_name(self):
        with self.assertRaises(HTTPException) as ctx:
            await dataset_folder_service.create_dataset_folder_for_user("  ", {"id": 1, "role": "user"})

        self.assertEqual(ctx.exception.status_code, 400)

    async def test_create_folder_rejects_duplicate_name_for_same_user(self):
        with patch("backend.services.dataset_folder_service.get_folder_by_owner_name", new=AsyncMock(return_value={"id": 2})):
            with self.assertRaises(HTTPException) as ctx:
                await dataset_folder_service.create_dataset_folder_for_user("项目", {"id": 1, "role": "user"})

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("同名", str(ctx.exception.detail))

    async def test_rename_folder_blocks_other_user_folder(self):
        folder = {"id": 4, "owner_id": 9, "name": "旧名称"}

        with patch("backend.services.dataset_folder_service.get_folder", new=AsyncMock(return_value=folder)):
            with self.assertRaises(HTTPException) as ctx:
                await dataset_folder_service.rename_dataset_folder_for_user(4, "新名称", {"id": 1, "role": "user"})

        self.assertEqual(ctx.exception.status_code, 404)

    async def test_rename_folder_allows_same_folder_name(self):
        folder = {"id": 4, "owner_id": 1, "name": "项目"}

        with patch("backend.services.dataset_folder_service.get_folder", new=AsyncMock(return_value=folder)):
            with patch("backend.services.dataset_folder_service.get_folder_by_owner_name", new=AsyncMock(return_value=folder)):
                with patch("backend.services.dataset_folder_service.rename_folder", new=AsyncMock()) as rename_folder:
                    result = await dataset_folder_service.rename_dataset_folder_for_user(4, " 项目 ", {"id": 1, "role": "user"})

        rename_folder.assert_awaited_once_with(4, "项目")
        self.assertEqual(result["folder"]["name"], "项目")

    async def test_rename_folder_rejects_duplicate_name_for_same_owner(self):
        folder = {"id": 4, "owner_id": 1, "name": "旧名称"}
        duplicate = {"id": 5, "owner_id": 1, "name": "项目"}

        with patch("backend.services.dataset_folder_service.get_folder", new=AsyncMock(return_value=folder)):
            with patch("backend.services.dataset_folder_service.get_folder_by_owner_name", new=AsyncMock(return_value=duplicate)):
                with self.assertRaises(HTTPException) as ctx:
                    await dataset_folder_service.rename_dataset_folder_for_user(4, "项目", {"id": 1, "role": "user"})

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("同名", str(ctx.exception.detail))

    async def test_move_dataset_to_folder_checks_dataset_and_folder_owner(self):
        dataset = {"id": 8, "owner_id": 1, "session_id": "sess-8"}
        folder = {"id": 5, "owner_id": 1, "name": "项目"}

        with patch("backend.services.dataset_folder_service.get_dataset_for_session", new=AsyncMock(return_value=dataset)):
            with patch("backend.services.dataset_folder_service.get_folder", new=AsyncMock(return_value=folder)):
                with patch("backend.services.dataset_folder_service.set_dataset_folder", new=AsyncMock()) as set_folder:
                    result = await dataset_folder_service.move_dataset_to_folder_for_user(
                        "sess-8",
                        5,
                        {"id": 1, "role": "user"},
                    )

        set_folder.assert_awaited_once_with(8, 5)
        self.assertEqual(result, {"ok": True, "session_id": "sess-8", "folder_id": 5})

    async def test_move_dataset_blocks_cross_user_dataset(self):
        dataset = {"id": 8, "owner_id": 9, "session_id": "sess-8"}

        with patch("backend.services.dataset_folder_service.get_dataset_for_session", new=AsyncMock(return_value=dataset)):
            with self.assertRaises(HTTPException) as ctx:
                await dataset_folder_service.move_dataset_to_folder_for_user("sess-8", None, {"id": 1, "role": "user"})

        self.assertEqual(ctx.exception.status_code, 404)

    async def test_batch_move_datasets_rejects_empty_list(self):
        with self.assertRaises(HTTPException) as ctx:
            await dataset_folder_service.batch_move_datasets_to_folder_for_user([], None, {"id": 1, "role": "user"})
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_batch_move_datasets_rejects_oversized_list(self):
        with self.assertRaises(HTTPException) as ctx:
            await dataset_folder_service.batch_move_datasets_to_folder_for_user(["s"] * 501, None, {"id": 1, "role": "user"})
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_batch_move_datasets_skips_missing_and_moves_owned(self):
        datasets = [
            {"id": 1, "owner_id": 1, "session_id": "s1"},
            {"id": 2, "owner_id": 9, "session_id": "s2"},  # 无权限
            {"id": 3, "owner_id": 1, "session_id": "s3"},
        ]
        folder = {"id": 5, "owner_id": 1, "name": "项目"}

        def _get_dataset_for_session(sid):
            return next((d for d in datasets if d["session_id"] == sid), None)

        with patch("backend.services.dataset_folder_service.get_dataset_for_session", new=AsyncMock(side_effect=_get_dataset_for_session)):
            with patch("backend.services.dataset_folder_service.get_folder", new=AsyncMock(return_value=folder)):
                with patch("backend.services.dataset_folder_service.set_dataset_folder", new=AsyncMock()) as set_folder:
                    result = await dataset_folder_service.batch_move_datasets_to_folder_for_user(
                        ["s1", "s2", "s3", "s4"], 5, {"id": 1, "role": "user"}
                    )

        self.assertEqual(result["count"], 2)
        self.assertEqual(sorted(result["moved"]), ["s1", "s3"])
        self.assertEqual(result["folder_id"], 5)
        set_folder.assert_any_await(1, 5)
        set_folder.assert_any_await(3, 5)
        self.assertEqual(set_folder.await_count, 2)
