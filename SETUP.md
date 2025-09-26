# 🎓 AI Timetable Generator - Setup Guide

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** 
- **Node.js 16+** and **npm**
- **Git**
- **Supabase Account** (for database)

## 🚀 Quick Setup

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd TIMETABLE
```

### 2. Environment Setup

**IMPORTANT**: Never commit your `.env` file with real credentials!

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual credentials
nano .env  # or use your preferred editor
```

Update `.env` with your actual values:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=your_generated_secret_key
```

### 3. Backend Setup (Python/FastAPI)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Database Setup

1. Create a Supabase project at https://supabase.com
2. Run the database schema:
   ```bash
   # Copy contents of database_schema.sql and run in Supabase SQL editor
   ```
3. Update your `.env` with Supabase credentials

### 5. Frontend Setup (React/Vite)

```bash
# Install dependencies
npm install
```

## 🏃‍♂️ Running the Application

### Start Backend (Terminal 1)
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend (Terminal 2)
```bash
# Start React development server
npm run dev
```

## 🌐 Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🛠️ Development Commands

### Backend
```bash
# Run with reload (development)
uvicorn main:app --reload

# Run tests (when implemented)
pytest

# Check code formatting
black app/ main.py

# Type checking
mypy app/ main.py
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 📊 Database Schema

The project uses these main tables:
- `programs` - Academic programs (B.Ed, M.Ed, etc.)
- `faculty` - Faculty information and availability
- `courses` - Course catalog
- `rooms` - Classroom management
- `time_slots` - Available time periods
- `constraints` - Scheduling rules
- `generated_timetables` - Generated schedules

## 🔧 Configuration

### Environment Variables
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `SECRET_KEY` - JWT secret key
- `ALGORITHM` - JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration

### API Configuration
- CORS is configured for `localhost:5173` and `localhost:3000`
- API runs on port 8000 by default
- Frontend runs on port 5173 by default

## 🚨 Common Issues

### Backend Issues
1. **Import errors**: Ensure virtual environment is activated
2. **Database connection**: Check Supabase credentials in `.env`
3. **Port conflicts**: Change port with `--port 8001`

### Frontend Issues
1. **Node version**: Ensure Node.js 16+ is installed
2. **Dependencies**: Run `npm ci` for clean install
3. **API connection**: Check if backend is running on port 8000

### Database Issues
1. **Schema errors**: Ensure database_schema.sql is executed
2. **Connection errors**: Verify Supabase URL and key
3. **Permissions**: Check Supabase RLS policies

## 📚 Project Structure

```
TIMETABLE/
├── app/                    # Backend application
│   ├── database.py        # Database connection
│   ├── models.py          # Pydantic models
│   ├── generator.py       # Timetable generation logic
│   └── export_utils.py    # Export functionality
├── src/                   # Frontend source
│   ├── components/        # React components
│   ├── pages/            # Page components
│   └── services/         # API services
├── main.py               # FastAPI application
├── requirements.txt      # Python dependencies
├── package.json         # Node.js dependencies
└── database_schema.sql  # Database schema
```

## 🔒 Security Notes

1. **Never commit `.env` files** with real credentials
2. **Use `.env.example`** for template
3. **Generate strong SECRET_KEY** for JWT
4. **Use environment-specific configs** for production

## 🚀 Deployment

For production deployment:
1. Use environment variables instead of `.env` files
2. Set up proper database with backups
3. Configure CORS for your domain
4. Use HTTPS
5. Set up monitoring and logging

## 📞 Support

If you encounter issues:
1. Check the logs in terminal
2. Verify environment variables
3. Ensure all dependencies are installed
4. Check database connection

Happy coding! 🎉