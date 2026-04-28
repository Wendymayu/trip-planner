# Trip Planner

A trip planning application with Python FastAPI backend.

## Project Structure

```
trip-planner/
├── backend/          # Python FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Configuration
│   │   ├── models/   # Database models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # Business logic
│   └── tests/        # Tests
└── frontend/         # Frontend (TBD)
```

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

The API will be available at http://localhost:8000

## License

MIT
