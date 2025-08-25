# Kingsmen Agent Curl Tutorial 🎩

This tutorial shows how to interact with the Kingsmen agent team using curl commands. You'll learn how to send tasks, manage sessions, and work with the A2A protocol directly.

## Prerequisites

1. **Start the Kingsmen server:**
```bash
export OPENAI_API_KEY="your-api-key-here"
python -m a2a_server.run
```

2. **Verify the server is running:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-XX", 
  "handlers": ["kingsmen_agent", "supervisor_agent", ...]
}
```

## Quick Start - Interactive Examples

For a quick interactive demo of all the examples, run:

```bash
./docs/examples/kingsmen_curl_examples.sh
```

This interactive script lets you try all the examples with a simple menu interface.

## Table of Contents
- [Basic Agent Information](#basic-agent-information)
- [Sending Tasks](#sending-tasks)
- [Session Management](#session-management)
- [Streaming Responses](#streaming-responses)
- [Team-Specific Examples](#team-specific-examples)
- [Error Handling](#error-handling)
- [Advanced Usage](#advanced-usage)

## Basic Agent Information

### Get Agent Card
Retrieve the Kingsmen agent's capabilities and information:

```bash
curl -X GET http://localhost:8000/kingsmen_agent/.well-known/agent.json | jq
```

Expected response:
```json
{
  "name": "The Kingsmen 🎩",
  "description": "An elite team of IBM Cloud specialists - Galahad, Lancelot, Percival, Gareth, and Tristan",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  },
  "skills": [
    {
      "id": "elite_team_coordination",
      "name": "🎩 Elite Team Coordination",
      "description": "Coordinates an elite team of IBM Cloud specialists..."
    }
  ]
}
```

## Sending Tasks

### Basic Task Submission

Send a simple task to the Kingsmen:

```bash
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "task-001",
    "sessionId": "session-123",
    "message": {
      "role": "user",
      "parts": [
        {
          "text": "I need help setting up a new IBM Cloud resource group"
        }
      ]
    },
    "acceptedOutputModes": ["text/plain"],
    "metadata": {
      "conversation_id": "conv-001"
    }
  }' | jq
```

Expected response structure:
```json
{
  "result": {
    "id": "task-001",
    "sessionId": "session-123",
    "status": {
      "state": "completed",
      "message": {
        "role": "assistant",
        "parts": [
          {
            "text": "[Handled by Galahad] I'll help you set up a new resource group..."
          }
        ]
      }
    }
  }
}
```

### Request Specific Agent by Codename

Direct a request to a specific Kingsman:

```bash
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "task-002", 
    "sessionId": "session-123",
    "message": {
      "role": "user",
      "parts": [
        {
          "text": "Have Lancelot create a new service ID for my application"
        }
      ]
    },
    "acceptedOutputModes": ["text/plain"]
  }' | jq
```

### Security and Access Management Task

```bash
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "task-003",
    "sessionId": "session-security",
    "message": {
      "role": "user", 
      "parts": [
        {
          "text": "I need to add a new user to my account with editor permissions for the development resource group"
        }
      ]
    },
    "acceptedOutputModes": ["text/plain"],
    "metadata": {
      "task_type": "user_management",
      "priority": "high"
    }
  }' | jq
```

### Serverless Application Request

```bash
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "task-004",
    "sessionId": "session-serverless", 
    "message": {
      "role": "user",
      "parts": [
        {
          "text": "Create a Code Engine application that scales from 0 to 10 instances based on HTTP requests"
        }
      ]
    },
    "acceptedOutputModes": ["text/plain"]
  }' | jq
```

## Session Management

### Start a New Session

```bash
# Create session variable
SESSION_ID="kingsmen-$(date +%s)"
echo "Session ID: $SESSION_ID"

# First message in session
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"task-session-001\",
    \"sessionId\": \"$SESSION_ID\",
    \"message\": {
      \"role\": \"user\",
      \"parts\": [
        {
          \"text\": \"Hello Kingsmen team! I'm setting up a new IBM Cloud environment for my company.\"
        }
      ]
    },
    \"acceptedOutputModes\": [\"text/plain\"]
  }" | jq
```

### Continue Session Conversation

```bash
# Follow-up message in the same session
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"task-session-002\", 
    \"sessionId\": \"$SESSION_ID\",
    \"message\": {
      \"role\": \"user\",
      \"parts\": [
        {
          \"text\": \"Now I need to add three developers to the account with appropriate permissions.\"
        }
      ]
    },
    \"acceptedOutputModes\": [\"text/plain\"]
  }" | jq
```

### Get Session History

```bash
curl -X GET "http://localhost:8000/kingsmen_agent/sessions/$SESSION_ID/history" | jq
```

## Streaming Responses

### Enable Streaming for Real-time Responses

```bash
curl -X POST http://localhost:8000/kingsmen_agent/task/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "id": "stream-task-001",
    "sessionId": "stream-session",
    "message": {
      "role": "user",
      "parts": [
        {
          "text": "Explain the step-by-step process to set up a complete IBM Cloud development environment with proper governance"
        }
      ]
    },
    "acceptedOutputModes": ["text/plain"]
  }' \
  --no-buffer
```

Expected streaming response:
```
data: {"event": "task_status_update", "data": {"state": "running", "message": {"role": "assistant", "parts": [{"text": "Analyzing your request..."}]}}}

data: {"event": "task_status_update", "data": {"state": "running", "message": {"role": "assistant", "parts": [{"text": "Deploying Galahad for infrastructure setup..."}]}}}

data: {"event": "task_status_update", "data": {"state": "completed", "message": {"role": "assistant", "parts": [{"text": "[Handled by Galahad] Here's the step-by-step process..."}]}}}

data: [DONE]
```

## Team-Specific Examples

### Infrastructure Setup (Galahad)

```bash
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "infra-001",
    "message": {
      "role": "user",
      "parts": [
        {
          "text": "List all resource groups in my account and show me which services are in each one"
        }
      ]
    }
  }' | jq '.result.status.message.parts[0].text'
```

### Security Operations (Lancelot)

```bash
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "security-001",
    "message": {
      "role": "user", 
      "parts": [
        {
          "text": "Show me all access groups and their members. I want to audit who has access to what."
        }
      ]
    }
  }' | jq '.result.status.message.parts[0].text'
```

### Serverless Applications (Percival)

```bash
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "serverless-001", 
    "message": {
      "role": "user",
      "parts": [
        {
          "text": "Deploy a Python Flask application to Code Engine with automatic scaling and custom domain"
        }
      ]
    }
  }' | jq
```

### Best Practices Guidance (Gareth)

```bash
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "guidance-001",
    "message": {
      "role": "user",
      "parts": [
        {
          "text": "What are the IBM Cloud best practices for organizing resources for a multi-environment development workflow?"
        }
      ]
    }
  }' | jq
```

### Automation & DevOps (Tristan)

```bash
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "automation-001",
    "message": {
      "role": "user",
      "parts": [
        {
          "text": "Create a Terraform-based deployable architecture for a 3-tier web application with database"
        }
      ]
    }
  }' | jq
```

## Error Handling

### Invalid Task Format

```bash
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "bad-task",
    "message": "This is not a proper message format"
  }' | jq
```

Expected error response:
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid message format",
    "details": "Message must have role and parts fields"
  }
}
```

### Check Task Status

```bash
curl -X GET http://localhost:8000/kingsmen_agent/tasks/task-001/status | jq
```

### Cancel Running Task

```bash
curl -X POST http://localhost:8000/kingsmen_agent/tasks/task-001/cancel \
  -H "Content-Type: application/json" | jq
```

## Advanced Usage

### Batch Task Submission

Submit multiple tasks for different Kingsmen:

```bash
# Submit multiple tasks in sequence
TASKS=(
  '{"id": "batch-001", "message": {"role": "user", "parts": [{"text": "Galahad, list my resource groups"}]}}'
  '{"id": "batch-002", "message": {"role": "user", "parts": [{"text": "Lancelot, show my service IDs"}]}}'  
  '{"id": "batch-003", "message": {"role": "user", "parts": [{"text": "Percival, list my Code Engine projects"}]}}'
)

for task in "${TASKS[@]}"; do
  echo "Submitting: $task"
  curl -X POST http://localhost:8000/kingsmen_agent/task \
    -H "Content-Type: application/json" \
    -d "$task" | jq '.result.status.state'
  echo "---"
done
```

### Complex Multi-Step Workflow

```bash
# Step 1: Planning phase
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "workflow-001",
    "sessionId": "complex-workflow",
    "message": {
      "role": "user", 
      "parts": [
        {
          "text": "I need to set up a complete development environment with: 1) Resource groups for dev/test/prod, 2) Service accounts for automation, 3) A serverless API, 4) Monitoring and logging. Can you coordinate this across the team?"
        }
      ]
    }
  }' | jq

# Step 2: Follow up on specific aspects
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "workflow-002",
    "sessionId": "complex-workflow", 
    "message": {
      "role": "user",
      "parts": [
        {
          "text": "Now implement the resource group structure you just planned"
        }
      ]
    }
  }' | jq
```

### Health Check and Status

```bash
# Check overall health
curl http://localhost:8000/health | jq

# Check specific agent health  
curl http://localhost:8000/kingsmen_agent/health | jq

# Get metrics (if available)
curl http://localhost:8000/kingsmen_agent/metrics | jq
```

## Useful Shell Functions

Add these to your `.bashrc` or `.zshrc` for easier testing:

```bash
# Quick task submission
kingsmen_task() {
  local message="$1"
  local task_id="${2:-task-$(date +%s)}"
  
  curl -X POST http://localhost:8000/kingsmen_agent/task \
    -H "Content-Type: application/json" \
    -d "{
      \"id\": \"$task_id\",
      \"message\": {
        \"role\": \"user\",
        \"parts\": [
          {
            \"text\": \"$message\"
          }
        ]
      }
    }" | jq '.result.status.message.parts[0].text' -r
}

# Usage: kingsmen_task "List my resource groups"

# Stream task with real-time output
kingsmen_stream() {
  local message="$1"
  
  curl -X POST http://localhost:8000/kingsmen_agent/task/stream \
    -H "Content-Type: application/json" \
    -H "Accept: text/event-stream" \
    -d "{
      \"id\": \"stream-$(date +%s)\",
      \"message\": {
        \"role\": \"user\",
        \"parts\": [
          {
            \"text\": \"$message\"
          }
        ]
      }
    }" --no-buffer
}

# Direct agent requests
galahad() { kingsmen_task "Galahad, $1"; }
lancelot() { kingsmen_task "Lancelot, $1"; }
percival() { kingsmen_task "Percival, $1"; }
gareth() { kingsmen_task "Gareth, $1"; } 
tristan() { kingsmen_task "Tristan, $1"; }

# Usage examples:
# galahad "list my resource groups"
# lancelot "show my access groups"
# percival "list my Code Engine projects"
```

## Testing Scenarios

### Complete Development Setup

```bash
#!/bin/bash
# Complete development environment setup test

SESSION="dev-setup-$(date +%s)"

echo "🎩 Starting complete development setup with session: $SESSION"

# Step 1: Resource planning
echo "📋 Step 1: Planning resources..."
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"setup-001\",
    \"sessionId\": \"$SESSION\",
    \"message\": {
      \"role\": \"user\",
      \"parts\": [
        {
          \"text\": \"I need to plan a development environment with separate resource groups for dev, test, and production. What's the best structure?\"
        }
      ]
    }
  }" | jq '.result.status.message.parts[0].text' -r

echo -e "\n⚔️ Step 2: Setting up security..."
# Step 2: Security setup
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"setup-002\", 
    \"sessionId\": \"$SESSION\",
    \"message\": {
      \"role\": \"user\",
      \"parts\": [
        {
          \"text\": \"Now create service IDs and access groups for each environment with appropriate permissions\"
        }
      ]
    }
  }" | jq '.result.status.message.parts[0].text' -r

echo -e "\n🚀 Step 3: Serverless setup..."
# Step 3: Serverless application
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"setup-003\",
    \"sessionId\": \"$SESSION\", 
    \"message\": {
      \"role\": \"user\",
      \"parts\": [
        {
          \"text\": \"Deploy a sample API application to Code Engine in the development environment\"
        }
      ]
    }
  }" | jq '.result.status.message.parts[0].text' -r

echo -e "\n🤖 Step 4: Automation setup..."  
# Step 4: Automation
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"setup-004\",
    \"sessionId\": \"$SESSION\",
    \"message\": {
      \"role\": \"user\",
      \"parts\": [
        {
          \"text\": \"Create a CI/CD pipeline to deploy from dev to test to production\"
        }
      ]
    }
  }" | jq '.result.status.message.parts[0].text' -r

echo -e "\n✅ Development setup complete!"
```

## Troubleshooting

### Common Issues

1. **Connection refused:**
```bash
# Check if server is running
ps aux | grep "a2a_server"
curl http://localhost:8000/health
```

2. **Authentication errors:**
```bash
# Check API key is set
echo $OPENAI_API_KEY

# Verify agent configuration
curl http://localhost:8000/kingsmen_agent/.well-known/agent.json | jq '.capabilities'
```

3. **Task timeout:**
```bash
# Check task status
curl http://localhost:8000/kingsmen_agent/tasks/your-task-id/status
```

4. **Invalid response format:**
```bash
# Validate request format
echo '{
  "id": "test",
  "message": {
    "role": "user", 
    "parts": [{"text": "test"}]
  }
}' | jq .
```

---

## Summary

This tutorial covered:
- ✅ Basic agent information retrieval
- ✅ Task submission and management  
- ✅ Session-based conversations
- ✅ Streaming responses
- ✅ Team-specific task routing
- ✅ Error handling and troubleshooting
- ✅ Advanced workflows and automation
- ✅ Practical shell functions and scripts

The Kingsmen team is now ready to handle your IBM Cloud operations via the A2A protocol! 🎩

**Quick Start:**
```bash
# Test the team
curl -X POST http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{"id":"test","message":{"role":"user","parts":[{"text":"Hello Kingsmen team!"}]}}' | jq
```