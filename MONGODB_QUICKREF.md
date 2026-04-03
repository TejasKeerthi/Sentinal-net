# MongoDB Quick Reference

## Common Operations

### Start/Stop MongoDB

```bash
# Docker
docker-compose up -d mongodb          # Start
docker-compose down                   # Stop

# Local (macOS)
brew services start mongodb-community
brew services stop mongodb-community

# Local (Linux)
sudo systemctl start mongodb
sudo systemctl stop mongodb
```

### Connect to MongoDB

```bash
# Local
mongosh

# With authentication
mongosh -u admin -p password --authenticationDatabase admin

# Docker container
docker-compose exec mongodb mongosh

# MongoDB Atlas
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/"
```

### Database Initialization

```bash
# Setup all indexes and configuration
cd backend
python db_migrate.py setup

# Reset database (destroys all data!)
python db_migrate.py reset

# Run migrations
python db_migrate.py migrate
```

## MongoDB Shell Commands

### Database Operations

```javascript
// Show all databases
show dbs

// Use database
use sentinel_net

// Show all collections
show collections

// Check database size
db.stats()

// Get database info
db.adminCommand("dbStats")
```

### Collection Operations

```javascript
// Count documents
db.risk_assessments.countDocuments()

// Find documents
db.signals.find()                        // All
db.signals.find({ status: "urgent" })    // Filtered
db.signals.find().limit(10)             // Limited
db.signals.find().sort({ timestamp: -1 }) // Sorted

// Pretty print
db.signals.findOne().pretty()

// Check collection size
db.signals.stats()

// Distinct values
db.signals.distinct("source")

// Get indexes
db.signals.getIndexes()
```

### Insert/Update Operations

```javascript
// Insert one
db.signals.insertOne({
  source: "commit",
  status: "neutral",
  title: "Test signal",
  timestamp: new Date()
})

// Insert many
db.signals.insertMany([{...}, {...}])

// Update one
db.signals.updateOne(
  { _id: ObjectId("...") },
  { $set: { status: "urgent" } }
)

// Update many
db.signals.updateMany(
  { source: "alert" },
  { $set: { status: "neutral" } }
)

// Replace
db.signals.replaceOne(
  { _id: ObjectId("...") },
  { new: "document" }
)
```

### Delete Operations

```javascript
// Delete one
db.signals.deleteOne({ _id: ObjectId("...") })

// Delete many
db.signals.deleteMany({ status: "neutral" })

// Delete all (careful!)
db.signals.deleteMany({})

// Drop collection
db.signals.drop()

// Drop database
db.dropDatabase()
```

### Aggregation Examples

```javascript
// Average risk score
db.risk_assessments.aggregate([
  {
    $group: {
      _id: null,
      avg_risk: { $avg: "$failure_risk_score" },
      max_risk: { $max: "$failure_risk_score" },
      count: { $sum: 1 }
    }
  }
])

// Signals by status
db.signals.aggregate([
  {
    $group: {
      _id: "$status",
      count: { $sum: 1 },
      avg_severity: { $avg: "$severity" }
    }
  },
  { $sort: { count: -1 } }
])

// Recent signals with limit
db.signals.aggregate([
  { $sort: { timestamp: -1 } },
  { $limit: 10 },
  { $project: { title: 1, status: 1, severity: 1, timestamp: 1 } }
])

// Signals over time period
db.signals.aggregate([
  {
    $match: {
      timestamp: {
        $gte: ISODate("2024-01-01"),
        $lte: ISODate("2024-01-31")
      }
    }
  },
  {
    $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$timestamp" } },
      count: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } }
])
```

## Index Operations

```javascript
// List all indexes
db.signals.getIndexes()

// Create index
db.signals.createIndex({ "timestamp": -1 })
db.signals.createIndex({ "status": 1, "timestamp": -1 })

// Create unique index
db.repositories.createIndex({ "repository_url": 1 }, { unique: true })

// Create text search index
db.signals.createIndex({ "title": "text", "description": "text" })

// Drop index
db.signals.dropIndex("timestamp_-1")
db.signals.dropIndex("*")  // Drop all except _id

// Index information
db.signals.getIndexes()
db.signals.stats()
```

## Validation Operations

```javascript
// Get schema validation rules
db.getCollectionInfos({ name: "risk_assessments" })

// Validate collection
db.validateCollection("signals")

// Check document validity
db.risk_assessments.findOne()  // Will error if invalid
```

## Backup & Restore

```bash
# Backup all databases
mongodump --out /path/to/backup

# Backup specific database
mongodump --db sentinel_net --out /path/to/backup

# Backup specific collection
mongodump --db sentinel_net --collection signals --out /path/to/backup

# Restore all databases
mongorestore /path/to/backup

# Restore specific database
mongorestore --db sentinel_net /path/to/backup/sentinel_net

# Backup to archive
mongodump --uri "mongodb://localhost:27017" --archive="backup.archive"

# Restore from archive
mongorestore --archive="backup.archive"
```

## User Management

```javascript
// Create user
db.createUser({
  user: "sentinel_app",
  pwd: "secure_password",
  roles: [
    { role: "readWrite", db: "sentinel_net" }
  ]
})

// List users
db.getUsers()

// Update user password
db.changeUserPassword("sentinel_app", "new_password")

// Grant role
db.grantRolesToUser("sentinel_app", [{ role: "readWrite", db: "sentinel_net" }])

// Revoke role
db.revokeRolesFromUser("sentinel_app", [{ role: "readWrite", db: "sentinel_net" }])

// Delete user
db.dropUser("sentinel_app")
```

## Monitoring

```javascript
// Server info
db.adminCommand("serverInfo")

// Connection info
db.adminCommand("connPoolStats")

// Current operations
db.currentOp()

// Kill operation
db.killOp(opid)

// Profiling level (0=off, 1=slow, 2=all)
db.setProfilingLevel(1, { slowms: 100 })

// Get profiling status
db.getProfilingLevel()
db.getProfilingStatus()

// View slow queries
db.system.profile.find({ millis: { $gt: 100 } }).sort({ ts: -1 }).limit(10)
```

## Performance Tips

```javascript
// Explain query
db.signals.find({ status: "urgent" }).explain("executionStats")

// Index size
Object.keys(db.signals.getIndexes()).forEach(i => {
  print(db.signals.getIndexes()[i])
})

// Find unused indexes
db.signals.aggregate([
  { $indexStats: {} }
])
```

## Replication (Replica Set)

```javascript
// Initialize replica set
rs.initiate()

// Check replica set status
rs.status()

// Get replica set configuration
rs.config()

// Add secondary
rs.add("host:port")

// Remove member
rs.remove("host:port")

// Check primary
rs.isMaster()
```

## FastAPI Integration

### Python Code Examples

```python
# Using Database class
from db.database import Database
from db.config import get_db

@app.get("/api/signals")
async def get_signals(db: Database = Depends(get_database)):
    return await db.get_signals(limit=50)

# Using raw motor
from motor.motor_asyncio import AsyncDatabase

@app.get("/api/custom")
async def custom_query(db: AsyncDatabase = Depends(get_db)):
    result = await db.signals.find_one({"status": "urgent"})
    return result
```

## Useful Queries

### Find highest risk assessments (last 7 days)

```javascript
db.risk_assessments.find({
  timestamp: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
}).sort({ failure_risk_score: -1 }).limit(10)
```

### Count urgent signals by source

```javascript
db.signals.aggregate([
  { $match: { status: "urgent" } },
  { $group: { _id: "$source", count: { $sum: 1 } } }
])
```

### Find repositories with most signals

```javascript
db.signals.aggregate([
  { $group: { _id: "$repository_url", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])
```

### Average metrics over time

```javascript
db.trends.aggregate([
  { $match: { metric_name: "bug_growth" } },
  { $unwind: "$data_points" },
  {
    $group: {
      _id: null,
      avg: { $avg: "$data_points.value" },
      max: { $max: "$data_points.value" },
      min: { $min: "$data_points.value" }
    }
  }
])
```

### Recent audit activity

```javascript
db.audit_logs.find().sort({ timestamp: -1 }).limit(20)
```

## Environment Variables Reference

```bash
# Connection
MONGODB_URL                          # Connection string
MONGODB_DATABASE                     # Database name
MONGODB_USERNAME                     # Username (optional)
MONGODB_PASSWORD                     # Password (optional)
MONGODB_REPLICA_SET                  # Replica set name (for transactions)

# Pooling
MONGODB_MAX_POOL_SIZE=50            # Max connections
MONGODB_MIN_POOL_SIZE=10            # Min connections
MONGODB_SERVER_SELECTION_TIMEOUT_MS  # Server selection timeout
MONGODB_SOCKET_TIMEOUT_MS           # Socket timeout

# Features
MONGODB_ENABLE_TRANSACTIONS=true    # Enable ACID transactions
```

## Error Handling

```python
# Connection error
try:
    db = await get_db()
except Exception as e:
    print(f"Connection failed: {e}")

# Validation error
try:
    await db.save_risk_assessment(assessment)
except ValidationError as e:
    print(f"Invalid assessment: {e}")

# Duplicate key error
from pymongo.errors import DuplicateKeyError
try:
    await db.save_repository(repo)
except DuplicateKeyError:
    print("Repository already exists")
```

## Further Help

- MongoDB Docs: https://docs.mongodb.com/
- Motor Guide: https://motor.readthedocs.io/
- Pymongo Reference: https://pymongo.readthedocs.io/
- FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
