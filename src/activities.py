from asyncio import sleep
from datetime import datetime
import os
import json
from pathlib import Path
from typing import Callable
from temporalio import activity
from dotenv import load_dotenv

from litellm import completion
from temporalio.exceptions import ApplicationError
from shared.config import TEMPORAL_TASK_QUEUE, get_temporal_client
from markdown_pdf import MarkdownPdf, Section


load_dotenv(override=True)

# Define the date for analysis to be a useful date relative to the static networking data
DATE_FOR_ANALYSIS = datetime(2025, 10, 23)
PLANNING_REPORT_NAME = "./reports/planning_report"
TOOL_EXECUTION_REPORT_NAME = "./reports/tool_execution_report"
MONOLITH_REPORT_NAME = "./reports/monolith_report"


'''These activities demonstrate the detect, analyze, repair, and report steps of the infrastructure monitoring agent workflow.'''
@activity.defn
async def detect(input: dict) -> dict:
    return await detect_some_stuff(input)

@activity.defn
async def analyze(input: dict) -> dict:
    return await analyze_some_stuff(input)

@activity.defn
async def plan_repair(input: dict) -> dict:
    return await plan_to_repair_some_stuff(input)

@activity.defn
async def notify(input: dict) -> dict:
    return await notify_interested_parties(input)

@activity.defn
async def execute_repairs(input: dict) -> dict:
    return await repair_some_stuff(input)

@activity.defn
async def report(input: dict) -> dict:
    return await report_some_stuff(input)


async def detect_some_stuff(input: dict) -> dict:
    """
    This is an automated helper agent that detects infrastructure problems.
    It uses a Large Language Model (LLM) to analyze infrastructure components and determine if there are issues.
    It heartbeats the activity to indicate progress 
    It returns a dict response with the detection results: primarily a confidence_score.
    """
    # Load the infrastructure data (from JSON files)
    infrastructure_data = load_infrastructure_data()
    health_metrics_data = load_health_metrics_data()
    equipment_life_expectancy_data = load_equipment_life_expectancy_data()

    activity.heartbeat("Infrastructure data loaded, detection in progress...")
    
    # Use the LLM to detect issues in the infrastructure
    # Get the LLM model and key from environment variables
    llm_model = os.environ.get("LLM_MODEL", "openai/gpt-4")
    llm_key = os.environ.get("LLM_KEY")
    if not llm_model or not llm_key:
        exception_message = f"LLM model or key not found in environment variables."
        activity.logger.error(exception_message)
        raise ApplicationError(exception_message)
    
    # This is a context instruction for the LLM to understand its task
    context_instructions = "You are a helpful assistant that detects problems in network infrastructure. " \
    "Your task is to analyze the provided infrastructure components, health metrics, and equipment life expectancy to detect issues or anomalies. " \
    "You will receive infrastructure inventory data with device status, alerts, temperatures, CPU/memory utilization, and uptime. " \
    "You will also receive health metrics with performance data like packet loss, latency, and recent readings. " \
    "You will also receive equipment life expectancy data to help assess if devices are nearing end of life. " \
    "Look for common problems such as: devices with 'Down' status, high temperature (>70C), high CPU utilization (>80%), " \
    "high memory utilization (>85%), packet loss >1%, latency >20ms, expired maintenance contracts, " \
    "devices with critical alerts, devices that haven't had maintenance in over 2 years, or devices approaching their expected life span. " \
    "Ensure your response is valid JSON and does not contain any markdown formatting. " \
    "The response should be a JSON object with a 'confidence_score' of how " \
    "sure you are that there are infrastructure issues requiring attention (0.0 to 1.0). " \
    "Feel free to include additional notes in 'additional_notes' if necessary. " \
    "If there are no critical issues, note that in additional_notes. " \
    "The infrastructure inventory to analyze is as follows: " \
    + json.dumps(infrastructure_data, indent=2) \
    + "\nThe health metrics data is as follows: " \
    + json.dumps(health_metrics_data, indent=2) \
    + "\nThe equipment life expectancy data is as follows: " \
    + json.dumps(equipment_life_expectancy_data, indent=2)
    
    activity.logger.debug(f"Context instructions for LLM: {context_instructions}")

    messages = [
        {
            "role": "system",
            "content": context_instructions
            + ". The current date is "
            + DATE_FOR_ANALYSIS.strftime("%B %d, %Y"),
        },
    ]

    try:
        completion_kwargs = {
            "model": llm_model,
            "messages": messages,
            "api_key": llm_key,
        }

        response = completion(**completion_kwargs)

        response_content = response.choices[0].message.content
        activity.logger.debug(f"Raw LLM response: {repr(response_content)}")
        activity.logger.debug(f"LLM response content: {response_content}")
        activity.logger.debug(f"LLM response type: {type(response_content)}")
        activity.logger.debug(
            f"LLM response length: {len(response_content) if response_content else 'None'}"
        )

        if not response_content:
            exception_message = "LLM response content is empty."
            activity.logger.error(exception_message)
            raise ApplicationError(exception_message)
        
        # Sanitize the response to ensure it is valid JSON
        response_content = sanitize_json_response(response_content)
        activity.logger.debug(f"Sanitized response: {repr(response_content)}")
        detection_json_response: dict = parse_json_response(response_content)

        activity.logger.debug(f"Validating Detection Result: {detection_json_response}")
        if "confidence_score" not in detection_json_response:
            exception_message = "Detection response does not contain 'confidence_score'."
            activity.logger.error(exception_message)
            raise ApplicationError(exception_message)
        
        confidence_score = detection_json_response.get("confidence_score", 0.0)
        activity.logger.info(f"Infrastructure detection confidence score: {confidence_score}")
        return detection_json_response
    
    except Exception as e:
        activity.logger.error(f"Error in LLM completion: {str(e)}")
        raise


def load_infrastructure_data() -> dict:
    """Load infrastructure inventory data from JSON file."""
    try:
        with open("./data/infrastructure_inventory.json", "r") as file:
            data = json.load(file)
            return data.get("infrastructure_inventory", [])
    except FileNotFoundError:
        activity.logger.warning("Infrastructure inventory file not found, returning empty data")
        return []
    except json.JSONDecodeError as e:
        activity.logger.error(f"Error parsing infrastructure inventory JSON: {e}")
        raise ApplicationError(f"Error parsing infrastructure inventory JSON: {e}")


def load_health_metrics_data() -> dict:
    """Load health metrics data from JSON file."""
    try:
        with open("./data/health_metrics.json", "r") as file:
            data = json.load(file)
            return data.get("health_metrics", [])
    except FileNotFoundError:
        activity.logger.warning("Health metrics file not found, returning empty data")
        return []
    except json.JSONDecodeError as e:
        activity.logger.error(f"Error parsing health metrics JSON: {e}")
        raise ApplicationError(f"Error parsing health metrics JSON: {e}")


def load_equipment_life_expectancy_data() -> dict:
    """Load equipment life expectancy data from JSON file."""
    try:
        with open("./data/equipment_life_expectancy.json", "r") as file:
            data = json.load(file)
            return data.get("equipment_life_expectancy", [])
    except FileNotFoundError:
        activity.logger.warning("Equipment life expectancy file not found, returning empty data")
        return []
    except json.JSONDecodeError as e:
        activity.logger.error(f"Error parsing equipment life expectancy JSON: {e}")
        raise ApplicationError(f"Error parsing equipment life expectancy JSON: {e}")



def sanitize_json_response(response_content: str) -> str:
    """
    Sanitizes the response content to ensure it's valid JSON.
    Removes markdown code blocks and other formatting.
    """
    if not response_content:
        return response_content
    
    # Remove markdown code blocks
    if "```json" in response_content:
        response_content = response_content.split("```json")[1].split("```")[0].strip()
    elif "```" in response_content:
        response_content = response_content.split("```")[1].split("```")[0].strip()
    
    return response_content.strip()


def parse_json_response(response_content: str) -> dict:
    """
    Parses the JSON response content and returns it as a dictionary.
    """
    try:
        return json.loads(response_content)
    except json.JSONDecodeError as e:
        activity.logger.error(f"Error parsing JSON response: {e}")
        activity.logger.error(f"Response content: {response_content}")
        raise ApplicationError(f"Error parsing JSON response: {e}")


async def analyze_some_stuff(input: dict) -> dict:
    """
    This is an automated helper agent that analyzes infrastructure problems.
    It uses a Large Language Model (LLM) to analyze infrastructure components and define specific issues.
    It heartbeats the activity to indicate progress 
    It returns a dictionary response with the analysis results: 
        - infrastructure components
        - their specific problems
        - severity levels
        - how sure it is via a confidence_score.
    """    
    # Load the infrastructure data 
    infrastructure_data = load_infrastructure_data()
    health_metrics_data = load_health_metrics_data()
    equipment_life_expectancy_data = load_equipment_life_expectancy_data()

    activity.heartbeat("Infrastructure data loaded, analysis in progress...")
    
    # Use the LLM to analyze issues in the infrastructure
    llm_model = os.environ.get("LLM_MODEL", "openai/gpt-4")
    llm_key = os.environ.get("LLM_KEY")
    if not llm_model or not llm_key:
        exception_message = f"LLM model or key not found in environment variables."
        activity.logger.error(exception_message)
        raise ApplicationError(exception_message)

    # Define the messages for the LLM completion
    context_instructions = "You are a helpful assistant that detects and analyzes problems in network infrastructure. " \
    "Your task is to analyze the provided infrastructure components, health metrics, and equipment life expectancy to identify specific issues and their severity. " \
    "You will receive infrastructure inventory data, health metrics data, and equipment life expectancy data in JSON format. " \
    "Look for specific problems and categorize them by severity: critical, warning, or info. " \
    "Critical issues include: devices down, high packet loss (>2%), extreme temperatures (>75C), expired contracts, devices past expected life. " \
    "Warning issues include: high utilization (CPU >80%, Memory >85%), moderate packet loss (0.5-2%), high latency (>15ms), devices approaching expected life (>80% of life span). " \
    "Info issues include: devices needing routine maintenance, moderate utilization levels, devices approaching mid-life. " \
    "Ensure your response is valid JSON and does not contain any markdown formatting. " \
    "The response should be a JSON object with a key 'issues' that contains a list of detected issues, " \
    "each with an 'equipment_id', 'issue' description, 'severity' (critical/warning/info), " \
    "the 'site' where the equipment is located, and " \
    "a 'confidence_score' of how sure you are there is a problem. " \
    "Feel free to include additional notes in 'additional_notes' if necessary. " \
    "If there are no issues, note that in additional_notes. " \
    "The infrastructure inventory to analyze is as follows: " \
    + json.dumps(infrastructure_data, indent=2) \
    + "\nThe health metrics data is as follows: " \
    + json.dumps(health_metrics_data, indent=2) \
    + "\nThe equipment life expectancy data is as follows: " \
    + json.dumps(equipment_life_expectancy_data, indent=2)
    
    messages = [
        {
            "role": "system",
            "content": context_instructions
            + ". The current date is "
            + DATE_FOR_ANALYSIS.strftime("%B %d, %Y"),
        },
    ]

    try:
        completion_kwargs = {
            "model": llm_model,
            "messages": messages,
            "api_key": llm_key,
        }

        response = completion(**completion_kwargs)

        response_content = response.choices[0].message.content
        activity.logger.debug(f"Raw LLM response: {repr(response_content)}")
        activity.logger.debug(f"LLM response content: {response_content}")
        activity.logger.debug(f"LLM response type: {type(response_content)}")
        activity.logger.debug(
            f"LLM response length: {len(response_content) if response_content else 'None'}"
        )

        if not response_content:
            exception_message = "LLM response content is empty."
            activity.logger.error(exception_message)
            raise ApplicationError(exception_message)
        
        # Sanitize the response to ensure it is valid JSON
        response_content = sanitize_json_response(response_content)
        activity.logger.debug(f"Sanitized response: {repr(response_content)}")
        parsed_response: dict = parse_json_response(response_content)

        activity.logger.info(f"Validating Analysis Result...")
        validate_analysis_results(parsed_response)
        
        return parsed_response
    
    except Exception as e:
        activity.logger.error(f"Error in LLM completion: {str(e)}")
        raise


def validate_analysis_results(parsed_response):
    """Validate the analysis results from the LLM response.
    This checks that the response contains the expected structure and types."""
    if not parsed_response:
        exception_message = "LLM response content is empty."
        activity.logger.error(exception_message)
        raise ApplicationError(exception_message)
    if not isinstance(parsed_response, dict):
        activity.logger.error(f"Expected a dictionary for response content, got {type(parsed_response)}")
        raise ApplicationError(f"Expected a dictionary for response content, got {type(parsed_response)}")
    else:
        activity.logger.debug(f"Response content type: {type(parsed_response)}")
        notes = parsed_response.get("additional_notes", "")
        activity.logger.debug(f"Additional Notes: {notes}")
        confidence_score = parsed_response.get("confidence_score", 0.0)
        activity.logger.debug(f"Analysis confidence score: {confidence_score}")
        issues = parsed_response.get("issues", [])
        if not issues:
            activity.logger.info("No issues detected in the infrastructure.")
        else:
            activity.logger.debug(f"Detected issues: {issues}")


async def plan_to_repair_some_stuff(input: dict) -> dict:
    """
    This function is used by the Infrastructure Maintenance workflows to plan repairs for detected problems.
    It uses a Large Language Model (LLM) to analyze infrastructure issues and plan maintenance actions.
    It returns a dictionary response with the planned maintenance actions.
    """    
    # Load the infrastructure data 
    infrastructure_data = load_infrastructure_data()
    health_metrics_data = load_health_metrics_data()
    equipment_life_expectancy_data = load_equipment_life_expectancy_data()

    activity.heartbeat("Infrastructure data loaded, maintenance planning in progress...")
    
    llm_model = os.environ.get("LLM_MODEL", "openai/gpt-4")
    llm_key = os.environ.get("LLM_KEY")
    if not llm_model or not llm_key:
        exception_message = f"LLM model or key not found in environment variables."
        activity.logger.error(exception_message)
        raise ApplicationError(exception_message)
    
    tool_list = get_infrastructure_tools()

    # Define the messages for the LLM completion
    context_instructions = "You are a helpful assistant that proposes scheduled maintenance solutions for infrastructure problems. " \
    "Your task is to analyze the provided infrastructure components, their problems, and propose maintenance actions " \
    "using the provided tool_list. " \
    "You will receive infrastructure data and health metrics in JSON format. " \
    "You will also receive a list of issues that need maintenance actions. " \
    "You will also receive a list of tools that can be used for maintenance. " \
    "Ensure your response is valid JSON and does not contain any markdown formatting. " \
    "The response should be a JSON object with a key 'proposed_tools' that contains " \
    "a set of equipment with key equipment_id. Equipment should have one or more proposed maintenance tools with key tool_name." \
    "Each tool entry should include tool_arguments for each tool, and " \
    "a confidence_score of how confident you are that the tool will solve the problem. " \
    "Feel free to include additional notes in 'additional_notes' if necessary. " \
    "If there are no proposed tools for maintenance, note that in additional_notes. " \
    "Include an overall_confidence_score for the proposed tools indicating confidence that the maintenance should be triggered. " \
    "The infrastructure inventory to analyze is as follows: " \
    + json.dumps(infrastructure_data, indent=2)

    context_instructions = context_instructions + "\nThe list of issues to repair is as follows: " \
    + json.dumps(input.get("problems_to_repair", []), indent=2) 
    context_instructions = context_instructions + "\nThe list of tools that can be used for maintenance is as follows: " \
    + json.dumps(tool_list, indent=2)
    context_instructions = context_instructions + "\nThe health metrics data is as follows: " \
    + json.dumps(health_metrics_data, indent=2)
    context_instructions = context_instructions + "\nThe equipment life expectancy data is as follows: " \
    + json.dumps(equipment_life_expectancy_data, indent=2)
    activity.logger.debug(f"Context instructions for LLM: {context_instructions}")

    messages = [
        {
            "role": "system",
            "content": context_instructions
            + ". The current date is "
            + DATE_FOR_ANALYSIS.strftime("%B %d, %Y"),
        },
    ]

    try:
        completion_kwargs = {
            "model": llm_model,
            "messages": messages,
            "api_key": llm_key,
        }

        response = completion(**completion_kwargs)
        activity.heartbeat("Got response, validating...")

        response_content = response.choices[0].message.content
        activity.logger.debug(f"Raw LLM response: {repr(response_content)}")
        
        if not response_content:
            exception_message = "LLM response content is empty."
            activity.logger.error(exception_message)
            raise ApplicationError(exception_message)
        
        activity.logger.debug(f"Sanitizing response content: {repr(response_content)}")
        response_content = sanitize_json_response(response_content)
        activity.logger.debug(f"Sanitized response: {repr(response_content)}")
        parsed_response: dict = parse_json_response(response_content)

        activity.logger.info(f"Validating Planning Result...")
        
        proposed_tools_for_all_equipment = parsed_response.get("proposed_tools", {})
        additional_repair_notes = parsed_response.get("additional_notes", "")
        overall_confidence_score = parsed_response.get("overall_confidence_score", 0.0)
        
        # Generate infrastructure maintenance planning report
        report_contents: str
        if not proposed_tools_for_all_equipment:
            activity.logger.info("No proposed tools found for infrastructure maintenance.")
            report_contents = "# No proposed tools found for infrastructure maintenance."
        else:
            activity.logger.debug(f"Proposed tools for all equipment: {proposed_tools_for_all_equipment}")
            activity.logger.info(f"Number of equipment with proposed tools: {len(proposed_tools_for_all_equipment)}")
            
            report_contents = "# Proposed Infrastructure Maintenance:\n"
            report_contents += f"- Overall confidence score for proposed tools: {overall_confidence_score}\n"
            report_contents += f"- Additional notes: {additional_repair_notes}\n"
            report_contents += f"- Number of equipment with proposed tools: {len(proposed_tools_for_all_equipment)}\n"
            report_contents += "## Proposed Equipment and Tools:\n"
            for equipment_id, equipment_tools in proposed_tools_for_all_equipment.items():
                if not isinstance(equipment_tools, list):
                    activity.logger.error(f"Expected a list for equipment {equipment_tools}, got {type(equipment_tools)}")
                    activity.logger.error(f"Equipment {equipment_id} proposed tools: {equipment_tools}")
                    raise ApplicationError(f"Expected a list for equipment {equipment_tools}, got {type(equipment_tools)}")
                report_contents += f"### Equipment ID: {equipment_id}\n"
                if not equipment_tools:
                    report_contents += "- No proposed tools for this equipment.\n"
                    continue
                for tool in equipment_tools:
                    confidence_score = tool.get("confidence_score", 0.0)
                    additional_notes = tool.get("additional_notes", "N/A")
                    tool_name = tool.get("tool_name", "Unknown Tool Name")
                    tool_arguments = tool.get("tool_arguments", {})
                    if not tool_name or tool_name == "Unknown Tool Name" or not tool_arguments:
                        activity.logger.error(f"Tool name or arguments missing for tool {tool_name} for equipment {equipment_id}: {tool}.")
                        raise ApplicationError(f"Tool name or arguments missing for tool {tool_name} for equipment {equipment_id}.")
                    if not isinstance(tool_arguments, dict):
                        activity.logger.error(f"Expected a dictionary for tool arguments for tool {tool_name} for equipment {equipment_id}, got {type(tool_arguments)} for {tool}")
                        raise ApplicationError(f"Expected a dictionary for tool arguments for tool {tool_name} for equipment {equipment_id}, got {type(tool_arguments)}")
                    activity.logger.debug(f"Tool arguments for tool {tool_name} for equipment {equipment_id}: {tool_arguments}")
                    report_contents += f"### {tool_name}"
                    report_contents += f"\n- Confidence Score: {confidence_score}\n- Additional Notes: {additional_notes}\n"
                    report_contents += f"- Tool Arguments: {json.dumps(tool_arguments, indent=2)}\n"
        
        activity.logger.info(f"...Planning results valid, generating reports.")

        # Create reports directory if it doesn't exist
        os.makedirs("./reports", exist_ok=True)

        # Write the report to a PDF file with markdown-pdf
        planning_report_pdf = MarkdownPdf(toc_level=2, optimize=True)
        planning_report_pdf.add_section(Section(report_contents))
        planning_report_pdf.meta["title"] = "Infrastructure Maintenance Planning Report"
        planning_report_pdf.meta["author"] = "Infrastructure Monitoring Agent"
        planning_report_pdf.save(PLANNING_REPORT_NAME + ".pdf")

        activity.logger.info(f"Planning report saved to {PLANNING_REPORT_NAME + '.pdf'}")
        
        return parsed_response
    
    except Exception as e:
        activity.logger.error(f"Error in LLM completion: {str(e)}")
        raise   


def get_infrastructure_tools() -> dict:
    """Return available infrastructure maintenance tools."""
    return {
        "restart_device": {
            "description": "Restart a network device to resolve performance issues",
            "parameters": ["equipment_id", "maintenance_window", "rollback_plan"]
        },
        "update_firmware": {
            "description": "Update device firmware to latest stable version",
            "parameters": ["equipment_id", "firmware_version", "maintenance_window", "rollback_plan"]
        },
        "replace_hardware": {
            "description": "Schedule hardware replacement for failed components",
            "parameters": ["equipment_id", "component", "replacement_part", "maintenance_window"]
        },
        "optimize_configuration": {
            "description": "Optimize device configuration for better performance",
            "parameters": ["equipment_id", "configuration_changes", "maintenance_window"]
        },
        "schedule_maintenance": {
            "description": "Schedule routine maintenance for equipment",
            "parameters": ["equipment_id", "maintenance_type", "maintenance_window", "technician"]
        },
        "renew_contract": {
            "description": "Renew maintenance contract for equipment",
            "parameters": ["equipment_id", "contract_type", "renewal_period"]
        }
    }


async def notify_interested_parties(input: dict) -> dict:
    """ This function notifies interested parties about infrastructure maintenance planning results."""
    notification_info = input.get("notification_info")
    if not notification_info or not isinstance(notification_info, dict):
        activity.logger.warning("No notification info provided, skipping notification.")
        return {
            "notification_status": "Improper notification info provided.",
        }
    
    activity.logger.info(f"Infrastructure maintenance notification sent to operations team")
    return {
        "notification_status": "Operations team notified of scheduled maintenance.",
        "notification_details": f"Maintenance report available at {PLANNING_REPORT_NAME}"
    }


async def repair_some_stuff(input: dict) -> dict:
    """
    This function executes infrastructure maintenance tools and schedules repair actions.
    """
    activity.logger.debug(f"Running infrastructure maintenance with input: {input}")

    results = {}
    results["maintenance_tool_details"] = []
    problems_repaired: int = 0
    problems_skipped: int = 0
    
    proposed_tools_for_all_equipment = input.get("planning_result", {}).get("proposed_tools", [])
    if not proposed_tools_for_all_equipment:
        activity.logger.info("No proposed maintenance tools found.")
        return {"repair_summary": "No proposed maintenance tools found."}

    for equipment_id, equipment in proposed_tools_for_all_equipment.items():
        print(f"*** Repairing order: {equipment_id} ***")
        if not isinstance(equipment, list):
            activity.logger.error(f"Expected a dictionary for equpiment, got {type(list)}")
            raise ApplicationError(f"Expected a dictionary for equipment, got {type(list)}")
        for tool in equipment:
            activity.heartbeat(f"Repair for order {equipment_id} in progress...") # heartbeat the activity per tool
            activity.logger.debug(f"Data for tool selected: {tool}")        
            confidence_score = tool.get("confidence_score", 0.0)
            activity.logger.debug(f"Confidence Score: {confidence_score}")
            additional_notes = tool.get("additional_notes", "")
            if additional_notes:
                additional_notes = f"({additional_notes})"
            activity.logger.debug(f"Additional Notes: {additional_notes}")
            tool_name = tool.get("tool_name", "Unknown Tool Name")
            activity.logger.debug(f"Using tool: {tool_name}")
            if confidence_score < 0.5:
                activity.logger.warning(f"Low confidence score for repair: {confidence_score}. Skipping repair for order {equipment_id}.")
                problems_skipped += 1
                continue
            else:
                print(f"- Executing {tool_name} with confidence score {confidence_score} {additional_notes}")
                tool_arguments = tool.get("tool_arguments", {})
                if not isinstance(tool_arguments, dict):
                    activity.logger.error(f"Expected a dictionary for tool arguments, got {type(tool_arguments)}")
                    raise ApplicationError(f"Expected a dictionary for tool arguments, got {type(tool_arguments)}")
                activity.logger.debug(f"Tool arguments: {tool_arguments}")
                
                tool_function = get_equipment_tool_function_by_name(tool_name)
                try:
                    tool_result = tool_function(tool_arguments)
                    activity.logger.debug(f"Tool {tool_name} executed with result: {tool_result}")

                except Exception as e:
                    activity.logger.error(f"Error executing tool {tool_name}: {e}")
                    raise ApplicationError(f"Error executing tool {tool_name}: {e}")

                print(f" - Tool {tool_name} executed successfully for order {equipment_id}!")
                problems_repaired += 1
                results["maintenance_tool_details"].append({
                    "equipment_id": equipment_id,
                    "tool_name": tool_name,
                    "confidence_score": confidence_score,
                    "additional_notes": additional_notes,
                    "tool_arguments": tool_arguments,
                    "tool_result": tool_result
                })
    activity.logger.info(f"Executing maintenance on {len(proposed_tools_for_all_equipment)} pieces of equipment")
    
    results["problems_repaired"] = problems_repaired
    results["problems_skipped"] = problems_skipped
    results["repair_summary"] = f"Infrastructure maintenance scheduled successfully: {problems_repaired} items maintained (with {problems_skipped} skipped)."
    
    activity.logger.info(f"Maintenance Summary: {results['repair_summary']}")
    return results


async def report_some_stuff(input: dict) -> dict:
    """
    This function generates a report on infrastructure maintenance activities.
    """
    activity.logger.info("Generating infrastructure maintenance report...")
    
    return {
        "report_summary": "Infrastructure maintenance completed successfully",
        "additional_notes": "All critical issues have been addressed through scheduled maintenance",
        "report_result": "Report generated successfully."
    }

def get_equipment_tool_function_by_name(tool_name: str) -> Callable[[dict], dict]:
    """
    Returns the function corresponding to the given tool name.
    Raises an ApplicationError if the tool name is not found.
    """
    tool_function_map = get_equipment_tool_function_map()
    if tool_name not in tool_function_map:
        exception_message = f"Tool {tool_name} not found in tool function map."
        activity.logger.error(exception_message)
        raise ApplicationError(exception_message)
    
    return tool_function_map[tool_name]

def get_equipment_tool_function_map() -> dict:
    """
    Returns a mapping of tool names to their corresponding functions.
    This can be used to dynamically call tools based on the context.
    """
    return {
        "restart_device": restart_device_tool,
        "update_firmware": update_firmware_tool,
        "replace_hardware": replace_hardware_tool,
        "optimize_configuration": optimize_configuration_tool,
        "schedule_maintenance": schedule_maintenance_tool,
        "renew_contract": renew_contract_tool,
    }

def restart_device_tool(inputs: dict) -> dict:
    """Simulates restarting a network device."""
    equipment_id = inputs.get("equipment_id")

    # Update infrastructure_inventory.json to set status to 'Operational', uptime days to 0, and remove alerts.
    with open(Path(__file__).resolve().parent.parent / "data" / "infrastructure_inventory.json", "r") as file:
        data = json.load(file)
    devices = data.get("infrastructure_inventory", [])
    if not devices:
        exception_message = "No devices found in infrastructure inventory."
        activity.logger.error(exception_message)
        raise ApplicationError(exception_message)
    for device in devices:
        if device.get("id") == equipment_id:
            device["status"] = "Operational"
            device["uptime_days"] = 0
            device["alerts"] = []
            break

    with open(Path(__file__).resolve().parent.parent / "data" / "infrastructure_inventory.json", "w") as file:
        json.dump(data, file, indent=2)

    return {"status": "success", "message": f"Device {equipment_id} restarted successfully."}

def update_firmware_tool(inputs: dict) -> dict:
    """Simulates updating device firmware."""
    equipment_id = inputs.get("equipment_id")
    firmware_version = inputs.get("firmware_version")

    return {"status": "success", "message": f"Device {equipment_id} firmware updated to version {firmware_version}."}

def replace_hardware_tool(inputs: dict) -> dict:
    """Simulates replacing hardware components."""
    equipment_id = inputs.get("equipment_id")
    component = inputs.get("component")

    return {"status": "success", "message": f"Component {component} on device {equipment_id} replaced successfully."}

def optimize_configuration_tool(inputs: dict) -> dict:
    """Simulates optimizing device configuration."""
    equipment_id = inputs.get("equipment_id")

    return {"status": "success", "message": f"Configuration for device {equipment_id} optimized successfully."}

def schedule_maintenance_tool(inputs: dict) -> dict:
    """Simulates scheduling routine maintenance."""
    equipment_id = inputs.get("equipment_id")
    maintenance_type = inputs.get("maintenance_type")

    return {"status": "success", "message": f"{maintenance_type} maintenance scheduled for device {equipment_id}."}

def renew_contract_tool(inputs: dict) -> dict:
    """Simulates renewing maintenance contract."""
    equipment_id = inputs.get("equipment_id")
    contract_type = inputs.get("contract_type")

    return {"status": "success", "message": f"{contract_type} contract renewed for device {equipment_id}."}