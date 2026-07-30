# Environment Variables

Ensure the following variables are configured in your Render Web Service dashboard under the "Environment" tab.

| Variable | Description | Required | Example |
|---|---|---|---|
| `ENVIRONMENT` | `production` | Yes | `production` |
| `DATABASE_PROVIDER` | Must be `supabase` | Yes | `supabase` |
| `SUPABASE_URL` | Supabase project URL | Yes | `https://xyz.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase Anon Key | Yes | `eyJ...` |
| `SUPABASE_DB_HOST` | Database host | Yes | `db.xyz.supabase.co` |
| `SUPABASE_DB_PORT` | Database port | Yes | `5432` |
| `SUPABASE_DB_NAME` | Database name | Yes | `postgres` |
| `SUPABASE_DB_USER` | Database user | Yes | `postgres` |
| `SUPABASE_DB_PASSWORD` | Database password | Yes | `supersecret` |
| `GROQ_API_KEY` | Default LLM Provider Key | Yes | `gsk_...` |
| `TAVILY_API_KEY` | Search API Key | Yes | `tvly-...` |
| `LOG_LEVEL` | Application log level | No | `INFO` |

**DO NOT configure `PORT`.** Render automatically injects `PORT`.
