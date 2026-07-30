import uvicorn
import sys
from pathlib import Path

# Add backend/app directory to sys path so absolute imports like 'from api...' work
app_dir = Path(__file__).resolve().parent / "app"
sys.path.append(str(app_dir))

if __name__ == "__main__":
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)
