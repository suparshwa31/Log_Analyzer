# Log Analyzer

A comprehensive log analysis tool that provides anomaly detection, timeline visualization, and AI-powered insights for log files.

## Features

- **Log File Upload & Parsing**: Support for Apache and SSH log formats
- **Anomaly Detection**: Automatic detection of suspicious patterns, error spikes, and unusual activities
- **Timeline Visualization**: Interactive charts showing log activity over time
- **AI-Powered Analysis**: OpenAI integration for intelligent log summaries and recommendations
- **Real-time Investigation**: View logs related to specific anomalies
- **User Authentication**: Secure login system with Supabase

## New Features (Latest Update)

- ✅ **View Logs Button**: Shows logs related to specific anomalies
- ✅ **Investigate Button**: Opens detailed anomaly investigation modal
- ✅ **Dismiss Button**: Removes notifications from detected anomalies section
- ✅ **Timeline Chart**: Fixed to properly display log activity graphs
- ✅ **OpenAI Integration**: AI-powered log summaries and insights
- ✅ **Enhanced Anomaly Handling**: Better filtering and display of relevant log entries

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
   export OPENAI_API_KEY="your_openai_api_key_here"
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
2. **Upload Logs**: Upload Apache or SSH log files for analysis
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

## Troubleshooting

### Timeline Chart Not Showing

If the timeline chart is not displaying:
1. Ensure log files have timestamp data
2. Check browser console for JavaScript errors
3. Verify that log parsing is successful

### AI Features Not Working

If AI summaries are not generating:
1. Verify `OPENAI_API_KEY` is set correctly
2. Check OpenAI API quota and billing
3. Ensure internet connectivity for API calls

### Backend Connection Issues

If the frontend can't connect to the backend:
1. Verify backend is running on port 5001
2. Check CORS configuration
3. Ensure firewall allows local connections

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
