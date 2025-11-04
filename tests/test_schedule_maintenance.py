#!/usr/bin/env python3
"""Test script for schedule_maintenance_tool functionality outside of Temporal activity context."""

import json
import sys
from pathlib import Path

# Add the parent directory to the path to import activities
sys.path.append(str(Path(__file__).resolve().parent.parent))

def mock_schedule_maintenance():
    """Mock version of schedule_maintenance_tool for testing outside Temporal context."""
    from datetime import datetime, timedelta
    
    equipment_id = "EQ-10003"
    maintenance_type = "Preventive Maintenance"
    scheduled_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    priority = "Medium"

    # Update infrastructure_inventory.json to reflect scheduled maintenance
    inventory_path = Path(__file__).resolve().parent.parent / "data" / "infrastructure_inventory.json"
    with open(inventory_path, "r") as file:
        data = json.load(file)
    
    devices = data.get("infrastructure_inventory", [])
    if not devices:
        print("❌ No devices found in infrastructure inventory.")
        return
    
    device_found = False
    for device in devices:
        if device.get("id") == equipment_id:
            device_found = True
            
            # Add scheduled maintenance information
            if "scheduled_maintenance" not in device:
                device["scheduled_maintenance"] = []
            
            # Create maintenance schedule entry
            maintenance_entry = {
                "type": maintenance_type,
                "scheduled_date": scheduled_date,
                "priority": priority,
                "status": "Scheduled",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "estimated_duration_hours": 2 if maintenance_type == "Preventive Maintenance" else 4
            }
            
            # Add to scheduled maintenance list
            device["scheduled_maintenance"].append(maintenance_entry)
            
            # Update maintenance window status
            device["maintenance_window"] = f"Scheduled for {scheduled_date}"
            
            # Add maintenance alert if not already present
            alerts = device.get("alerts", [])
            maintenance_alert = f"Scheduled maintenance: {maintenance_type} on {scheduled_date}"
            if maintenance_alert not in alerts:
                alerts.append(maintenance_alert)
                device["alerts"] = alerts
            
            print(f"✅ Scheduled {maintenance_type} for device {equipment_id} on {scheduled_date}")
            print(f"✅ Maintenance window updated: {device['maintenance_window']}")
            print(f"✅ Alert added: {maintenance_alert}")
            break

    if not device_found:
        print(f"❌ Device {equipment_id} not found in infrastructure inventory.")
        return

    with open(inventory_path, "w") as file:
        json.dump(data, file, indent=2)

    # Add maintenance scheduling note to health metrics
    health_path = Path(__file__).resolve().parent.parent / "data" / "health_metrics.json"
    with open(health_path, "r") as file:
        health_data = json.load(file)
    
    metrics = health_data.get("health_metrics", [])
    if not metrics:
        print("❌ No health metrics found.")
        return
    
    # Find the equipment and add maintenance scheduling note
    equipment_found = False
    for metric in metrics:
        if metric.get("equipment_id") == equipment_id:
            equipment_found = True
            
            # Add maintenance notes to the metric
            if "maintenance_notes" not in metric:
                metric["maintenance_notes"] = []
            
            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            maintenance_note = {
                "timestamp": current_time,
                "type": "Maintenance Scheduled",
                "details": f"{maintenance_type} scheduled for {scheduled_date}",
                "priority": priority,
                "status": "Scheduled"
            }
            
            # Add maintenance note
            metric["maintenance_notes"].append(maintenance_note)
            
            # Keep only the last 5 maintenance notes
            if len(metric["maintenance_notes"]) > 5:
                metric["maintenance_notes"] = metric["maintenance_notes"][-5:]
            
            # Update maintenance status in the metric
            metric["next_maintenance"] = scheduled_date
            metric["maintenance_status"] = "Scheduled"
            
            print(f"✅ Next maintenance date set: {scheduled_date}")
            print(f"✅ Maintenance status updated: Scheduled")
            print(f"✅ Added maintenance scheduling note for device {equipment_id}")
            break
    
    if not equipment_found:
        print(f"⚠️ Equipment {equipment_id} not found in health metrics")

    with open(health_path, "w") as file:
        json.dump(health_data, file, indent=2)

    print(f"✅ Maintenance scheduling completed successfully!")

if __name__ == "__main__":
    print("📅 Testing maintenance scheduling functionality...")
    mock_schedule_maintenance()