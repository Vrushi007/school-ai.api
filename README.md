# School AI API

A Flask-based REST API for generating educational lesson plans and detailed session content using OpenAI's GPT models.

## Features

- **Lesson Plan Generation**: Create structured lesson plans for Indian school standards (CBSE/NCERT)
- **Detailed Session Content**: Generate comprehensive lesson content for individual sessions
- **Modular Architecture**: Clean, maintainable code structure
- **Auto-reload**: Development mode with automatic reloading

## API Endpoints

### 1. Generate Lesson Plan

```
POST /api/generate-lesson-plan
```

**Request:**

```json
{
  "subjectName": "Physics",
  "className": "10th",
  "chapterTitle": "Light - Reflection and Refraction",
  "numberOfSessions": 5,
  "defaultSessionDuration": "40 minutes"
}
```

### 2. Generate Detailed Session Content

```
POST /api/generate-detailed-content-for-session
```

**Request:**

```json
{
  "sessionData": {
    "title": "Introduction to Light and its Properties",
    "summary": "Session overview...",
    "duration": "40 minutes",
    "objectives": ["objective1", "objective2", "objective3"]
  },
  "subjectName": "Physics",
  "className": "10th"
}
```

## Project Structure

```
shool-ai.api/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── services/
│   └── openai_service.py # OpenAI API integration
├── utils/
│   └── json_parser.py    # JSON parsing utilities
└── routes/
    └── lesson_plan.py    # API route handlers
```

## Setup

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd shool-ai.api
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the application:**
   ```bash
   python app.py
   # or
   flask run
   ```

## Environment Variables

Create a `.env` file with:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Development

The application runs in debug mode by default, which provides:

- Automatic reloading when files change
- Detailed error messages
- Interactive debugger

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]
