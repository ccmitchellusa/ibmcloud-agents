# kingsmen_agent/agent.py

"""
Kingsmen Agent - Elite IBM Cloud Operations Team
Backward compatibility module for the Kingsmen handler.
"""

from .kingsmen_handler import create_kingsmen_handler

# Create the Kingsmen handler for backward compatibility
root_agent = create_kingsmen_handler()