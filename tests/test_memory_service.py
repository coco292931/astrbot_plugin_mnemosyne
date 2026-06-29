"""
管理面板记忆服务测试。
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

if "astrbot.api" not in sys.modules:
    astrbot = types.ModuleType("astrbot")
    astrbot_api = types.ModuleType("astrbot.api")

    class _Logger:
        def info(self, *_args, **_kwargs):
            return None

        def error(self, *_args, **_kwargs):
            return None

        def warning(self, *_args, **_kwargs):
            return None

    astrbot_api.logger = _Logger()
    astrbot.api = astrbot_api
    sys.modules["astrbot"] = astrbot
    sys.modules["astrbot.api"] = astrbot_api


from admin_panel.services.memory_service import MemoryService  # noqa: E402
from memory_manager.vector_db_base import VectorDeleteResult  # noqa: E402


class _FakeVectorDB:
    def __init__(self):
        self.deleted_expr = None
        self.flushed = False

    def is_connected(self):
        return True

    def has_collection(self, _collection_name):
        return True

    def delete(self, collection_name, expr):
        self.deleted_expr = (collection_name, expr)
        return VectorDeleteResult(delete_count=1)

    def flush(self, _collection_names):
        self.flushed = True


class _Plugin:
    def __init__(self, vector_db_type):
        self.config = {"vector_db_type": vector_db_type}
        self.collection_name = "memory_collection"
        self.vector_db = _FakeVectorDB()


@pytest.mark.asyncio
async def test_delete_memory_uses_native_id_for_non_milvus():
    plugin = _Plugin("chroma")
    service = MemoryService(plugin)

    assert await service.delete_memory("native-id_1")
    assert plugin.vector_db.deleted_expr == (
        "memory_collection",
        'id == "native-id_1"',
    )
    assert plugin.vector_db.flushed


@pytest.mark.asyncio
async def test_delete_memory_uses_memory_id_for_milvus():
    plugin = _Plugin("milvus")
    service = MemoryService(plugin)

    assert await service.delete_memory("123")
    assert plugin.vector_db.deleted_expr == (
        "memory_collection",
        "memory_id == 123",
    )
