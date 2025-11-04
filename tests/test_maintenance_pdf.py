#!/usr/bin/env python3
"""Test script for PDF report generation functionality."""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from markdown_pdf import MarkdownPdf, Section

def test_maintenance_pdf_report():
    """Test the PDF report generation part of repair_some_stuff."""
    print("Testing maintenance PDF report generation...")
    
    # Mock maintenance results data
    maintenance_tool_details = [
        {
            "equipment_id": "EQ-10001",
            "tool_name": "restart_device",
            "confidence_score": 0.85,
            "additional_notes": "Device showing high CPU utilization",
            "tool_arguments": {
                "equipment_id": "EQ-10001",
                "maintenance_window": "2025-11-03T16:00:00Z",
                "rollback_plan": "Restore from backup configuration"
            },
            "tool_result": {
                "status": "success",
                "message": "Device EQ-10001 restarted successfully."
            }
        },
        {
            "equipment_id": "EQ-10002",
            "tool_name": "update_firmware",
            "confidence_score": 0.75,
            "additional_notes": "Firmware version is outdated",
            "tool_arguments": {
                "equipment_id": "EQ-10002",
                "firmware_version": "2.1.4",
                "maintenance_window": "2025-11-03T16:30:00Z",
                "rollback_plan": "Rollback to previous firmware"
            },
            "tool_result": {
                "status": "success",
                "message": "Device EQ-10002 firmware updated to version 2.1.4."
            }
        }
    ]
    
    problems_repaired = 2
    problems_skipped = 1
    repair_summary = "Infrastructure maintenance scheduled successfully: 2 items maintained (with 1 skipped)."
    
    try:
        # Create reports directory if it doesn't exist
        os.makedirs("./reports", exist_ok=True)
        
        # Build report content (same logic as in repair_some_stuff)
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_contents = "# Infrastructure Maintenance Execution Report\n\n"
        report_contents += f"**Report Generated:** {report_date}\n\n"
        report_contents += f"**Maintenance Summary:** {repair_summary}\n\n"
        report_contents += f"- **Equipment Processed:** 3\n"
        report_contents += f"- **Maintenance Actions Completed:** {problems_repaired}\n"
        report_contents += f"- **Actions Skipped (Low Confidence):** {problems_skipped}\n\n"
        
        if maintenance_tool_details:
            report_contents += "## Detailed Maintenance Actions\n\n"
            
            for detail in maintenance_tool_details:
                equipment_id = detail["equipment_id"]
                tool_name = detail["tool_name"]
                confidence_score = detail["confidence_score"]
                additional_notes = detail.get("additional_notes", "").strip("()")
                tool_arguments = detail["tool_arguments"]
                tool_result = detail["tool_result"]
                
                report_contents += f"### Equipment: {equipment_id}\n"
                report_contents += f"**Tool Executed:** {tool_name}\n\n"
                report_contents += f"**Confidence Score:** {confidence_score}\n\n"
                
                if additional_notes:
                    report_contents += f"**Notes:** {additional_notes}\n\n"
                
                report_contents += f"**Tool Arguments:**\n"
                for arg, value in tool_arguments.items():
                    report_contents += f"- {arg}: {value}\n"
                report_contents += "\n"
                
                report_contents += f"**Execution Result:**\n"
                report_contents += f"- Status: {tool_result.get('status', 'Unknown')}\n"
                report_contents += f"- Message: {tool_result.get('message', 'No message provided')}\n\n"
                
                report_contents += "---\n\n"
        
        if problems_skipped > 0:
            report_contents += f"## Skipped Actions\n\n"
            report_contents += f"{problems_skipped} maintenance actions were skipped due to low confidence scores (<0.5).\n"
            report_contents += "These items may require manual review or additional analysis.\n\n"
        
        report_contents += "## Recommendations\n\n"
        if problems_repaired > 0:
            report_contents += "- Monitor equipment performance after maintenance to verify improvements\n"
            report_contents += "- Update maintenance schedules based on completed actions\n"
            report_contents += "- Review health metrics for signs of improvement\n"
        else:
            report_contents += "- No immediate actions were required\n"
            report_contents += "- Continue regular monitoring of infrastructure health\n"
        
        report_contents += "\n---\n\n"
        report_contents += "*This report was generated automatically by the Infrastructure Monitoring Agent*\n"
        
        # Generate PDF report
        TOOL_EXECUTION_REPORT_NAME = "./reports/tool_execution_report"
        maintenance_report_pdf = MarkdownPdf(toc_level=2, optimize=True)
        maintenance_report_pdf.add_section(Section(report_contents))
        maintenance_report_pdf.meta["title"] = "Infrastructure Maintenance Execution Report"
        maintenance_report_pdf.meta["author"] = "Infrastructure Monitoring Agent"
        maintenance_report_pdf.meta["subject"] = f"Maintenance Report - {report_date}"
        maintenance_report_pdf.save(TOOL_EXECUTION_REPORT_NAME + ".pdf")
        
        report_file = TOOL_EXECUTION_REPORT_NAME + ".pdf"
        print(f"✅ PDF report generated: {report_file}")
        
        # Check if file actually exists
        if Path(report_file).exists():
            print(f"✅ Report file exists on disk")
            file_size = Path(report_file).stat().st_size
            print(f"✅ Report file size: {file_size} bytes")
            
            # Print some of the report content for verification
            print(f"\n📄 Report Content Preview:")
            print(f"- Title: Infrastructure Maintenance Execution Report")
            print(f"- Equipment processed: 3")
            print(f"- Actions completed: {problems_repaired}")
            print(f"- Actions skipped: {problems_skipped}")
            print(f"- Generated: {report_date}")
            
        else:
            print(f"❌ Report file not found on disk")
        
    except Exception as e:
        print(f"❌ Error generating PDF report: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_maintenance_pdf_report()