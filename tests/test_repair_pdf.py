#!/usr/bin/env python3
"""Test script for repair_some_stuff PDF report functionality."""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.activities import repair_some_stuff

def test_repair_pdf_report():
    """Test the enhanced repair_some_stuff function with PDF report generation."""
    print("Testing repair_some_stuff PDF report generation...")
    
    # Create mock input data that simulates a planning result
    mock_input = {
        "planning_result": {
            "proposed_tools": {
                "EQ-10001": [
                    {
                        "tool_name": "restart_device",
                        "confidence_score": 0.85,
                        "additional_notes": "Device showing high CPU utilization",
                        "tool_arguments": {
                            "equipment_id": "EQ-10001",
                            "maintenance_window": "2025-11-03T16:00:00Z",
                            "rollback_plan": "Restore from backup configuration"
                        }
                    }
                ],
                "EQ-10002": [
                    {
                        "tool_name": "update_firmware",
                        "confidence_score": 0.75,
                        "additional_notes": "Firmware version is outdated",
                        "tool_arguments": {
                            "equipment_id": "EQ-10002",
                            "firmware_version": "2.1.4",
                            "maintenance_window": "2025-11-03T16:30:00Z",
                            "rollback_plan": "Rollback to previous firmware"
                        }
                    }
                ],
                "EQ-10003": [
                    {
                        "tool_name": "schedule_maintenance",
                        "confidence_score": 0.45,  # Low confidence - should be skipped
                        "additional_notes": "Routine maintenance due",
                        "tool_arguments": {
                            "equipment_id": "EQ-10003",
                            "maintenance_type": "routine_inspection",
                            "maintenance_window": "2025-11-03T17:00:00Z",
                            "technician": "field_tech_01"
                        }
                    }
                ]
            }
        }
    }
    
    try:
        print("Executing maintenance operations...")
        
        # Note: We'll need to run this in an async context, but for testing 
        # we can call the function directly since it doesn't use await internally
        import asyncio
        result = asyncio.run(repair_some_stuff(mock_input))
        
        print(f"Maintenance result: {result}")
        
        # Check if PDF was generated
        report_file = result.get("report_file")
        if report_file:
            print(f"✅ PDF report generated: {report_file}")
            
            # Check if file actually exists
            if Path(report_file).exists():
                print(f"✅ Report file exists on disk")
                file_size = Path(report_file).stat().st_size
                print(f"✅ Report file size: {file_size} bytes")
            else:
                print(f"❌ Report file not found on disk")
        else:
            print(f"❌ No report file generated")
            if "report_error" in result:
                print(f"Report error: {result['report_error']}")
        
        # Print summary
        print(f"\n📊 Maintenance Summary:")
        print(f"- Equipment processed: {len(mock_input['planning_result']['proposed_tools'])}")
        print(f"- Actions completed: {result.get('problems_repaired', 0)}")
        print(f"- Actions skipped: {result.get('problems_skipped', 0)}")
        print(f"- Summary: {result.get('repair_summary', 'No summary')}")
        
    except Exception as e:
        print(f"❌ Error testing repair_some_stuff: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_repair_pdf_report()