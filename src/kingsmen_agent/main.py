#!/usr/bin/env python3
"""
Launch Kingsmen agent server.

The Kingsmen - An elite team of IBM Cloud specialists with codenames and expertise areas.
Each agent has specialized skills for different aspects of IBM Cloud operations.
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# a2a imports
from a2a_server.app import create_app
from .kingsmen_handler import create_kingsmen_handler

# Get configuration from environment with defaults
HOST = os.getenv('KINGSMEN_HOST', '0.0.0.0')
PORT = int(os.getenv('KINGSMEN_PORT', '9001'))


def main():
    """Main entry point for the Kingsmen agent server."""
    print("🎩 Assembling the Kingsmen team...")
    
    # Create the Kingsmen handler
    handler = create_kingsmen_handler()
    
    # Create the FastAPI app with the handler
    app = create_app(
        handlers=[handler],
        title="Kingsmen Agent - Elite IBM Cloud Team",
        description="An elite team of IBM Cloud specialists, each with codenames and specialized expertise"
    )
    
    # Launch the server
    print(f"🎩 Kingsmen team ready for operations on {HOST}:{PORT}")
    print("🎯 Team roster:")
    print("  - Galahad (Base Agent): Foundation & Infrastructure")
    print("  - Lancelot (Account Admin): Security & Access Control") 
    print("  - Percival (Serverless): Modern Applications & Serverless")
    print("  - Gareth (Guide): Strategy & Best Practices")
    print("  - Tristan (Automation): DevOps & Infrastructure as Code")
    
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()