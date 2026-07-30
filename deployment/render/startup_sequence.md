# FastAPI Startup Sequence

At startup, the `Lifespan` context manager in `api/main.py` explicitly handles validation:
1. Validates `.env` and `DATABASE_PROVIDER`
2. Asserts Supabase connection (if `DATABASE_PROVIDER=supabase`)
3. Asserts LLM API Key existence (Groq, OpenAI, etc.)
4. Loads Governance Middleware
5. Mounts routers
6. Binds to `$PORT` and starts accepting traffic.

If any of these fail, the startup crashes immediately before accepting traffic, preventing zombie containers.
