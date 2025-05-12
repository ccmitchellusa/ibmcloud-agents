#!/bin/bash
source .env

# Launches the adk web ui to test the agent.

# TODO: uv concurrency limit needs to match the Code Engine Max concurrency setting when run on IBM Cloud
# Login to IBM Cloud using api key. LLM will be acting on user's behalf, with user's access
# ibmcloud login --apikey IBMCLOUD_APIKEY
/Users/chrism1/Downloads/ibmcloud login --apikey $IBMCLOUD_API_KEY

uv run adk web
