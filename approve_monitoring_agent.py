import asyncio
import os

from shared.config import TEMPORAL_TASK_QUEUE, get_temporal_client
from dotenv import load_dotenv

import argparse
parser = argparse.ArgumentParser(description="Approve repair for an infrastructure monitoring agent workflow.")
parser.add_argument(
    "--workflow-id",
    type=str,
    default="infra-monitoring-agent-for-Admin.User-a736473c-61d9-44e7-98b4-ad5309a8579e",
    help="The ID of the workflow to approve.",
)
args = parser.parse_args() 

async def main(workflow_id: str) -> None:
    """Approve the infrastructure monitoring agent workflow for execution.
    Used to approve the infrastructure monitoring workflow after it has proposed repairs and is ready for execution."""
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
        
    print("Approving the infrastructure monitoring workflow")
    await handle.signal("ApproveRepair", user)
    print("Infrastructure monitoring workflow approved!")

if __name__ == "__main__":
    asyncio.run(main(args.workflow_id))