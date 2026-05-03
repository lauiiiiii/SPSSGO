# -*- coding: utf-8 -*-
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app_runtime import FRONTEND_ASSETS_DIR, frontend_file

router = APIRouter()


def mount_frontend_assets(app):
    if os.path.isdir(FRONTEND_ASSETS_DIR):
        app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS_DIR), name="frontend-assets")


@router.get("/", include_in_schema=False)
async def frontend_index():
    index_file = frontend_file("index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(404, "前端构建文件不存在，请先构建 frontend/dist")


@router.get("/favicon.ico", include_in_schema=False)
async def favicon_ico():
    ico_file = frontend_file("favicon.ico")
    png_file = frontend_file("favicon.png")
    if os.path.exists(ico_file):
        return FileResponse(ico_file)
    if os.path.exists(png_file):
        return FileResponse(png_file, media_type="image/png")
    raise HTTPException(404, "favicon not found")


@router.get("/favicon.svg", include_in_schema=False)
async def favicon_svg():
    svg_file = frontend_file("favicon.svg")
    if os.path.exists(svg_file):
        return FileResponse(svg_file, media_type="image/svg+xml")
    raise HTTPException(404, "favicon not found")


@router.get("/{full_path:path}", include_in_schema=False)
async def frontend_spa(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(404, "接口不存在")

    candidate = frontend_file(full_path)
    if full_path and os.path.isfile(candidate):
        return FileResponse(candidate)

    index_file = frontend_file("index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(404, "前端构建文件不存在，请先构建 frontend/dist")

