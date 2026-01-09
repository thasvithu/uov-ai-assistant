# Phase 1 - Database Setup Guide

## Step 1: Run the SQL Schema

1. **Open Supabase Dashboard**
   - Go to https://supabase.com/dashboard
   - Select your project

2. **Open SQL Editor**
   - Click "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Copy and Run the Schema**
   - Open `shared/database_schema.sql`
   - Copy all the SQL code
   - Paste into Supabase SQL Editor
   - Click "Run" button

4. **Verify Tables Created**
   - Go to "Table Editor" in left sidebar
   - You should see:
     - `chat_sessions`
     - `chat_messages`
     - `feedback`
     - `request_logs`
     - `documents`

## Step 2: Test Database Connection

Run the test script:

```bash
python tests/test_database.py
```

This will:
- Test connection to Supabase
- Create a test session
- Save a test message
- Verify data was saved correctly
- Clean up test data

## Troubleshooting

**Error: "relation does not exist"**
- Make sure you ran the SQL schema in Supabase

**Error: "permission denied"**
- Check your `SUPABASE_KEY` is correct
- Verify Row Level Security (RLS) policies if enabled

**Error: "connection failed"**
- Check `SUPABASE_URL` is correct
- Verify internet connection
