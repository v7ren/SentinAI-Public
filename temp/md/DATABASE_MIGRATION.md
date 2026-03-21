# Sentinel AI - Database Migration Guide

This guide covers the migration from the JSON-based database to a proper SQL database (SQLite by default, but supports PostgreSQL, MySQL, etc.).

## Overview

The migration moves the SAST tool's data from a single `sentinel_db.json` file to a relational SQL database with the following structure:

- **Users** - Top-level entity
- **Projects** - Belong to users
- **Scans** - Belong to projects
- **Vulnerabilities** - Files with security issues (belong to scans)
- **Issues** - Individual security findings (belong to vulnerabilities)
- **KeywordsDetected** - Keywords detected per issue
- **PoCScripts** - Proof of Concept scripts per issue
- **ProjectAnalysis** - Project metadata per scan
- **ExternalApis & TopConcerns** - Related to project analysis

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or install SQLAlchemy directly:
```bash
pip install SQLAlchemy>=2.0.0
```

### 2. Run the Migration

```bash
# Basic migration (creates sentinel.db in current directory)
python migrate_json_to_sql.py

# With custom paths
python migrate_json_to_sql.py --json sentinel_db.json --db sqlite:///sentinel.db

# With validation
python migrate_json_to_sql.py --validate

# Dry run (preview only)
python migrate_json_to_sql.py --dry-run
```

### 3. Use the New Backend

Replace `main4.py` with the SQL-enabled version:

```bash
# Option 1: Use the new file directly
python backend/main_sql.py

# Option 2: Replace the old file (backup first!)
cp backend/main4.py backend/main4.py.backup
cp backend/main_sql.py backend/main4.py
python backend/main4.py
```

## Database Schema

```
users
  ├── id (PK, string)
  ├── created_at
  └── updated_at

projects
  ├── id (PK, string)
  ├── user_id (FK)
  ├── name
  └── created_at

scans
  ├── id (PK, string)
  ├── project_id (FK)
  ├── scan_type
  ├── timestamp
  ├── project_name
  ├── files_scanned
  ├── vulnerabilities_count
  └── elapsed_seconds

vulnerabilities
  ├── id (PK, auto)
  ├── scan_id (FK)
  ├── filename
  ├── status
  └── source_code

issues
  ├── id (PK, auto)
  ├── vulnerability_id (FK)
  ├── severity
  ├── type
  ├── subtype
  ├── trigger
  ├── line
  ├── description
  ├── vulnerable_code
  ├── impact_summary
  ├── confidence_score
  ├── cwe_id
  ├── remediation (JSON)
  ├── consequences
  ├── references (JSON)
  ├── fingerprint
  ├── cvss_score
  ├── fix_complexity
  └── code_context_* (JSON fields)

keywords_detected
  ├── id (PK, auto)
  ├── issue_id (FK)
  ├── keyword
  ├── line
  └── context

poc_scripts
  ├── id (PK, auto)
  ├── issue_id (FK)
  ├── language
  ├── script
  └── exploit_type

project_analyses
  ├── id (PK, auto)
  ├── scan_id (FK)
  ├── project_name
  ├── framework
  ├── description
  ├── has_authentication
  └── has_database

external_apis & top_concerns
  └── Related to project_analyses
```

## Configuration

### Environment Variables

```bash
# Database connection (SQLite default)
export DATABASE_URL="sqlite:///sentinel.db"

# For PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost/sentinel"

# For MySQL
export DATABASE_URL="mysql+pymysql://user:password@localhost/sentinel"

# Worker configuration
export WORKER_NODES="http://127.0.0.1:5002,http://127.0.0.1:5003"
export WORKER_SECRET="your-secret-here"

# Performance tuning
export MAX_WORKERS="5"
export MAX_FILE_SIZE_BYTES="1000000"
```

### Using PostgreSQL

1. Install the driver:
```bash
pip install psycopg2-binary
```

2. Create the database:
```sql
CREATE DATABASE sentinel;
```

3. Run migration with PostgreSQL:
```bash
python migrate_json_to_sql.py --db "postgresql://user:pass@localhost/sentinel"
```

### Using MySQL

1. Install the driver:
```bash
pip install pymysql
```

2. Run migration with MySQL:
```bash
python migrate_json_to_sql.py --db "mysql+pymysql://user:pass@localhost/sentinel"
```

## API Changes

The new backend maintains backward compatibility with the existing API:

### Unchanged Endpoints
- `POST /api/scan/stream` - Streaming scan
- `POST /api/scan/pocs` - Generate PoCs
- `GET /api/scan/docs/<scan_id>` - Get DeepWiki docs
- `GET /api/projects/<user_id>` - Get user projects
- `GET /api/poc/<user_id>/<scan_id>/<fingerprint>` - Download PoC

### New Endpoints
- `GET /api/scans/<user_id>/<project_name>` - Get scans for a project
- `GET /api/scan/<user_id>/<project_name>/<scan_id>` - Get full scan details
- `GET /api/health` - Health check (database + workers)

## Migration Validation

After migration, verify the data:

```python
from backend.database import init_database

db = init_database("sqlite:///sentinel.db")

# Get migration stats
with db.get_session() as session:
    from backend.database.models import User, Project, Scan, Vulnerability, Issue
    
    print(f"Users: {session.query(User).count()}")
    print(f"Projects: {session.query(Project).count()}")
    print(f"Scans: {session.query(Scan).count()}")
    print(f"Vulnerabilities: {session.query(Vulnerability).count()}")
    print(f"Issues: {session.query(Issue).count()}")
```

## Troubleshooting

### Migration Errors

1. **JSON file not found**: Ensure `sentinel_db.json` exists in the project root
2. **Permission errors**: Check write permissions for the database directory
3. **Memory errors**: For large databases, the migration is chunked automatically

### Database Connection Issues

1. **SQLite**: Ensure the directory exists and is writable
2. **PostgreSQL**: Verify the server is running and credentials are correct
3. **MySQL**: Check that the database exists before migrating

### Rollback

To rollback to JSON:
1. Restore your `sentinel_db.json` backup
2. Switch back to using `main4.py` (pre-SQL version)

## Performance Notes

- **SQLite**: Good for development and small deployments (up to ~100k issues)
- **PostgreSQL**: Recommended for production with many users/scans
- **Indexes**: The schema includes indexes on commonly queried fields
- **Lazy loading**: Database operations use lazy loading for related entities

## Security Considerations

1. **Database permissions**: Ensure the database file is readable only by the application
2. **Backups**: Regular backups of the database are recommended
3. **Encryption**: Consider encrypting sensitive fields at rest for production use

## Support

For issues or questions:
1. Check the migration log output
2. Verify database connectivity with the health endpoint
3. Review the SQLAlchemy documentation for database-specific issues
