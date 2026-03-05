# School AI API

A Python web API application that integrates with AI providers (OpenAI, SarvamAI) to generate educational content including lesson plans, detailed session content, and questions for multiple education boards and curricula.

## Features

- **Multi-AI Provider Support**: Switch between OpenAI and SarvamAI using environment variables
- **Knowledge Point Generation**: Decompose curriculum content into atomic, teachable knowledge points aligned with curriculum standards, Bloom's Taxonomy, and IRT difficulty metrics
- **AI-Powered Session Planning**: Intelligently group knowledge points into teaching sessions respecting prerequisite dependencies
- **Session Summary Generation**: Generate teacher-focused instructional overviews and objectives for teaching sessions
- **Lesson Plan Generation**: Create structured lesson plans with multiple sessions
- **Detailed Session Content**: Generate comprehensive lesson content with activities, assessments, and resources
- **YouTube Integration**: Automatically fetch relevant educational videos based on session content
- **Question Generation**: Create diverse question sets with various difficulty levels and types
- **Student Q&A Chatbot**: Conversational AI assistant for student questions with context-aware responses
- **JSON Parser Integration**: Handles malformed AI responses gracefully
- **Multi-Board Support**: Works with various education boards (CBSE, ICSE, IB, State Boards, etc.)
- **RESTful API**: Clean, well-documented API endpoints
- **Error Handling**: Comprehensive error handling and logging

## Quick Start (Advanced Users)

```bash
# Clone and setup in one go
git clone <repository-url> && cd dummy-school-ai.api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-minimal.txt
cp .env.example .env
# Edit .env file to add your AI provider API key
python main.py
```

Then visit: http://localhost:8000/docs

## AI Provider Configuration

The API supports multiple AI providers. Switch between them using the `AI_PROVIDER` environment variable:

### Using OpenAI (Default)

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL_DEFAULT=gpt-4o-mini
```

### Using SarvamAI

```bash
AI_PROVIDER=sarvam
SARVAM_API_KEY=your-sarvam-api-key
SARVAM_API_BASE_URL=https://api.sarvam.ai/v1
SARVAM_MODEL_DEFAULT=sarvam-1
```

For detailed configuration options, see [AI_PROVIDER_GUIDE.md](AI_PROVIDER_GUIDE.md).

## API Endpoints

### Health Check

- `GET /` - Root endpoint with API status
- `GET /health` - Health check endpoint

### Knowledge Points

- `POST /api/generate-knowledge-points` - Generate curriculum-aligned knowledge points for a chapter

### Lesson Planning

- `POST /api/generate-lesson-plan` - Generate lesson plans with multiple sessions
- `POST /api/group-kps-into-sessions` - Intelligently group knowledge points into teaching sessions
- `POST /api/generate-session-summary` - Generate session summary and objectives from knowledge points
- `POST /api/generate-detailed-content-for-session` - Generate detailed session content with YouTube videos

### Assessment

- `POST /api/generate-questions` - Generate questions and assessments

### Student Support

- `POST /api/get-answers` - Student Q&A chatbot with conversation history support

## Setup Instructions

### Prerequisites

- Python 3.8 or higher (Python 3.13 tested and working)
- OpenAI API key (get one from https://platform.openai.com/api-keys)
- Git (for cloning the repository)

### Installation

1. **Clone or download the project**

   ```bash
   # If you have git, clone the repository:
   git clone <repository-url>
   cd dummy-school-ai.api

   # OR if you downloaded as ZIP, extract and navigate:
   cd dummy-school-ai.api
   ```

2. **Create and activate a virtual environment**

   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate it (macOS/Linux):
   source .venv/bin/activate

   # Activate it (Windows):
   .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   # Install required packages (pip will automatically install all dependencies):
   pip install -r requirements-minimal.txt
   ```

   > **Note**: The `requirements-minimal.txt` contains only the essential packages. Pip will automatically install all dependent packages (like starlette, anyio, etc.). If you want to pin exact versions of all packages, use `requirements.txt` instead.

4. **Configure OpenAI API key**

   ```bash
   # Option 1: Copy the example file and edit it
   cp .env.example .env
   # Then edit .env file in any text editor and replace the placeholders:
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   OPENAI_MODEL=gpt-4o-mini  # Optional - defaults to gpt-4o-mini

   # Option 2: Create .env file directly (macOS/Linux)
   echo "OPENAI_API_KEY=sk-your-actual-openai-api-key-here" > .env
   ```

   > **Important**: Never commit your `.env` file to git as it contains your secret API key!

5. **Run the application**

   ```bash
   # Method 1: Using Python directly (recommended)
   python main.py

   # Method 2: Using the startup script (macOS/Linux only)
   ./start.sh

   # Method 3: Using uvicorn directly
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

6. **Verify the installation**
   - Open your browser and go to: `http://localhost:8000`
   - You should see: `{"status":"healthy","message":"School AI API is running successfully"}`
   - API documentation: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

## API Usage Examples

### Generate Lesson Plan

```bash
curl -X POST "http://localhost:8000/api/generate-lesson-plan" \
     -H "Content-Type: application/json" \
     -d '{
       "subject_name": "Mathematics",
       "class_name": "8th",
       "chapter_title": "Linear Equations in One Variable",
       "number_of_sessions": 4,
       "default_session_duration": "45 minutes"
     }'
```

### Generate Session Content

```bash
curl -X POST "http://localhost:8000/api/generate-detailed-content-for-session" \
     -H "Content-Type: application/json" \
     -d '{
       "session_data": {
         "title": "Introduction to Linear Equations",
         "summary": "Basic concepts and solving simple linear equations",
         "duration": "45 minutes",
         "objectives": [
           "Understand what a linear equation is",
           "Identify variables and constants",
           "Solve simple linear equations",
           "Apply equations to real-world problems"
         ]
       },
       "subject_name": "Mathematics",
       "class_name": "8th"
     }'
```

### Generate Questions

```bash
curl -X POST "http://localhost:8000/api/generate-questions" \
     -H "Content-Type: application/json" \
     -d '{
       "class_name": "8th",
       "subject_name": "Mathematics",
       "chapters": ["Linear Equations", "Geometry"],
       "question_requirements": "Generate 20 questions with mix of MCQ, short answer, and long answer types"
     }'
```

### Expected Response Format

All API endpoints return responses in this standardized format:

**Success Response:**

```json
{
  "success": true,
  "data": {
    "lesson_plan": [...],     // or "session_content": {...}, or "questions": {...}
  },
  "message": "Operation completed successfully",
  "error": null
}
```

**Error Response:**

```json
{
  "success": false,
  "data": {
    "raw_response": "..." // Raw OpenAI response for debugging (if applicable)
  },
  "message": "Error description",
  "error": "Detailed error information"
}
```

## Project Structure

```
school-ai.api/
├── main.py                    # FastAPI application and routes
├── config.py                  # Configuration and app setup
├── models.py                  # Pydantic models for request/response
├── prompts.py                 # AI prompts for content generation
├── exceptions.py              # Custom exception handlers
├── routers/                   # API route modules
│   ├── __init__.py
│   ├── health.py              # Health check endpoints
│   ├── lesson_planning.py     # Lesson planning endpoints
│   ├── knowledge_points.py    # Knowledge point generation
│   ├── questions.py           # Question generation
│   └── student.py             # Student Q&A chatbot
├── services/                  # Business logic layer
│   ├── __init__.py
│   ├── openai_service.py      # OpenAI API integration
│   └── openai_helper.py       # OpenAI helper functions
├── helpers/                   # Helper modules
│   └── youtube.py             # YouTube video search integration
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── json_parser.py         # JSON parsing utilities
│   └── openai_logger.py       # OpenAI API logging
├── requirements.txt           # Complete Python dependencies
├── requirements-minimal.txt   # Minimal dependencies for basic setup
├── .env.example               # Environment variables template
├── .env                       # Environment variables (create from .env.example)
├── .gitignore                 # Git ignore file
├── test_api.py                # API testing script
├── test_json_parser.py        # JSON parser testing script
├── start.sh                   # Startup script
└── README.md                  # This file
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: OpenAI model to use (optional, defaults to `gpt-4o-mini`)

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running the application
- **OpenAI**: Official OpenAI Python client (v1.3.7 for compatibility)
- **Pydantic**: Data validation using Python type annotations
- **python-dotenv**: Load environment variables from .env file
- **httpx**: HTTP client (v0.24.1 for OpenAI compatibility)
- **requests**: HTTP library for testing

### Package Version Compatibility

This application uses specific package versions to ensure compatibility:

- `openai==1.3.7` - Latest stable version that works with httpx 0.24.1
- `httpx==0.24.1` - Compatible with OpenAI 1.3.7 (newer versions cause conflicts)
- `fastapi==0.104.1` - Stable FastAPI version
- `pydantic==2.12.3` - Updated for better performance

If you encounter dependency conflicts, use `requirements-minimal.txt` for a basic installation.

## Troubleshooting

### Common Issues and Solutions

**1. Port 8000 already in use**

```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or run on a different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

**2. OpenAI API key not working**

- Verify your API key is correct at: https://platform.openai.com/api-keys
- Ensure you have credits in your OpenAI account
- Check the .env file format (no quotes around the key)

**3. Module not found errors**

````bash
**3. Module not found errors**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements-minimal.txt
````

````

**4. JSON parsing errors**

- The app includes automatic JSON parsing with fallback to raw responses
- Check the API response in the error message for debugging

**5. Virtual environment issues**

```bash
# Delete and recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-minimal.txt
````

### Testing the Installation

Run the test scripts to verify everything is working:

```bash
# Test basic API functionality
python test_api.py

# Test JSON parser specifically
python test_json_parser.py
```

## Git Repository Setup

If you want to create your own git repository:

```bash
# Initialize git repository
git init

# Add all source files (the .gitignore will exclude sensitive files)
git add .

# Make initial commit
git commit -m "Initial commit: School AI API with OpenAI integration"

# Add remote repository (if you have one)
git remote add origin <your-repository-url>
git push -u origin main
```

> **Security Note**: The `.env` file is automatically excluded from git to protect your API keys. Users should copy `.env.example` to `.env` and add their own API keys.

## Error Handling

The API includes comprehensive error handling:

- Validation errors for invalid input
- OpenAI API errors
- JSON parsing errors
- General server errors

All errors return standardized JSON responses with success status, message, and error details.

## Logging

The application includes structured logging for:

- Request processing
- OpenAI API calls
- Error tracking
- Performance monitoring
