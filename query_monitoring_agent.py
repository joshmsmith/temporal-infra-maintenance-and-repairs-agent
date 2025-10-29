import asyncio
import uuid
import os

from shared.config import TEMPORAL_TASK_QUEUE, get_temporal_client
from dotenv import load_dotenv

import argparse
parser = argparse.ArgumentParser(description="Query an infrastructure monitoring agent workflow.")
parser.add_argument(
    "--workflow-id",
    type=str,
    default="infra-monitoring-agent-for-Admin.User-a736473c-61d9-44e7-98b4-ad5309a8579e",
    help="The ID of the workflow to query.",
)
args = parser.parse_args() 

async def main(workflow_id: str) -> None:
    """Query the infrastructure monitoring agent workflow for its status and results.
    Used to check the status of an infrastructure monitoring workflow and get details about proposed repairs and results."""
    # Load environment variables
    load_dotenv(override=True)
    user = os.environ.get("USER_NAME", "Admin.User") 
    print(f"Using user: {user}")

    # Create client connected to server at the given address
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id=workflow_id)
    print(f"Workflow handle: {handle}")
    try:
        status = await handle.query("GetRepairStatus")
        print(f"Current infrastructure status: {status}")
    except Exception as e:
        print(f"Error querying infrastructure status: {e}")
        status = "Unknown"

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
        # proposed_tools = planning_result.get("proposed_tools", [])
        # additional_notes = planning_result.get("additional_notes", "")

        # if not proposed_tools:
        #     print("No proposed tools found for infrastructure repair.")
        # else:
        #     print("Proposed Infrastructure Repairs:")
        #     for tool in proposed_tools:
        #         confidence_score = tool.get("confidence_score", 0.0)
        #         additional_notes = tool.get("additional_notes", "")
        #         if additional_notes:
        #             additional_notes = f"({additional_notes})"
        #         tool_name = tool.get("tool_name", "Unknown Tool Name")
        #         if confidence_score < 0.5:
        #             print(f"Low confidence score for repair: {confidence_score}. Tools with low confidence will not be executed.")
                
        #         print(f"  - {tool_name}: confidence score {confidence_score} {additional_notes}")
        #         tool_arguments = tool.get("tool_arguments", {})
        #         if not isinstance(tool_arguments, dict):
        #             print(f"Expected a dictionary for tool arguments, got {type(tool_arguments)}")
        #         for arg_name, arg_value in tool_arguments.items():
        #             print(f"    - {arg_name}: {arg_value}")
    except Exception as e:
        print(f"Error querying infrastructure planning result: {e}")
        proposed_tools = "No tools proposed yet."

    print("Infrastructure Tool Execution results:")
    try:
        repair_result = await handle.query("GetRepairToolResults")
    except Exception as e:
        print(f"Error querying infrastructure tool results: {e}")
        repair_result = "No repair results available yet."
        
    
    if not isinstance(repair_result, dict):
        print(f"Expected a dictionary for repair results, got {type(repair_result)}")
    else:
        for key, value in repair_result.items():
            if isinstance(value, list):
                print(f"  - {key}: (results omitted for brevity, {len(value)} items)")
            else:
                print(f"  - {key}: {value}")

    
    try:
        print(f"*** Final Infrastructure Report: ***")
        repair_report = await handle.query("GetRepairReport")

        report_summary = repair_report.get("repairs_summary", "No summary available")
        
        print(f"{report_summary}")
    except Exception as e:
        print(f"Error querying infrastructure repair report: {e}")
        report_result = "No infrastructure repair report available yet."
    
    print(f"Infrastructure status: {status}")

if __name__ == "__main__":
    asyncio.run(main(args.workflow_id))