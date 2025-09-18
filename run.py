#!/usr/bin/env python3
"""
Simple script to run the Nano Banana Image Mixer web application
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting Nano Banana Image Mixer...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
        sys.exit(0)
