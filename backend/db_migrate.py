"""Database migration and setup script."""

import asyncio
import sys
from db.config import MongoDBConnection, MongoDBSettings
from db.indexes import IndexManager


async def setup_database() -> None:
    """Initialize MongoDB connection and create indexes."""
    print("🔄 Setting up MongoDB database...")
    
    # Initialize connection
    settings = MongoDBSettings()
    MongoDBConnection.initialize(settings)
    
    # Check connection
    print(f"📡 Connecting to MongoDB: {settings.mongodb_url}")
    print(f"📚 Database: {settings.mongodb_database}")
    
    db = await MongoDBConnection.get_async_db()
    
    # Verify connection
    is_healthy = await MongoDBConnection.health_check()
    if not is_healthy:
        print("✗ Database health check failed!")
        return False
    
    print("✓ Connected to MongoDB successfully")
    
    # Get database info
    try:
        server_info = await db.client.server_info()
        print(f"✓ MongoDB version: {server_info.get('version')}")
    except Exception as e:
        print(f"⚠ Could not get server info: {e}")
    
    # Create indexes
    print("\n🔨 Creating indexes...")
    try:
        await IndexManager.create_all_indexes(db)
        print("✓ All indexes created successfully")
    except Exception as e:
        print(f"✗ Failed to create indexes: {e}")
        return False
    
    # Get index statistics
    print("\n📊 Index Statistics:")
    stats = await IndexManager.get_index_stats(db)
    for collection_name, collection_stats in stats.items():
        print(f"  {collection_name}: {collection_stats['index_count']} indexes")
    
    # Close connection
    await MongoDBConnection.close_async()
    print("\n✓ Database setup complete!")
    return True


async def reset_database() -> None:
    """Drop all collections (use with caution!)."""
    print("⚠️  WARNING: This will delete all data!")
    response = input("Type 'yes' to confirm: ")
    
    if response.lower() != "yes":
        print("Cancelled.")
        return
    
    settings = MongoDBSettings()
    MongoDBConnection.initialize(settings)
    db = await MongoDBConnection.get_async_db()
    
    # Drop all collections
    collections = await db.list_collection_names()
    for collection_name in collections:
        await db[collection_name].drop()
        print(f"✓ Dropped collection: {collection_name}")
    
    await MongoDBConnection.close_async()
    print("✓ Database reset complete")


async def migrate_legacy_data() -> None:
    """Migration helper for legacy data (customize as needed)."""
    print("🔄 Migrating legacy data...")
    
    settings = MongoDBSettings()
    MongoDBConnection.initialize(settings)
    db = await MongoDBConnection.get_async_db()
    
    # Example migration: Add fields to existing documents
    # Customize based on your needs
    
    print("✓ Migration complete")
    await MongoDBConnection.close_async()


async def main() -> None:
    """Main CLI handler."""
    if len(sys.argv) < 2:
        print("Usage: python db_migrate.py [setup|reset|migrate]")
        return
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        await setup_database()
    elif command == "reset":
        await reset_database()
    elif command == "migrate":
        await migrate_legacy_data()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: setup, reset, migrate")


if __name__ == "__main__":
    asyncio.run(main())
