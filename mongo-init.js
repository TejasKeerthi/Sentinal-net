// MongoDB replica set initialization script
// Runs automatically when container starts

// Initialize replica set for transaction support
rs.initiate(
  {
    _id: "rs0",
    version: 1,
    members: [
      { _id: 0, host: "mongodb:27017", priority: 1 }
    ]
  }
);

// Wait for replica set initialization
let isReady = false;
let attempts = 0;

while (!isReady && attempts < 30) {
  try {
    const status = rs.status();
    if (status.ok === 1) {
      isReady = true;
      print("✓ Replica set initialized successfully");
    }
  } catch (e) {
    print("⏳ Waiting for replica set to initialize...");
    sleep(1000);
    attempts++;
  }
}

// Create sentinel_net database
db = db.getSiblingDB('sentinel_net');

// Create collections with schema validation
db.createCollection("risk_assessments", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["failure_risk_score", "timestamp"],
      properties: {
        failure_risk_score: {
          bsonType: "int",
          description: "Risk score 0-100",
          minimum: 0,
          maximum: 100
        },
        risk_level: {
          enum: ["low", "medium", "high", "critical"]
        },
        timestamp: {
          bsonType: "date"
        }
      }
    }
  }
});

db.createCollection("signals", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["source", "status", "title", "severity", "timestamp"],
      properties: {
        source: {
          enum: ["commit", "issue", "alert", "metric"]
        },
        status: {
          enum: ["neutral", "negative", "urgent"]
        }
      }
    }
  }
});

db.createCollection("trends");
db.createCollection("ai_insights");
db.createCollection("repositories");
db.createCollection("risk_reports");
db.createCollection("audit_logs");
db.createCollection("archived_trends");

print("✓ Collections created successfully");

// Create admin user (already created by MONGO_INITDB_ROOT_USERNAME)
// Create application user with specific permissions
db.createUser({
  user: "sentinel_app",
  pwd: "app_password_change_me",
  roles: [
    {
      role: "readWrite",
      db: "sentinel_net"
    }
  ]
});

print("✓ Application user created");
print("✓ MongoDB initialization complete");
