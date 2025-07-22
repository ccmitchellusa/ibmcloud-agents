#!/bin/bash

# Function to display the IBM Cloud banner
show_banner() {
    # Define IBM Blue color (hex 0f62fe)
    local IBM_BLUE='\033[38;2;15;98;254m'
    local RESET='\033[0m'
    
    echo -e "${IBM_BLUE}"
    echo "==============================================================================="
    echo ""
    echo "    ██╗██████╗ ███╗   ███╗     ██████╗██╗      ██████╗ ██╗   ██╗██████╗ "
    echo "    ██║██╔══██╗████╗ ████║    ██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗"
    echo "    ██║██████╔╝██╔████╔██║    ██║     ██║     ██║   ██║██║   ██║██║  ██║"
    echo "    ██║██╔══██╗██║╚██╔╝██║    ██║     ██║     ██║   ██║██║   ██║██║  ██║"
    echo "    ██║██████╔╝██║ ╚═╝ ██║    ╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝"
    echo "    ╚═╝╚═════╝ ╚═╝     ╚═╝     ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ "
    echo ""
    echo "==============================================================================="
    echo -e "${RESET}"
}

# Display the banner when script starts
show_banner

# Login to IBM Cloud
ibmcloud login --apikey $IBMCLOUD_API_KEY -r $IBMCLOUD_REGION

# Activate the virtual environment
source /venv/bin/activate

# Run the agent
/venv/bin/python3 -m ibmcloud_agents.main --config agent.yaml
