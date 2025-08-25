#!/usr/bin/env python3
"""
Launch supervisor agent server using a2a-server framework.

This server launches an A2A server that can delegate tasks to other agents
using the a2a protocol without Google ADK dependencies.
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# a2a imports
from a2a_server.app import create_app
from .supervisor_handler import create_supervisor_handler
from .team_management import router as team_router, set_supervisor_handler

# Get configuration from environment with defaults
HOST = os.getenv('SUPERVISOR_HOST', '0.0.0.0')
PORT = int(os.getenv('SUPERVISOR_PORT', '9000'))  # Default to 9000 to avoid conflicts


def main():
    """Main entry point for the supervisor agent server."""
    # Create the supervisor handler
    handler = create_supervisor_handler()
    
    # Set the handler reference for team management endpoints
    set_supervisor_handler(handler)
    
    # Create the FastAPI app with the handler
    app = create_app(
        handlers=[handler],
        title="Supervisor Agent",
        description="A2A Supervisor agent that delegates tasks to specialized agents"
    )
    
    # Add team management routes
    app.include_router(team_router, prefix="/api/v1")
    
    # Launch the server
    print(f"Starting Supervisor Agent on {HOST}:{PORT}")
    print(f"Agent URLs configured from: SUPERVISOR_AGENT_URLS environment variable")
    print(f"Team management API available at: http://{HOST}:{PORT}/api/v1/team")
    print(f"API documentation available at: http://{HOST}:{PORT}/docs")
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()