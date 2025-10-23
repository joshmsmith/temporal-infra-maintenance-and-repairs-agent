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

