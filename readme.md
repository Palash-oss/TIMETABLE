pip install reportlab
pip install ortools
pip install email-validator



backend first terminal
cd backend
pip install -r requirements.txt
# Create a .env file with your Supabase credentials

python -m venv venv
.\venv\Scripts\Activate
pip install uvicorn[standard] fastapi
uvicorn main:app --reload
pip install supabase


frontend second terminal
cd frontend
npm install
npm run dev



