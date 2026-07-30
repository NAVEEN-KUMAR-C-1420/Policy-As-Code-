# Troubleshooting

**1. Application crashes immediately on startup**
Check Render Logs. Ensure `DATABASE_PROVIDER=supabase` and all Supabase connection variables are provided.

**2. 401 Unauthorized from LLM**
Ensure `GROQ_API_KEY` (or the default LLM provider key) is correctly set in Render.

**3. Application binds to 8000 but Render says Healthcheck failed**
Render requires the application to bind to `$PORT` (injected by Render). Verify `uvicorn api.main:app --host 0.0.0.0 --port $PORT` is the exact start command in `render.yaml`.

**4. Subprocess/Pipeline failures**
Verify `TAVILY_API_KEY` is present. Ensure python dependencies are completely synced with `requirements.txt`.
