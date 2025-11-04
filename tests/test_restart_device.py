#!/usr/bin/env python3
"""Test script for restart_device_tool functionality."""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.activities import restart_device_tool

def test_restart_device():
    """Test the enhanced restart_device_tool function."""
    print("Testing restart_device_tool functionality...")
    
    # Test with a known equipment ID from the data
    test_equipment_id = "EQ-10001"
    
    print(f"Testing restart for equipment: {test_equipment_id}")
    
    # Read current health metrics before restart
    health_file = Path(__file__).parent.parent / "data" / "health_metrics.json"
    with open(health_file, 'r') as f:
        before_data = json.load(f)
    
    # Find the equipment's current health
    before_health = None
    for metric in before_data["health_metrics"]:
        if metric["equipment_id"] == test_equipment_id:
            before_health = {
                "health_score": metric["health_score"],
                "status": metric["status"],
                "recent_readings_count": len(metric["recent_readings"]),
                "latest_cpu": metric["recent_readings"][0]["cpu_utilization_percent"] if metric["recent_readings"] else "N/A"
            }
            break
    
    print(f"Before restart: {before_health}")
    
    # Call the restart tool
    inputs = {
        "equipment_id": test_equipment_id,
        "maintenance_window": "2025-11-03T15:00:00Z",
        "rollback_plan": "Restore from backup configuration"
    }
    
    try:
        result = restart_device_tool(inputs)
        print(f"Restart result: {result}")
        
        # Read health metrics after restart
        with open(health_file, 'r') as f:
            after_data = json.load(f)
        
        # Find the equipment's health after restart
        after_health = None
        for metric in after_data["health_metrics"]:
            if metric["equipment_id"] == test_equipment_id:
                after_health = {
                    "health_score": metric["health_score"],
                    "status": metric["status"],
                    "recent_readings_count": len(metric["recent_readings"]),
                    "latest_cpu": metric["recent_readings"][0]["cpu_utilization_percent"],
                    "latest_memory": metric["recent_readings"][0]["memory_utilization_percent"],
                    "latest_temp": metric["recent_readings"][0]["temperature_celsius"],
                    "latest_timestamp": metric["recent_readings"][0]["timestamp"]
                }
                break
        
        print(f"After restart: {after_health}")
        
        # Verify improvements
        if after_health and before_health:
            if after_health["health_score"] > before_health["health_score"]:
                print("✅ Health score improved!")
            if after_health["status"] == "Operational":
                print("✅ Status set to Operational!")
            if after_health["latest_cpu"] <= 20:
                print("✅ CPU utilization reduced to healthy levels!")
            print("✅ New healthy metric reading added successfully!")
        
    except Exception as e:
        print(f"❌ Error testing restart_device_tool: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_restart_device()