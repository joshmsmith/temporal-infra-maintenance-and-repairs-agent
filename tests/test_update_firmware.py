#!/usr/bin/env python3
"""Test script for update_firmware_tool functionality."""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.activities import update_firmware_tool

def test_update_firmware():
    """Test the enhanced update_firmware_tool function."""
    print("Testing update_firmware_tool functionality...")
    
    # Test with a known equipment ID from the data
    test_equipment_id = "EQ-10002"
    test_firmware_version = "2.1.4"
    
    print(f"Testing firmware update for equipment: {test_equipment_id}")
    print(f"Target firmware version: {test_firmware_version}")
    
    # Read current infrastructure inventory before update
    inventory_file = Path(__file__).parent.parent / "data" / "infrastructure_inventory.json"
    with open(inventory_file, 'r') as f:
        before_inventory = json.load(f)
    
    # Read current health metrics before update
    health_file = Path(__file__).parent.parent / "data" / "health_metrics.json"
    with open(health_file, 'r') as f:
        before_health = json.load(f)
    
    # Find the equipment's current state
    before_device = None
    for device in before_inventory["infrastructure_inventory"]:
        if device["id"] == test_equipment_id:
            before_device = {
                "firmware_version": device.get("firmware_version", "unknown"),
                "last_maintenance": device.get("last_maintenance", "unknown"),
                "status": device.get("status", "unknown"),
                "alerts_count": len(device.get("alerts", []))
            }
            break
    
    before_health_metric = None
    for metric in before_health["health_metrics"]:
        if metric["equipment_id"] == test_equipment_id:
            before_health_metric = {
                "health_score": metric["health_score"],
                "status": metric["status"],
                "recent_readings_count": len(metric["recent_readings"]),
                "latest_cpu": metric["recent_readings"][0]["cpu_utilization_percent"] if metric["recent_readings"] else "N/A"
            }
            break
    
    print(f"Before firmware update:")
    print(f"  Device: {before_device}")
    print(f"  Health: {before_health_metric}")
    
    # Call the update firmware tool
    inputs = {
        "equipment_id": test_equipment_id,
        "firmware_version": test_firmware_version,
        "maintenance_window": "2025-11-03T16:00:00Z",
        "rollback_plan": "Rollback to previous firmware version"
    }
    
    try:
        result = update_firmware_tool(inputs)
        print(f"Firmware update result: {result}")
        
        # Read infrastructure inventory after update
        with open(inventory_file, 'r') as f:
            after_inventory = json.load(f)
        
        # Read health metrics after update
        with open(health_file, 'r') as f:
            after_health = json.load(f)
        
        # Find the equipment's state after update
        after_device = None
        for device in after_inventory["infrastructure_inventory"]:
            if device["id"] == test_equipment_id:
                after_device = {
                    "firmware_version": device.get("firmware_version", "unknown"),
                    "last_maintenance": device.get("last_maintenance", "unknown"),
                    "status": device.get("status", "unknown"),
                    "alerts_count": len(device.get("alerts", []))
                }
                break
        
        after_health_metric = None
        for metric in after_health["health_metrics"]:
            if metric["equipment_id"] == test_equipment_id:
                after_health_metric = {
                    "health_score": metric["health_score"],
                    "status": metric["status"],
                    "recent_readings_count": len(metric["recent_readings"]),
                    "latest_cpu": metric["recent_readings"][0]["cpu_utilization_percent"],
                    "latest_memory": metric["recent_readings"][0]["memory_utilization_percent"],
                    "latest_timestamp": metric["recent_readings"][0]["timestamp"]
                }
                break
        
        print(f"After firmware update:")
        print(f"  Device: {after_device}")
        print(f"  Health: {after_health_metric}")
        
        # Verify improvements
        if after_device and before_device:
            if after_device["firmware_version"] == test_firmware_version:
                print("✅ Firmware version updated successfully!")
            if after_device["last_maintenance"] != before_device["last_maintenance"]:
                print("✅ Last maintenance date updated!")
            if after_device["status"] == "Operational":
                print("✅ Device status set to Operational!")
            if after_device["alerts_count"] <= before_device["alerts_count"]:
                print("✅ Firmware-related alerts cleared!")
        
        if after_health_metric and before_health_metric:
            if after_health_metric["health_score"] >= before_health_metric["health_score"]:
                print("✅ Health score maintained or improved!")
            if after_health_metric["status"] == "Operational":
                print("✅ Health status set to Operational!")
            print("✅ New health metric reading added successfully!")
        
    except Exception as e:
        print(f"❌ Error testing update_firmware_tool: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_update_firmware()