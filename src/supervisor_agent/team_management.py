"""
Team management endpoints for the supervisor agent.
Provides HTTP APIs for dynamically managing team members.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)

# Global reference to supervisor handler (set by main.py)
_supervisor_handler = None

def set_supervisor_handler(handler):
    """Set the global supervisor handler reference."""
    global _supervisor_handler
    _supervisor_handler = handler

def get_supervisor_handler():
    """Get the global supervisor handler reference."""
    if _supervisor_handler is None:
        raise HTTPException(status_code=500, detail="Supervisor handler not initialized")
    return _supervisor_handler


# Pydantic models for API requests/responses
class AddTeamMemberRequest(BaseModel):
    """Request model for adding a team member."""
    model_config = ConfigDict(extra='forbid')
    
    agent_url: str = Field(..., description="URL of the agent to add")
    agent_name: Optional[str] = Field(None, description="Optional custom name for the agent")

class RemoveTeamMemberRequest(BaseModel):
    """Request model for removing a team member."""
    model_config = ConfigDict(extra='forbid')
    
    agent_name: str = Field(..., description="Name of the agent to remove")

class TeamMemberResponse(BaseModel):
    """Response model for team member operations."""
    success: bool
    agent_name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    streaming: Optional[bool] = None
    message: Optional[str] = None
    error: Optional[str] = None

class TeamMemberInfo(BaseModel):
    """Model for team member information."""
    name: str
    description: str
    url: str
    streaming: bool
    type: str  # 'configured' or 'dynamic'
    status: str  # 'connected' or 'disconnected'
    added_at: Optional[str] = None

class TeamListResponse(BaseModel):
    """Response model for listing team members."""
    total_agents: int
    configured_agents: int
    dynamic_agents: int
    connected_agents: int
    team_members: List[TeamMemberInfo]

class ReconnectRequest(BaseModel):
    """Request model for reconnecting to a team member."""
    model_config = ConfigDict(extra='forbid')
    
    agent_name: str = Field(..., description="Name of the agent to reconnect")


# Create router for team management endpoints
router = APIRouter(prefix="/team", tags=["team-management"])


@router.post("/add", response_model=TeamMemberResponse)
async def add_team_member(request: AddTeamMemberRequest):
    """
    Add a new team member agent dynamically.
    
    - **agent_url**: URL of the agent to add (e.g., http://localhost:9000/custom_agent)
    - **agent_name**: Optional custom name for the agent (defaults to agent's self-reported name)
    
    Returns information about the newly added agent or an error if the operation fails.
    """
    try:
        supervisor = get_supervisor_handler()
        result = await supervisor.add_team_member(
            agent_url=request.agent_url,
            agent_name=request.agent_name
        )
        
        return TeamMemberResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in add_team_member endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/remove", response_model=TeamMemberResponse)
async def remove_team_member(request: RemoveTeamMemberRequest):
    """
    Remove a dynamically added team member agent.
    
    - **agent_name**: Name of the agent to remove
    
    Note: Only dynamically added agents can be removed. Configured agents cannot be removed.
    """
    try:
        supervisor = get_supervisor_handler()
        result = await supervisor.remove_team_member(request.agent_name)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Unknown error'))
        
        return TeamMemberResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in remove_team_member endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/list", response_model=TeamListResponse)
async def list_team_members():
    """
    List all current team member agents with their status and information.
    
    Returns detailed information about all configured and dynamic agents.
    """
    try:
        supervisor = get_supervisor_handler()
        result = await supervisor.list_team_members()
        
        return TeamListResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in list_team_members endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/info/{agent_name}")
async def get_team_member_info(agent_name: str):
    """
    Get detailed information about a specific team member.
    
    - **agent_name**: Name of the agent to get information about
    
    Returns comprehensive information about the specified agent.
    """
    try:
        supervisor = get_supervisor_handler()
        result = await supervisor.get_team_member_info(agent_name)
        
        if not result.get('success', False):
            raise HTTPException(status_code=404, detail=result.get('error', 'Agent not found'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_team_member_info endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/reconnect", response_model=TeamMemberResponse)
async def reconnect_team_member(request: ReconnectRequest):
    """
    Attempt to reconnect to a team member agent.
    
    - **agent_name**: Name of the agent to reconnect to
    
    Useful for re-establishing connections to agents that may have been restarted.
    """
    try:
        supervisor = get_supervisor_handler()
        result = await supervisor.reconnect_team_member(request.agent_name)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Unknown error'))
        
        return TeamMemberResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in reconnect_team_member endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/status")
async def get_team_status():
    """
    Get a quick status overview of the supervisor's team.
    
    Returns summary statistics about team composition and health.
    """
    try:
        supervisor = get_supervisor_handler()
        result = await supervisor.list_team_members()
        
        return {
            "supervisor_status": "active",
            "total_agents": result["total_agents"],
            "configured_agents": result["configured_agents"],
            "dynamic_agents": result["dynamic_agents"],
            "connected_agents": result["connected_agents"],
            "disconnected_agents": result["total_agents"] - result["connected_agents"],
            "health": "healthy" if result["connected_agents"] > 0 else "warning"
        }
        
    except Exception as e:
        logger.error(f"Error in get_team_status endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Management endpoints for batch operations
@router.post("/batch/add")
async def batch_add_team_members(agents: List[AddTeamMemberRequest]):
    """
    Add multiple team members in a batch operation.
    
    - **agents**: List of agent configurations to add
    
    Returns results for each agent addition attempt.
    """
    if len(agents) > 10:
        raise HTTPException(status_code=400, detail="Batch size limited to 10 agents")
    
    try:
        supervisor = get_supervisor_handler()
        results = []
        
        for agent_req in agents:
            result = await supervisor.add_team_member(
                agent_url=agent_req.agent_url,
                agent_name=agent_req.agent_name
            )
            results.append(result)
        
        successful = len([r for r in results if r.get('success')])
        return {
            "batch_size": len(agents),
            "successful": successful,
            "failed": len(agents) - successful,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in batch_add_team_members endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch/remove")
async def batch_remove_team_members(agents: List[RemoveTeamMemberRequest]):
    """
    Remove multiple team members in a batch operation.
    
    - **agents**: List of agent names to remove
    
    Returns results for each agent removal attempt.
    """
    if len(agents) > 10:
        raise HTTPException(status_code=400, detail="Batch size limited to 10 agents")
    
    try:
        supervisor = get_supervisor_handler()
        results = []
        
        for agent_req in agents:
            result = await supervisor.remove_team_member(agent_req.agent_name)
            results.append(result)
        
        successful = len([r for r in results if r.get('success')])
        return {
            "batch_size": len(agents),
            "successful": successful,
            "failed": len(agents) - successful,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in batch_remove_team_members endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")