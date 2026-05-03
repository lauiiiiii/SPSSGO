# -*- coding: utf-8 -*-
import os
from contextlib import contextmanager

from backend.config import DATA_EXTENSIONS
from backend.file_parser import parse_data_file
from backend.storage import storage_service


def load_dataframe(data_file: str):
    return parse_data_file(data_file)[0]


def upload_files(session_id: str) -> list[str]:
    return storage_service.list_files("uploads", session_id)


def find_data_file_name(session_id: str):
    for fname in upload_files(session_id):
        if os.path.splitext(fname)[1].lower() in DATA_EXTENSIONS:
            return fname
    return None


@contextmanager
def materialized_upload(session_id: str, filename: str):
    path = storage_service.materialize_file("uploads", session_id, filename)
    try:
        yield path
    finally:
        storage_service.release_materialized(path)

