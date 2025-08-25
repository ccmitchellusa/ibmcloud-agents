# supervisor_agent/agent.py

"""
Supervisor agent using a2a-server framework.
This module provides backward compatibility with the old agent structure.
"""

from .supervisor_handler import create_supervisor_handler

# Create the supervisor handler for backward compatibility
root_agent = create_supervisor_handler()