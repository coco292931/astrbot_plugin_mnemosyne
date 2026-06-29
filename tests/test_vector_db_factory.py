"""
向量数据库工厂测试
测试多数据库类型支持和工厂模式
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path


class TestVectorDatabaseFactory:
    """测试 VectorDatabaseFactory"""

    def test_create_milvus_db(self):
        """测试创建 Milvus 数据库实例"""
        from memory_manager.vector_db.factory import VectorDatabaseFactory

        config = {
            "milvus_lite_path": "./test_data/milvus.db",
            "db_name": "test_db",
            "connection_alias": "test_alias",
        }

        with patch("memory_manager.vector_db.factory.MilvusVectorDB") as MockMilvus:
            db = VectorDatabaseFactory.create_vector_db(
                db_type="milvus",
                config=config,
                plugin_data_dir="./test_data"
            )

            # 验证调用了 MilvusVectorDB 构造函数
            MockMilvus.assert_called_once()
            call_args = MockMilvus.call_args[1]

            # 验证参数传递正确
            assert call_args["db_name"] == "test_db"
            assert call_args["alias"] == "test_alias"
            assert call_args["lite_path"] == "./test_data/milvus.db"

    def test_create_chroma_db(self):
        """测试创建 Chroma 数据库实例"""
        from memory_manager.vector_db.factory import VectorDatabaseFactory

        config = {
            "chroma_config": {
                "persist_directory": "./test_data/chroma"
            }
        }

        with patch("memory_manager.vector_db.factory.ChromaVectorDB") as MockChroma:
            db = VectorDatabaseFactory.create_vector_db(
                db_type="chroma",
                config=config,
                plugin_data_dir="./test_data"
            )

            # 验证调用了 ChromaVectorDB 构造函数
            MockChroma.assert_called_once()

    def test_create_chroma_db_client_mode(self):
        """测试创建 Chroma 客户端模式数据库"""
        from memory_manager.vector_db.factory import VectorDatabaseFactory

        config = {
            "chroma_config": {
                "host": "localhost",
                "port": 8000
            }
        }

        with patch("memory_manager.vector_db.factory.ChromaVectorDB") as MockChroma:
            db = VectorDatabaseFactory.create_vector_db(
                db_type="chroma",
                config=config,
                plugin_data_dir="./test_data"
            )

            MockChroma.assert_called_once()
            call_args = MockChroma.call_args[1]
            assert call_args["host"] == "localhost"
            assert call_args["port"] == 8000

    def test_missing_vector_db_type_defaults_to_chroma_in_initialization(self):
        """测试未配置 vector_db_type 时默认使用 Chroma。"""
        from astrbot_plugin_mnemosyne.core import initialization

        class Plugin:
            config = {"embedding_dim": 3}
            embedding_provider = None
            _embedding_provider_ready = False

        plugin = Plugin()

        with patch(
            "astrbot_plugin_mnemosyne.memory_manager.vector_db.factory.ChromaVectorDB"
        ) as MockChroma:
            initialization.initialize_config_and_schema(plugin)
            initialization.initialize_vector_db(plugin, "./test_data")

        MockChroma.assert_called_once()
        assert plugin.vector_db is MockChroma.return_value

    def test_unsupported_db_type(self):
        """测试不支持的数据库类型"""
        from memory_manager.vector_db.factory import VectorDatabaseFactory

        config = {}

        with pytest.raises(ValueError, match="不支持的向量数据库类型"):
            VectorDatabaseFactory.create_vector_db(
                db_type="unsupported_db",
                config=config
            )

    def test_milvus_with_address(self):
        """测试使用 address 配置的 Milvus"""
        from memory_manager.vector_db.factory import VectorDatabaseFactory

        config = {
            "address": "localhost:19530",
            "db_name": "production_db",
            "authentication": {
                "user": "admin",
                "password": "password123"
            }
        }

        with patch("memory_manager.vector_db.factory.MilvusVectorDB") as MockMilvus:
            db = VectorDatabaseFactory.create_vector_db(
                db_type="milvus",
                config=config,
                plugin_data_dir="./test_data"
            )

            call_args = MockMilvus.call_args[1]
            assert call_args["host"] == "localhost"
            assert call_args["port"] == 19530
            assert call_args["db_name"] == "production_db"
            assert call_args["user"] == "admin"
            assert call_args["password"] == "password123"


class TestMilvusDbNameFix:
    """测试 Issue #131 修复：db_name 配置被正确使用"""

    def test_db_name_is_passed_to_connection(self):
        """测试 db_name 被正确传递到连接参数"""
        pytest.importorskip("pymilvus")
        from memory_manager.vector_db.milvus_manager import MilvusManager

        manager = MilvusManager(
            host="localhost",
            port=19530,
            db_name="custom_database",
            plugin_data_dir="./test_data"
        )

        # 验证 db_name 在连接信息中
        assert manager._db_name == "custom_database"
        assert manager._connection_info.get("db_name") == "custom_database"

    def test_default_db_name(self):
        """测试默认 db_name"""
        pytest.importorskip("pymilvus")
        from memory_manager.vector_db.milvus_manager import MilvusManager

        manager = MilvusManager(
            host="localhost",
            port=19530,
            db_name="default",
            plugin_data_dir="./test_data"
        )

        # 默认值不应该在连接信息中（优化）
        assert manager._db_name == "default"
        # 注意：默认值可能不在 connection_info 中，这是正常的

    def test_token_auth_is_passed(self):
        """测试 token 认证被正确传递"""
        pytest.importorskip("pymilvus")
        from memory_manager.vector_db.milvus_manager import MilvusManager

        manager = MilvusManager(
            uri="http://localhost:19530",
            token="test_token_123",
            db_name="test_db",
            plugin_data_dir="./test_data"
        )

        # 验证 token 在连接信息中
        assert manager._token == "test_token_123"
        assert manager._connection_info.get("token") == "test_token_123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
