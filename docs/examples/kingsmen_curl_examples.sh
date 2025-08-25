#!/bin/bash
# Kingsmen Curl Examples - Interactive Demo Script
# This script provides easy-to-use examples from the tutorial

BASE_URL="http://localhost:8000"
AGENT="kingsmen_agent"

echo "🎩 KINGSMEN CURL EXAMPLES"
echo "========================="
echo ""

# Check if server is running
echo "🔍 Checking if Kingsmen server is running..."
if ! curl -s "$BASE_URL/health" > /dev/null; then
    echo "❌ Server not responding. Please start it first:"
    echo "   export OPENAI_API_KEY='your-key'"
    echo "   python -m a2a_server.run"
    echo ""
    exit 1
fi

echo "✅ Server is running!"
echo ""

# Helper function to run curl with nice formatting
run_example() {
    local title="$1"
    local curl_cmd="$2"
    
    echo "📝 $title"
    echo "Command: $curl_cmd"
    echo "Response:"
    eval "$curl_cmd"
    echo ""
    echo "---"
    echo ""
}

# Examples menu
while true; do
    echo "🎩 Choose an example to run:"
    echo "1. Get Agent Card"
    echo "2. Basic Task - General Help"
    echo "3. Request Specific Agent (Galahad)"
    echo "4. Security Task (Lancelot)"
    echo "5. Serverless Task (Percival)" 
    echo "6. Best Practices (Gareth)"
    echo "7. Automation Task (Tristan)"
    echo "8. Session-based Conversation"
    echo "9. Streaming Response"
    echo "10. Complex Multi-step Workflow"
    echo "0. Exit"
    echo ""
    read -p "Enter your choice (0-10): " choice

    case $choice in
        1)
            run_example "Agent Card Retrieval" \
                "curl -s '$BASE_URL/$AGENT/.well-known/agent.json' | jq"
            ;;
        2)
            run_example "Basic Task - General Help" \
                "curl -s -X POST '$BASE_URL/$AGENT/task' \\
                -H 'Content-Type: application/json' \\
                -d '{
                    \"id\": \"basic-$(date +%s)\",
                    \"message\": {
                        \"role\": \"user\",
                        \"parts\": [{\"text\": \"I need help setting up a new IBM Cloud resource group\"}]
                    }
                }' | jq '.result.status.message.parts[0].text' -r"
            ;;
        3)
            run_example "Request Galahad (Infrastructure)" \
                "curl -s -X POST '$BASE_URL/$AGENT/task' \\
                -H 'Content-Type: application/json' \\
                -d '{
                    \"id\": \"galahad-$(date +%s)\",
                    \"message\": {
                        \"role\": \"user\",
                        \"parts\": [{\"text\": \"Galahad, list all resource groups in my account\"}]
                    }
                }' | jq '.result.status.message.parts[0].text' -r"
            ;;
        4)
            run_example "Security Task - Lancelot" \
                "curl -s -X POST '$BASE_URL/$AGENT/task' \\
                -H 'Content-Type: application/json' \\
                -d '{
                    \"id\": \"lancelot-$(date +%s)\",
                    \"message\": {
                        \"role\": \"user\",
                        \"parts\": [{\"text\": \"Lancelot, create a service ID for my development team\"}]
                    }
                }' | jq '.result.status.message.parts[0].text' -r"
            ;;
        5)
            run_example "Serverless Task - Percival" \
                "curl -s -X POST '$BASE_URL/$AGENT/task' \\
                -H 'Content-Type: application/json' \\
                -d '{
                    \"id\": \"percival-$(date +%s)\",
                    \"message\": {
                        \"role\": \"user\",
                        \"parts\": [{\"text\": \"Percival, create a Code Engine application that scales automatically\"}]
                    }
                }' | jq '.result.status.message.parts[0].text' -r"
            ;;
        6)
            run_example "Best Practices - Gareth" \
                "curl -s -X POST '$BASE_URL/$AGENT/task' \\
                -H 'Content-Type: application/json' \\
                -d '{
                    \"id\": \"gareth-$(date +%s)\",
                    \"message\": {
                        \"role\": \"user\",
                        \"parts\": [{\"text\": \"Gareth, what are the best practices for organizing IBM Cloud resources?\"}]
                    }
                }' | jq '.result.status.message.parts[0].text' -r"
            ;;
        7)
            run_example "Automation Task - Tristan" \
                "curl -s -X POST '$BASE_URL/$AGENT/task' \\
                -H 'Content-Type: application/json' \\
                -d '{
                    \"id\": \"tristan-$(date +%s)\",
                    \"message\": {
                        \"role\": \"user\",
                        \"parts\": [{\"text\": \"Tristan, set up a CI/CD pipeline for my application\"}]
                    }
                }' | jq '.result.status.message.parts[0].text' -r"
            ;;
        8)
            echo "🔄 Starting session-based conversation..."
            SESSION_ID="demo-session-$(date +%s)"
            echo "Session ID: $SESSION_ID"
            
            run_example "Session Message 1" \
                "curl -s -X POST '$BASE_URL/$AGENT/task' \\
                -H 'Content-Type: application/json' \\
                -d '{
                    \"id\": \"session-1-$(date +%s)\",
                    \"sessionId\": \"$SESSION_ID\",
                    \"message\": {
                        \"role\": \"user\",
                        \"parts\": [{\"text\": \"Hello Kingsmen! I'm starting a new IBM Cloud project.\"}]
                    }
                }' | jq '.result.status.message.parts[0].text' -r"
            
            read -p "Press Enter to send follow-up message..."
            
            run_example "Session Message 2" \
                "curl -s -X POST '$BASE_URL/$AGENT/task' \\
                -H 'Content-Type: application/json' \\
                -d '{
                    \"id\": \"session-2-$(date +%s)\",
                    \"sessionId\": \"$SESSION_ID\",
                    \"message\": {
                        \"role\": \"user\",
                        \"parts\": [{\"text\": \"Now I need to set up security and access controls.\"}]
                    }
                }' | jq '.result.status.message.parts[0].text' -r"
            ;;
        9)
            echo "🌊 Starting streaming response (press Ctrl+C to stop)..."
            curl -X POST "$BASE_URL/$AGENT/task/stream" \
                -H "Content-Type: application/json" \
                -H "Accept: text/event-stream" \
                -d "{
                    \"id\": \"stream-$(date +%s)\",
                    \"message\": {
                        \"role\": \"user\",
                        \"parts\": [{\"text\": \"Explain the complete process for setting up an IBM Cloud environment with proper governance\"}]
                    }
                }" \
                --no-buffer
            echo ""
            ;;
        10)
            echo "🔄 Complex Multi-step Workflow..."
            WORKFLOW_SESSION="workflow-$(date +%s)"
            
            echo "Step 1: Planning phase"
            curl -s -X POST "$BASE_URL/$AGENT/task" \
                -H "Content-Type: application/json" \
                -d "{
                    \"id\": \"workflow-1-$(date +%s)\",
                    \"sessionId\": \"$WORKFLOW_SESSION\",
                    \"message\": {
                        \"role\": \"user\",
                        \"parts\": [{\"text\": \"I need to coordinate the team to set up: 1) Resource groups for dev/test/prod, 2) Service accounts, 3) A serverless API, 4) Monitoring. Plan this out.\"}]
                    }
                }" | jq '.result.status.message.parts[0].text' -r
            
            echo ""
            read -p "Press Enter for Step 2..."
            
            echo "Step 2: Implementation"
            curl -s -X POST "$BASE_URL/$AGENT/task" \
                -H "Content-Type: application/json" \
                -d "{
                    \"id\": \"workflow-2-$(date +%s)\", 
                    \"sessionId\": \"$WORKFLOW_SESSION\",
                    \"message\": {
                        \"role\": \"user\",
                        \"parts\": [{\"text\": \"Now implement the resource structure you just planned\"}]
                    }
                }" | jq '.result.status.message.parts[0].text' -r
            echo ""
            ;;
        0)
            echo "👋 Thanks for trying the Kingsmen curl examples!"
            break
            ;;
        *)
            echo "❌ Invalid choice. Please enter 0-10."
            ;;
    esac
    
    read -p "Press Enter to continue..."
    clear
    echo "🎩 KINGSMEN CURL EXAMPLES"
    echo "========================="
    echo ""
done