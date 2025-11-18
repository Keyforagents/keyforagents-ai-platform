# Keyforagents AI Platform Backend

This backend is powered by FastAPI and integrates with Supabase for database operations. Environment variables needed for configuration are defined in `.env.example`.

## Setup

1. Install dependencies:
   pip install -r requirements.txt
2. Copy `.env.example` to `.env` and update with your credentials.
3. Run using:
   uvicorn main:app --reload

## Endpoints
- `/` - Health check endpoint

## Repo Structure
- requirements.txt: Python dependencies
- main.py: FastAPI entrypoint
- .env.example: Environment template

For more details, see DEPLOYMENT_STATUS.md.