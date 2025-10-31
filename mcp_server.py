import json
import os
from pathlib import Path
import uuid
from typing import Dict

from mcp.server.fastmcp import FastMCP, Context
import asyncio
import uuid
import os

from shared.config import TEMPORAL_TASK_QUEUE, get_temporal_client
from src.workflows import InfraMonAgentWorkflow, InfraMonAgentWorkflowProactive
from dotenv import load_dotenv


mcp = FastMCP(name="Infrastructure Monitoring Agent",
              description="An infrastructure monitoring and repair agent for network equipment maintenance.",
              version="0.1.0",
              author="Josh Smith",
              instructions="""
This agent is designed to monitor and repair issues in network infrastructure systems.
It can detect equipment problems, plan maintenance and repairs, and execute them based on user approval. 
Users can initiate a monitoring workflow, approve or reject proposed repairs, and query the status of the workflow.
Optionally they can start a proactive monitoring workflow that will run in the background and detect problems on its own."""
                )


@mcp.tool(description="Trigger an infrastructure monitoring workflow to start that will detect equipment problems and propose repairs. " \
          "Upon Approval, the workflow will continue with the repairs and eventually report its results.",
          #tags={"monitoring", "infrastructure", "workflow", "start workflow"},
          )
async def initiate_infrastructure_monitoring() -> Dict[str, str]:
    """Start the Infrastructure Monitoring Workflow to detect and repair equipment problems.
    This is not a proactive agent, but a workflow that runs on demand.
    It will analyze the infrastructure system, plan repairs, and execute them as needed.
    Users can approve or reject proposed repairs."""
    
    load_dotenv(override=True)
    user = os.environ.get("USER_NAME", "Admin.User") 
    client = await get_temporal_client()

    start_msg = {
        "prompt": "Analyze and repair equipment issues in the infrastructure system.",
        "metadata": {
            "user": user,  
            "system": "temporal-infra-monitoring-agent",
        },
    }
    
    handle = await client.start_workflow(
        InfraMonAgentWorkflow.run,
        start_msg,
        id=f"infra-monitoring-{user}-{uuid.uuid4()}",
        task_queue=TEMPORAL_TASK_QUEUE,
    )
    
    desc = await handle.describe()
    status = await handle.query("GetRepairStatus")    
    
    return {"workflow_id": handle.id, "run_id": handle.result_run_id, "status": status, "description": desc.status.name}

@mcp.tool(description="Approve the repairs proposed by the infrastructure monitoring agent workflow. Upon Approval, " \
        "the Workflow will continue with the repairs and eventually report its results.",
          #tags={"monitoring", "infrastructure", "workflow", "approve workflow"},
          )
async def approve_proposed_infrastructure_repairs(workflow_id: str, run_id: str) -> str:
    """Signal approval for the infrastructure monitoring workflow."""
    
    load_dotenv(override=True)
    user = os.environ.get("USER_NAME", "Admin.User") 
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)
    await handle.signal("ApproveRepair", user)
    
    #TODO implement this as an update
    status = await handle.query("GetRepairStatus")    
    return "Infrastructure repair status: " + status + ", repairs are being completed."

@mcp.tool(description="Reject the repairs proposed by the infrastructure monitoring agent workflow. Upon Rejection, " \
        "the Workflow will end and not continue with the repairs.",
          #tags={"monitoring", "infrastructure", "workflow", "reject workflow"},
          )
async def reject_proposed_infrastructure_repairs(workflow_id: str, run_id: str) -> str:
    """Signal rejection for the infrastructure monitoring workflow."""
    load_dotenv(override=True)
    user = os.environ.get("USER_NAME", "Admin.User") 
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)
    await handle.signal("RejectRepair", user)
    status = await handle.query("GetRepairStatus")    
    return status

@mcp.tool(description="Detect if there are problems with the infrastructure equipment.",
          #tags={"monitoring", "infrastructure", "workflow", "status"},
          )
async def get_infrastructure_problems_confidence(workflow_id: str, run_id: str) -> Dict[str, float]:
    """Return score about how confident the system is there are problems with the infrastructure equipment.
    used to answer problems like "Are there problems with the network equipment?"."""
    load_dotenv(override=True)
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)
    
    problem_confidence_score = await handle.query("GetProblemsConfidenceScore")
    return {
        "confidence that there are infrastructure problems percent": problem_confidence_score,
    }

@mcp.tool(description="Get the current status of the infrastructure monitoring workflow.",
          #tags={"monitoring", "infrastructure", "workflow", "status"},
          )
async def status(workflow_id: str, run_id: str) -> Dict[str, str]:
    """Return current status of the infrastructure monitoring workflow."""
    load_dotenv(override=True)
    user = os.environ.get("USER_NAME", "Admin.User") 
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)
    desc = await handle.describe()
    status = await handle.query("GetRepairStatus")
    return {
        "status": status,
        "description": desc.status.name
    }

@mcp.tool(description="Get the analysis result for the infrastructure monitoring workflow.",
          #tags={"monitoring", "infrastructure", "workflow", "analysis"},
          )
async def get_infrastructure_analysis_result(workflow_id: str, run_id: str) -> Dict[str, str]:
    """Return the analysis result for the infrastructure monitoring workflow. This is the result of the analysis step.
    This won't have results before the analysis step is complete.
    The analysis result includes the problems for each equipment and any additional notes.   
    """
    load_dotenv(override=True)
    user = os.environ.get("USER_NAME", "Admin.User") 
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)
    
    try:
        analysis_result: dict = await handle.query("GetRepairAnalysisResult")
    except Exception as e:
        print(f"Error querying infrastructure analysis result: {e}")
        analysis_result = "No analysis result available yet."
    
    return {"analysis_result": analysis_result}

@mcp.tool(description="Get the proposed maintenance tools for the infrastructure monitoring workflow.",
          #tags={"monitoring", "infrastructure", "workflow", "proposed tools"},
          )
async def get_proposed_infrastructure_tools(workflow_id: str, run_id: str) -> Dict[str, str]:
    """Return the proposed maintenance tools for the infrastructure monitoring workflow. This is the result of the planning step. 
    This should not be confused with the tools that are actually executed.
    This won't have results before the planning step is complete."""
    load_dotenv(override=True)
    user = os.environ.get("USER_NAME", "Admin.User") 
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)
    
    try:
        planning_result: dict = await handle.query("GetRepairPlanningResult")
        proposed_tools = planning_result.get("proposed_tools", [])
        additional_notes = planning_result.get("additional_notes", "")
    except Exception as e:
        print(f"Error querying infrastructure planning result: {e}")
        proposed_tools = "No tools proposed yet."
        additional_notes = ""
    
    return {
        "proposed_tools": proposed_tools,
        "additional_notes": additional_notes
    }

@mcp.tool(description="Get the results of the maintenance tools executed by the infrastructure monitoring workflow.",
          #tags={"monitoring", "infrastructure", "workflow", "repair results"},
          )
async def get_infrastructure_repair_tool_results(workflow_id: str, run_id: str) -> Dict[str, str]:
    """Return the results of the maintenance tools executed by the infrastructure monitoring workflow.
    This won't have results before the repair step is complete."""
    load_dotenv(override=True)
    user = os.environ.get("USER_NAME", "Admin.User") 
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)
    
    try:
        repair_result = await handle.query("GetRepairToolResults")
    except Exception as e:
        print(f"Error querying infrastructure repair tool results: {e}")
        repair_result = "No repair results available yet."
    
    return {
        "repair_results": repair_result
    }

@mcp.tool(description="Get the final report of the infrastructure monitoring workflow.",
          #tags={"monitoring", "infrastructure", "workflow", "report"},
          )
async def get_infrastructure_repair_report(workflow_id: str, run_id: str) -> Dict[str, str]:
    """Return the final report of the infrastructure monitoring workflow. This is the result of the report step.
    This won't have results before the report step is complete."""
    load_dotenv(override=True)
    user = os.environ.get("USER_NAME", "Admin.User") 
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)
    
    try:
        report_result = await handle.query("GetRepairReport")
    except Exception as e:
        print(f"Error querying infrastructure repair report: {e}")
        report_result = "No repair report available yet."
    
    return {
        "report": report_result
    }

@mcp.tool(description="Get the infrastructure inventory data from the database.",
          #tags={"monitoring", "infrastructure", "workflow", "inventory"},
          )
async def get_infrastructure_inventory_data() -> Dict:
    """Load the infrastructure inventory data from a JSON file.
    This loads all the equipment information to get infrastructure details."""
    inventory_file_path = (
        Path(__file__).resolve().parent / "data" / "infrastructure_inventory.json"
    )

    with open(inventory_file_path, "r") as inventory_file:
        inventory_data: dict = json.load(inventory_file)

    return inventory_data

@mcp.tool(description="Get the health metrics data from the monitoring system.",
          #tags={"monitoring", "infrastructure", "workflow", "health"},
          )
async def get_infrastructure_health_metrics() -> Dict:
    """Load the health metrics data from a JSON file.
    This loads all the current health metrics for equipment monitoring."""
    health_file_path = (
        Path(__file__).resolve().parent / "data" / "health_metrics.json"
    )

    with open(health_file_path, "r") as health_file:
        health_data: dict = json.load(health_file)

    return health_data

@mcp.tool(description="Initiate proactive infrastructure monitoring workflow agent.",
          #tags={"monitoring", "infrastructure", "workflow", "proactive"},
          )
async def initiate_proactive_infrastructure_monitoring() -> Dict[str, str]:
    """start/initiate the proactive infrastructure monitoring agent to proactively detect and repair equipment problems 
    that's always running in the background.
    This will run in the background and detect problems on its own, without user intervention.
    It will analyze the infrastructure system, plan repairs, and execute them as needed.
    This is useful for systems that need continuous monitoring and repair capabilities
    It will run indefinitely, detecting and repairing issues as they arise.
    If it's confident enough, it will proactively repair issues without user approval.
    If it's not confident, it will notify the user and wait for approval before proceeding with repairs."""
    
    load_dotenv(override=True)
    user = os.environ.get("USER_NAME", "Admin.User") 
    client = await get_temporal_client()

    start_msg = {
        "prompt": "Continuously monitor and repair equipment issues in the infrastructure system.",
        "metadata": {
            "user": user,  
            "system": "temporal-infra-monitoring-agent",
        }, # could add some proactive notification/callback here
    }
    
    handle = await client.start_workflow(
        InfraMonAgentWorkflowProactive.run,
        start_msg,
        id=f"always-be-monitoring-for-{user}-{uuid.uuid4()}",
        task_queue=TEMPORAL_TASK_QUEUE,
    )
    
    desc = await handle.describe()
    status = await handle.query("GetRepairStatus")    
    
    return {"workflow_id": handle.id, 
            "run_id": handle.result_run_id, 
            "status": status, 
            "description": desc.status.name,
            "proactive": True}

if __name__ == "__main__":
    mcp.run(transport="stdio")