# MongoDB replication (development demo)

## Concepts

| Term | Meaning |
|------|--------|
| **Replication** | Copying data to secondary nodes for redundancy |
| **Primary** | Node that accepts writes |
| **Secondary** | Node that replicates the primary's data |
| **Replica set** | Named group of MongoDB nodes (`rs0`) |
| **Sharding** | Splitting data across shards (not required for this project) |
| **Backup** | Point-in-time export (`scripts/backup_db.py`) — not the same as replication |

## Single-member replica set (Windows lab)

For a college demo on one PC, a **one-member replica set** still uses real replica-set machinery (`replSetInitiate`, `replSetGetStatus`).

1. Stop the default MongoDB Windows service if it conflicts with custom config.
2. Start `mongod` with replication enabled (example):

```powershell
mongod --dbpath C:\data\rs0 --replSet rs0 --port 27017 --bind_ip 127.0.0.1
```

3. Initialize:

```powershell
python scripts\init_replica_set.py
```

4. Update `.env`:

```env
MONGODB_URI=mongodb://127.0.0.1:27017/?replicaSet=rs0
```

5. Verify:

```powershell
mongosh --eval "rs.status()"
```

## Three-node demo (optional, advanced)

Run three `mongod` processes on ports **27017**, **27018**, **27019** with separate `--dbpath` folders and add three members in `replSetInitiate`. Document screenshots of `rs.status()` for your report.

## Failover testing (safe)

- Only on **fictional** dev data.
- Stop the primary process; elect a new primary in multi-member sets.
- Never test failover on production or real patient data.
