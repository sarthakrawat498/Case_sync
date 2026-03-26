# CaseSync Database Setup Guide

## Current Status: Fixed! ✅

The application has been configured to use SQLite by default for easier development. No PostgreSQL setup required!

## Quick Start (Recommended)

The app is now configured with SQLite database. Just run the backend:

```bash
cd backend
uvicorn main:app --reload
```

The SQLite database file `casesync.db` will be created automatically in the backend directory.

## Alternative: PostgreSQL Setup

If you prefer PostgreSQL, follow these steps:

### Option 1: Install PostgreSQL and Create Database

1. **Install PostgreSQL:**
   - Download from: https://www.postgresql.org/download/windows/
   - During installation, remember the password you set for the `postgres` user

2. **Create the database:**

   ```sql
   -- Connect to PostgreSQL as postgres user
   psql -U postgres -h localhost

   -- Create the database
   CREATE DATABASE casesync;

   -- Exit
   \q
   ```

3. **Update .env file:**
   ```env
   # Replace with your PostgreSQL password
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/casesync
   ```

### Option 2: Use Docker PostgreSQL

```bash
# Start PostgreSQL in Docker
docker run --name casesync-postgres -e POSTGRES_DB=casesync -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:13

# Update .env file
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/casesync
```

### Option 3: Reset PostgreSQL Password

If you have PostgreSQL installed but forgot the password:

```bash
# Stop PostgreSQL service
net stop postgresql-x64-13

# Start in single-user mode (run as Administrator)
postgres --single -D "C:\Program Files\PostgreSQL\13\data" postgres

# In single-user mode:
ALTER USER postgres PASSWORD 'newpassword';

# Exit and restart service
net start postgresql-x64-13
```

## Switching Between Databases

### Current: SQLite (Default)

```env
DATABASE_URL=sqlite:///./casesync.db
```

### Switch to PostgreSQL

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/casesync
```

Just update the DATABASE_URL in your `.env` file and restart the application.

## Troubleshooting

### SQLite Issues

- **Permission errors**: Run terminal as Administrator
- **Database locked**: Close all connections and restart the app

### PostgreSQL Issues

- **Connection refused**: Ensure PostgreSQL service is running
- **Password errors**: Reset password using instructions above
- **Database doesn't exist**: Create it using `CREATE DATABASE casesync;`
- **Port conflicts**: Change port in DATABASE_URL if 5432 is taken

## Database Features

Both SQLite and PostgreSQL support all CaseSync features:

- ✅ Case management
- ✅ Audio transcription storage
- ✅ Entity extraction
- ✅ FIR draft generation
- ✅ Review workflow
- ✅ PDF export

**Note**: PostgreSQL is recommended for production, SQLite is perfect for development.
