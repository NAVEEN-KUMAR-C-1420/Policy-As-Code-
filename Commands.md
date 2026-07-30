 ## Create a new virtual environment

## From the backend directory:

cd backend
python -m venv .venv

## Activate it:

Windows
.\.venv\Scripts\activate

## Install backend requirements

pip install --upgrade pip
pip install -r requirements.txt

## Verify backend

python scripts/verify_project.py
python tests/run_all_tests.py
python -c "from api.main import app; print('Backend Import Successful')"
uvicorn api.main:app --reload

 ## Open

http://127.0.0.1:8000/docs
and
http://127.0.0.1:8000/health

## Frontend

## Open another terminal.

cd frontend
npm install

## Start

npm run dev

http://localhost:5173

## Running Backend Only

.\.venv\Scripts\activate
uvicorn api.main:app --reload

## Running Frontend Only

cd frontend
npm install
npm run dev


## Running Both Together


## Terminal 1

cd backend
.\.venv\Scripts\activate
uvicorn api.main:app --reload

## Terminal 2

cd frontend
npm run dev