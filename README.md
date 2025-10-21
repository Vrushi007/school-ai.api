# School AI API

A Python web API application that integrates with OpenAI to generate educational content including lesson plans, detailed session content, and questions for Indian school standards (CBSE/NCERT).

## Features

- **Lesson Plan Generation**: Create structured lesson plans with multiple sessions
- **Detailed Session Content**: Generate comprehensive lesson content with activities, assessments, and resources
- **Question Generation**: Create diverse question sets with various difficulty levels and types
- **JSON Parser Integration**: Handles malformed OpenAI responses gracefully
- **CBSE/NCERT Aligned**: Content specifically designed for Indian school standards
- **RESTful API**: Clean, well-documented API endpoints
- **Error Handling**: Comprehensive error handling and logging

## Quick Start (Advanced Users)

```bash
# Clone and setup in one go
git clone <repository-url> && cd dummy-school-ai.api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-minimal.txt
echo "OPENAI_API_KEY=your-api-key-here" > .env
python main.py
```

Then visit: http://localhost:8000/docs

## API Endpoints

### Health Check

- `GET /` - Root endpoint with API status
- `GET /health` - Health check endpoint

### Educational Content Generation

- `POST /api/generate-lesson-plan` - Generate lesson plans
- `POST /api/generate-detailed-content-for-session` - Generate detailed session content
- `POST /api/generate-questions` - Generate questions and assessments

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
   # Option 1: Edit the .env file directly
   # Open .env file in any text editor and replace the placeholder:
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here

   # Option 2: Use echo command (macOS/Linux):
   echo "OPENAI_API_KEY=sk-your-actual-openai-api-key-here" > .env
   ```

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
dummy-school-ai.api/
├── main.py              # FastAPI application and routes
├── openai_service.py    # OpenAI service integration
├── models.py            # Pydantic models for request/response
├── utils/               # Utility modules
│   ├── __init__.py     # Utils package init
│   └── json_parser.py  # JSON parsing utilities
├── requirements.txt     # Complete Python dependencies
├── requirements-minimal.txt # Minimal dependencies for basic setup
├── .env                 # Environment variables (API keys)
├── .gitignore          # Git ignore file
├── test_api.py         # API testing script
├── test_json_parser.py # JSON parser testing script
├── start.sh            # Startup script
└── README.md           # This file
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

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
