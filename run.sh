#!/bin/bash

# Launches the agent(s) using the A2A Server framework
#
# Usage: A2A Server (YAML config) [-h] [-c CONFIG] [-p HANDLER_PACKAGES] [--no-discovery] [--log-level {debug,info,warning,error,critical}] [--list-routes] [--enable-flow-diagnosis]
#
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

# uv run -m ibmcloud_base_agent.main --config agent.yaml --log-level debug --enable-flow-diagnosis
uv run -m ibmcloud_base_agent.main --config agent.yaml --log-level debug --list-routes
# uv run -m ibmcloud_base_agent.main --config agent.yaml --log-level debug 
# uv run -m ibmcloud_base_agent.main --config agent.yaml

