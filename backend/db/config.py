"""MongoDB configuration and connection management."""

import os
from typing import Optional, Any
from pydantic_settings import BaseSettings
from pymongo import MongoClient, ASCENDING, DESCENDING
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDBSettings(BaseSettings):
    """MongoDB configuration from environment variables."""

    mongodb_url: str = os.getenv(
        "MONGODB_URL",
        "mongodb://localhost:27017"
    )
    mongodb_database: str = os.getenv(
        "MONGODB_DATABASE",
        "sentinel_net"
    )
    mongodb_username: Optional[str] = os.getenv("MONGODB_USERNAME")
    mongodb_password: Optional[str] = os.getenv("MONGODB_PASSWORD")
    mongodb_replica_set: Optional[str] = os.getenv("MONGODB_REPLICA_SET")
    
    # Connection pooling
    max_pool_size: int = int(os.getenv("MONGODB_MAX_POOL_SIZE", "50"))
    min_pool_size: int = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
    
    # Advanced options
    server_selection_timeout_ms: int = int(
        os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000")
    )
    socket_timeout_ms: int = int(
        os.getenv("MONGODB_SOCKET_TIMEOUT_MS", "30000")
    )
    
    # Transactions (requires replica set)
    enable_transactions: bool = os.getenv("MONGODB_ENABLE_TRANSACTIONS", "false").lower() == "true"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = 'ignore'  # Ignore extra environment variables

    def build_connection_string(self) -> str:
        """Build MongoDB connection string with auth if provided."""
        url = self.mongodb_url
        
        # Add authentication
        if self.mongodb_username and self.mongodb_password:
            # Parse URL and insert credentials
            if "://" in url:
                protocol, rest = url.split("://", 1)
                url = f"{protocol}://{self.mongodb_username}:{self.mongodb_password}@{rest}"
        
        # Add replica set if configured
        if self.mongodb_replica_set:
            separator = "&" if "?" in url else "?"
            url += f"{separator}replicaSet={self.mongodb_replica_set}"
        
        return url


class MongoDBConnection:
    """MongoDB connection manager with async support."""

    _async_client: Optional[AsyncIOMotorClient] = None
    _sync_client: Optional[MongoClient] = None
    _async_db: Optional[Any] = None
    _settings: Optional[MongoDBSettings] = None

    @classmethod
    def initialize(cls, settings: Optional[MongoDBSettings] = None) -> None:
        """Initialize MongoDB connection."""
        cls._settings = settings or MongoDBSettings()

    @classmethod
    async def get_async_client(cls) -> AsyncIOMotorClient:
        """Get async MongoDB client (Motor)."""
        if cls._async_client is None:
            if cls._settings is None:
                cls.initialize()
            
            connection_string = cls._settings.build_connection_string()
            cls._async_client = AsyncClient(
                connection_string,
                maxPoolSize=cls._settings.max_pool_size,
                minPoolSize=cls._settings.min_pool_size,
                serverSelectionTimeoutMS=cls._settings.server_selection_timeout_ms,
                socketTimeoutMS=cls._settings.socket_timeout_ms,
                retryWrites=True,
            )
        
        return cls._async_client

    @classmethod
    async def get_async_db(cls) -> Any:
        """Get async MongoDB database."""
        if cls._async_db is None:
            client = await cls.get_async_client()
            if cls._settings is None:
                cls.initialize()
            cls._async_db = client[cls._settings.mongodb_database]
        
        return cls._async_db

    @classmethod
    def get_sync_client(cls) -> MongoClient:
        """Get sync MongoDB client for migrations/scripts."""
        if cls._sync_client is None:
            if cls._settings is None:
                cls.initialize()
            
            connection_string = cls._settings.build_connection_string()
            cls._sync_client = MongoClient(
                connection_string,
                maxPoolSize=cls._settings.max_pool_size,
                minPoolSize=cls._settings.min_pool_size,
                serverSelectionTimeoutMS=cls._settings.server_selection_timeout_ms,
                socketTimeoutMS=cls._settings.socket_timeout_ms,
                retryWrites=True,
            )
        
        return cls._sync_client

    @classmethod
    def get_sync_db(cls):
        """Get sync MongoDB database for migrations/scripts."""
        client = cls.get_sync_client()
        if cls._settings is None:
            cls.initialize()
        return client[cls._settings.mongodb_database]

    @classmethod
    async def close_async(cls) -> None:
        """Close async MongoDB client."""
        if cls._async_client is not None:
            cls._async_client.close()
            cls._async_client = None
            cls._async_db = None

    @classmethod
    def close_sync(cls) -> None:
        """Close sync MongoDB client."""
        if cls._sync_client is not None:
            cls._sync_client.close()
            cls._sync_client = None

    @classmethod
    async def health_check(cls) -> bool:
        """Check MongoDB connection health."""
        try:
            db = await cls.get_async_db()
            await db.command("ping")
            return True
        except Exception as e:
            print(f"MongoDB health check failed: {e}")
            return False


# Convenient database access
async def get_db() -> Any:
    """Dependency for FastAPI to inject database."""
    return await MongoDBConnection.get_async_db()
