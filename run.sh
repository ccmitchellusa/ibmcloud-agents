#!/bin/bash

# import env vars/secrets
source .env

# Function to display the IBM Cloud banner
show_banner() {
    # Define IBM Blue color (hex 0f62fe)
    local IBM_BLUE='\033[38;2;15;98;254m'
    local KINGSMEN_YELLO='\033[38;2;255;204;0m'
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
    echo -e "${KINGSMEN_YELLO}"
    echo "        _     _ _____ __   _  ______ _______ _______ _______ __   _"
    echo "        |____/    |   | \  | |  ____ |______ |  |  | |______ | \  |"
    echo "        |    \_ __|__ |  \_| |_____| ______| |  |  | |______ |  \_|"
    echo -e "${IBM_BLUE}"
    echo "                   A2A Server w/ Platform Engineering Agents"
    echo "==============================================================================="
    echo -e "${RESET}"
}

# Display the banner when script starts
show_banner
# Launches the agent(s) using the A2A Server framework
#
# Usage: A2A Server (YAML config) [-h] [-c CONFIG] [-p HANDLER_PACKAGES] [--no-discovery] [--log-level {debug,info,warning,error,critical}] [--list-routes] [--enable-flow-diagnosis]

# Options:
#  -h, --help            show this help message and exit
#  -c, --config CONFIG   YAML config path, eg. 'agent.yaml' 
#                        The YAML can contain multiple agent definitions. See a2a-server README for multiple agent example.
#  -p, --handler-package HANDLER_PACKAGES
#                        Additional packages to search for handlers.  Handlers are the Agent modules, eg. 'pirate_agent_a2a'
#  --no-discovery        Disable automatic handler discovery
#  --log-level {debug,info,warning,error,critical}
#                        Override configured log level
#  --list-routes         List all registered routes after initialization
#  --enable-flow-diagnosis
#                        Enable detailed flow diagnosis and tracing for pub/sub event handling.

# TODO: uv concurrency limit needs to match the Code Engine Max concurrency setting when run on IBM Cloud
# Login to IBM Cloud using api key. LLM will be acting on user's behalf, with user's access
# ibmcloud login --apikey IBMCLOUD_APIKEY
$IBMCLOUD_CLI_PATH login --apikey $IBMCLOUD_API_KEY -r $IBMCLOUD_REGION
$IBMCLOUD_CLI_PATH target -g $IBMCLOUD_RESOURCE_GROUP
# uv run -m ibmcloud_base_agent.main --config agent.yaml --log-level debug --enable-flow-diagnosis
# uv run -m ibmcloud_base_agent.main --config agent.yaml --log-level debug --list-routes
# uv run -m ibmcloud_base_agent.main --config agent.yaml --log-level debug 
cd src && uv run -m ibmcloud_base_agent.main --config ../agent.yaml

