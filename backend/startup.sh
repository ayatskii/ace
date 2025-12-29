#!/bin/bash
echo "🚀 Starting ACE Platform Backend..."
echo "📦 Running database initialization..."
python seed_init.py
echo "🌐 Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
