#!/usr/bin/env python3
# main.py
"""
Launch multi-agent server. 

This example launches an A2A server by passing a raw Google ADK `Agent`
directly into the handler; no manual adapter import or `use_handler_discovery`
flag is needed.
"""
import uvicorn

# a2a imports
from a2a_server.app import create_app
from a2a_server.tasks.handlers.google_adk_handler import GoogleADKHandler

# import the sample agent
from .agent import root_agent as root_agent

# constants
HOST = "0.0.0.0"
PORT = 8000

def main():
    # Instantiate the handler directly with the raw ADK agent
    handler = GoogleADKHandler(root_agent)

    # Create the FastAPI app with just this handler
    app = create_app(
        handlers=[handler]
    )

    # Launch the server
    uvicorn.run(app, host=HOST, port=PORT)

if __name__ == "__main__":
    main()