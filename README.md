# Log Analyzer

A comprehensive log analysis tool that provides anomaly detection, timeline visualization, and AI-powered insights for log files.

## Features

- **Log File Upload & Parsing**: Support for Apache and SSH log formats
- **Anomaly Detection**: Automatic detection of suspicious patterns, error spikes, and unusual activities
- **Timeline Visualization**: Interactive charts showing log activity over time
- **AI-Powered Analysis**: OpenAI integration for intelligent log summaries and recommendations
- **Real-time Investigation**: View logs related to specific anomalies
- **User Authentication**: Secure login system with Supabase

## Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API Key (for AI features)

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd log-analyzer/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   SUPABASE_URL="your-supabase-url-here"
   SUPABASE_ANON_KEY="your-supabase-anon-key-here"
   SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-key-here"
   SUPABASE_BUCKET="your-supabase-bucket-name-here"
   OPENAI_API_KEY="your_openai_api_key_here"
   
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd log-analyzer/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```
3. Set up environment variables:
   ```bash
   SUPABASE_URL="your-supabase-url-here"
   SUPABASE_ANON_KEY="your-supabase-anon-key-here"
   VITE_API_BASE_URL="your-backend-hosted-url"
   
   ```

## Running the Application

### Backend

From the `log-analyzer/backend` directory:

```bash
# Option 1: Use the run script
python3 run.py

# Option 2: Use Flask directly
FLASK_ENV=development DEBUG=true PORT=5001 python3 app.py
```

The backend will start on `http://localhost:5001`

### Frontend

From the `log-analyzer/frontend` directory:

```bash
npm run dev
```

The frontend will start on `http://localhost:3000`

## Usage

1. **Login**: Use the authentication system to access the application
2. **Upload Logs**: Upload log files for analysis
3. **View Results**: See detected anomalies, timeline charts, and AI-generated insights
4. **Investigate Anomalies**: Click "Investigate" to see detailed information
5. **View Related Logs**: Click "View Logs" to see logs related to specific anomalies
6. **Dismiss Notifications**: Remove resolved or false positive anomalies

## API Endpoints

- `POST /api/auth/login` - User authentication
- `POST /api/upload/log` - Log file upload and parsing
- `POST /api/analysis/analyze` - Log analysis with AI insights
- `POST /api/analysis/anomalies` - Detailed anomaly analysis
- `POST /api/analysis/timeline` - Timeline data for visualization

## Configuration

The application can be configured through environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key for AI features
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `DEBUG`: Enable debug mode
- `PORT`: Backend server port

## AI Usage

the Analysis summary feature uses OpenAI API to generate a intelligent summaries, key insights, and actionable recommendations based on log analysis data. i am using openai-gpt-3.5-turbo model for this task.
if openai fails to generate a summary the application will continue to process othe analysis features with a fallback summary generated using keywords based analysis.
## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
