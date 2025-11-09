# AI Wiki Quiz Generator

An intelligent quiz generator that creates multiple-choice quizzes from Wikipedia articles using AI. Built with FastAPI (backend) and React + Vite (frontend).

## 🔗 Links

- **GitHub Repository**: [https://github.com/bsv29/Ai_Quiz_Generator](https://github.com/bsv29/Ai_Quiz_Generator)
- **Live Demo**: [Deploy your app using the instructions below]

## 🚀 Deployment

### Frontend Deployment (Vercel/Netlify)

1. **Vercel**:
   - Push your code to GitHub
   - Go to [vercel.com](https://vercel.com) and import your repository
   - Set the root directory to `frontend`
   - Set build command: `npm run build`
   - Set output directory: `dist`
   - Add environment variable: `VITE_API_URL` = your backend URL

2. **Netlify**:
   - Push your code to GitHub
   - Go to [netlify.com](https://netlify.com) and import your repository
   - Set base directory: `frontend`
   - Set build command: `npm run build`
   - Set publish directory: `frontend/dist`
   - Add environment variable: `VITE_API_URL` = your backend URL

### Backend Deployment (Railway/Render/Heroku)

1. **Railway**:
   - Push your code to GitHub
   - Go to [railway.app](https://railway.app) and create a new project
   - Connect your GitHub repository
   - Set the root directory to `backend`
   - Install dependencies: `pip install -r requirements.txt`
   - Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables: `GEMINI_API_KEY` (optional)

2. **Render**:
   - Push your code to GitHub
   - Go to [render.com](https://render.com) and create a new Web Service
   - Connect your GitHub repository
   - Set root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables as needed

3. **Heroku**:
   - Install Heroku CLI and login
   - Create a `Procfile` in the backend directory: `web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Run: `heroku create your-app-name`
   - Set config vars: `heroku config:set GEMINI_API_KEY=your_key`
   - Deploy: `git push heroku main`

## 📸 Screenshots

*Add screenshots of your application here*

## Features

- 🎯 **Wikipedia Integration**: Scrape and process Wikipedia articles
- 🤖 **AI-Powered Quiz Generation**: Generate intelligent multiple-choice questions
- 💾 **Quiz History**: Save and browse previously generated quizzes
- 🎨 **Modern UI**: Professional, responsive design with smooth animations
- 🔄 **Real-time Generation**: Fast quiz generation with loading states
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - Database ORM
- **BeautifulSoup4** - Web scraping
- **LangChain** - AI integration
- **SQLite** - Database

### Frontend
- **React** - UI library
- **Vite** - Build tool
- **CSS3** - Modern styling with animations

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
# Windows PowerShell
python -m venv venv
venv\Scripts\Activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Set up your Gemini API key:
```bash
# Windows PowerShell
$Env:GEMINI_API_KEY = "YOUR_KEY_HERE"

# Linux/Mac
export GEMINI_API_KEY="YOUR_KEY_HERE"
```

5. Run the backend server:
```bash
# From project root
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Or from backend directory
python main.py
```

The API will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### POST `/generate_quiz`
Generate a quiz from a Wikipedia URL.

**Request Body:**
```json
{
  "url": "https://en.wikipedia.org/wiki/Example"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Article Title",
  "summary": "Article summary...",
  "questions": [...],
  "keywords": [...],
  "source_url": "https://en.wikipedia.org/wiki/Example"
}
```

### GET `/history`
Get all generated quizzes.

**Response:**
```json
[
  {
    "id": 1,
    "url": "https://en.wikipedia.org/wiki/Example",
    "title": "Article Title",
    "date_generated": "2024-01-01T00:00:00"
  }
]
```

### GET `/quiz/{quiz_id}`
Get a specific quiz by ID.

**Response:**
```json
{
  "id": 1,
  "title": "Article Title",
  "summary": "Article summary...",
  "questions": [...],
  "keywords": [...]
}
```

## Project Structure

```
ai_quiz_generator/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── scraper.py           # Wikipedia scraper
│   ├── llm_quiz_generator.py # AI quiz generator
│   ├── requirements.txt     # Python dependencies
│   └── static/              # Static files
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   ├── App.jsx          # Main app component
│   │   └── main.jsx         # Entry point
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite configuration
└── README.md
```

## Usage

1. Start both the backend and frontend servers
2. Open `http://localhost:5173` in your browser
3. Enter a Wikipedia URL in the input field
4. Click "Generate Quiz" to create a quiz
5. View your quiz history in the History tab

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests (if configured)
cd frontend
npm test
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build

# Backend
# Use a production server like gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Environment Variables

- `GEMINI_API_KEY` - Google Gemini API key (optional, for enhanced AI features)
- `PORT` - Backend server port (default: 8000)
- `VITE_API_URL` - Frontend API URL (default: http://127.0.0.1:8000)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
