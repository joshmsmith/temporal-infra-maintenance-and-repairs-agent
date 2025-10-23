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
    "Your task is to analyze the provided infrastructure components and health metrics to detect issues or anomalies. " \
    "You will receive infrastructure inventory data with device status, alerts, temperatures, CPU/memory utilization, and uptime. " \
    "You will also receive health metrics with performance data like packet loss, latency, and recent readings. " \
    "Look for common problems such as: devices with 'Down' status, high temperature (>70C), high CPU utilization (>80%), " \
    "high memory utilization (>85%), packet loss >1%, latency >20ms, expired maintenance contracts, " \
    "devices with critical alerts, or devices that haven't had maintenance in over 2 years. " \
    "Ensure your response is valid JSON and does not contain any markdown formatting. " \
    "The response should be a JSON object with a 'confidence_score' of how " \
    "sure you are that there are infrastructure issues requiring attention (0.0 to 1.0). " \
    "Feel free to include additional notes in 'additional_notes' if necessary. " \
    "If there are no critical issues, note that in additional_notes. " \
    "The infrastructure inventory to analyze is as follows: " \
    + json.dumps(infrastructure_data, indent=2) \
    + "\nThe health metrics data is as follows: " \
    + json.dumps(health_metrics_data, indent=2)
    
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
    "Your task is to analyze the provided infrastructure components and health metrics to identify specific issues and their severity. " \
    "You will receive infrastructure inventory data and health metrics data in JSON format. " \
    "Look for specific problems and categorize them by severity: critical, warning, or info. " \
    "Critical issues include: devices down, high packet loss (>2%), extreme temperatures (>75C), expired contracts. " \
    "Warning issues include: high utilization (CPU >80%, Memory >85%), moderate packet loss (0.5-2%), high latency (>15ms). " \
    "Info issues include: devices needing routine maintenance, moderate utilization levels. " \
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
    + json.dumps(health_metrics_data, indent=2)
    
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
        "additional_notes": "All critical issues have been addressed through scheduled maintenance"
    }