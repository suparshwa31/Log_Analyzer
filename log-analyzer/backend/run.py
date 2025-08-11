#!/usr/bin/env python3
"""
Simple script to run the Flask backend server
"""
import os
import sys
from app import create_app

if __name__ == '__main__':
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['DEBUG'] = 'true'
    os.environ['PORT'] = '5001'
    
    # Create and run the app
    app = create_app()
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5001
    )
