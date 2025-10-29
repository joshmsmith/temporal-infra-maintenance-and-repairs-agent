import asyncio
import uuid
import os

from shared.config import TEMPORAL_TASK_QUEUE, get_temporal_client
from src.workflows import InfraMonAgentWorkflow
from dotenv import load_dotenv

import argparse
parser = argparse.ArgumentParser(description="Run the infrastructure monitoring agent workflow.")
parser.add_argument(
    "--auto-approve",
    action="store_true",
    help="Automatically approve the repair workflow without user input.",
)
args = parser.parse_args() 

async def main(auto_approve: bool) -> None:
    """Run the infrastructure monitoring agent workflow.
    This workflow analyzes and repairs infrastructure in the monitoring system.
    It will propose repairs and wait for user approval before executing them.
    Use the --auto-approve flag to skip user approval and proceed with repairs automatically."""
    
    # Load environment variables
    load_dotenv(override=True)
    user = os.environ.get("USER_NAME", "Admin.User") 
    # Create client connected to server at the given address
    client = await get_temporal_client()

    # Start the workflow with an initial prompt
    start_msg = {
        "prompt": "Analyze and repair the infrastructure in the monitoring system.",
        "metadata": {
            "user": user,  
            "system": "temporal-infra-maintenance-agent",
        },
    }
    
    handle = await client.start_workflow(
        InfraMonAgentWorkflow.run,
        start_msg,
        id=f"infra-monitoring-agent-for-{user}-{uuid.uuid4()}",
        task_queue=TEMPORAL_TASK_QUEUE,
    )
    print(f"{user}'s Infrastructure Monitoring Workflow started with ID: {handle.id}")

    repairs_planned = False
    while not repairs_planned:
        try:
            repairs_planned = await handle.query("IsRepairPlanned")
            status = await handle.query("GetRepairStatus")
            print(f"Current infrastructure status: {status}")
        except Exception as e:
            print(f"Error querying infrastructure status: {e}")
        await asyncio.sleep(5)  # Wait before checking the status again
    
    print("Infrastructure repair planning is complete.")
    try:
        planning_result : dict = await handle.query("GetRepairPlanningResult")
        proposed_tools = planning_result.get("proposed_tools", [])
        additional_notes = planning_result.get("additional_notes", "")
        confidence_score = planning_result.get("confidence_score", 0.0)

    except Exception as e:
        print(f"Error querying infrastructure planning result: {e}")
        proposed_tools = "No tools proposed yet."
    
    try:
        planning_result: dict = await handle.query("GetRepairPlanningResult")
        proposed_tools = planning_result.get("proposed_tools", [])
        additional_notes = planning_result.get("additional_notes", "")
        confidence_score = planning_result.get("confidence_score", 0.0)
        
        print(f"Additional Notes: {additional_notes}")
        print(f"Confidence Score: {confidence_score}")
        if not proposed_tools:
            print("No proposed tools found for infrastructure repair.")
        elif isinstance(proposed_tools, str):
            print(proposed_tools)
        else:
            print("Proposed Infrastructure Repairs:")
            
            for equipment_id, equipment_tools in proposed_tools.items():
                print(f"### Equipment ID: {equipment_id}\n")
                for tool in equipment_tools:
                    confidence_score = tool.get("confidence_score", 0.0)
                    additional_notes = tool.get("additional_notes", "")
                    if additional_notes:
                        additional_notes = f"({additional_notes})"
                    tool_name = tool.get("tool_name", "Unknown Tool Name")
                    if confidence_score < 0.5:
                        print(f"Low confidence score for tool repair: {confidence_score}. Tools with low confidence will not be executed.")

                    print(f"  - {equipment_id}: {tool_name}: confidence score {confidence_score} {additional_notes}")
                    tool_arguments = tool.get("tool_arguments", {})
                    if not isinstance(tool_arguments, dict):
                        print(f"Expected a dictionary for tool arguments, got {type(tool_arguments)}")
                    for arg_name, arg_value in tool_arguments.items():
                        print(f"    - {arg_name}: {arg_value}")
    except Exception as e:
        print(f"Error querying infrastructure planning result: {e}")
        proposed_tools = "No tools proposed yet."

    if not auto_approve:
        print("Waiting for user approval to proceed with infrastructure repairs...")
        try:
            approved = await handle.query("IsRepairApproved")
            if approved:
                print("Infrastructure repair has already been approved.")
            else:
                print("Infrastructure repair has not been approved yet. Waiting for user input...")
                # Wait for user input to approve the repair
                while not approved:
                    user_input = input("Do you approve the infrastructure repair? (yes/no): ").strip().lower()
                    if user_input == "yes":
                        await handle.signal("ApproveRepair", user)
                        approved = True
                        print("Infrastructure repair approved by user.")
                    elif user_input == "no":
                        print("Infrastructure repair not approved. Exiting workflow.")
                        # todo send signal to workflow to reject repair
                        await handle.signal("RejectRepair", user)
                        return
                    else:
                        print("Invalid input. Please enter 'yes' or 'no'.")
        except Exception as e:
            print(f"Error querying infrastructure repair approval status: {e}")
    else:
        print("Auto-approval is enabled. Proceeding with infrastructure repair workflow.")
        print("Auto-approving the infrastructure repair workflow")
        await handle.signal("ApproveRepair", user)

    repairs_complete = False
    while not repairs_complete:
        try:
            status = await handle.query("GetRepairStatus")
            if status == "REPAIR-COMPLETED" or status == "NO-REPAIR-NEEDED" or status == "REJECTED":
                repairs_complete = True
                break
            elif status == "REPAIR-FAILED":
                print("Infrastructure repair failed. Exiting workflow.")
                break
            print(f"Current infrastructure status: {status}")
        except Exception as e:
            print(f"Error querying infrastructure status: {e}")
        await asyncio.sleep(5)  # Wait before checking the status again
    
    # Wait for the workflow to complete
    result = await handle.result()
    print(f"Infrastructure Monitoring Workflow completed with result: {result}")
    print("Review the infrastructure repair report for more details.")

if __name__ == "__main__":
    asyncio.run(main(args.auto_approve))