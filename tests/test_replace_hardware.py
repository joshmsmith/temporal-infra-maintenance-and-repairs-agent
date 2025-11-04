#!/usr/bin/env python3
"""Test script for replace_hardware_tool functionality outside of Temporal activity context."""

import json
import sys
from pathlib import Path

# Add the parent directory to the path to import activities
sys.path.append(str(Path(__file__).resolve().parent.parent))

def mock_replace_hardware():
    """Mock version of replace_hardware_tool for testing outside Temporal context."""
    from datetime import datetime
    
    equipment_id = "EQ-10001"
    component = "Network Switch"
    replacement_part = "Cisco Catalyst 9300"

    # Update infrastructure_inventory.json to reflect hardware replacement
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
            
            # Update last maintenance date to current date
            device["last_maintenance"] = datetime.now().strftime("%Y-%m-%d")
            
            # Ensure device is operational after hardware replacement
            device["status"] = "Operational"
            
            # Reset uptime since hardware replacement typically requires restart
            device["uptime_days"] = 0
            
            # Remove any hardware-related alerts
            alerts = device.get("alerts", [])
            device["alerts"] = [alert for alert in alerts if 
                              "hardware" not in alert.lower() and 
                              "component" not in alert.lower() and
                              "failure" not in alert.lower()]
            
            print(f"✅ Replaced {component} on device {equipment_id} with {replacement_part}")
            break

    if not device_found:
        print(f"❌ Device {equipment_id} not found in infrastructure inventory.")
        return

    with open(inventory_path, "w") as file:
        json.dump(data, file, indent=2)

    # Add a new health metric to health_metrics.json
    health_path = Path(__file__).resolve().parent.parent / "data" / "health_metrics.json"
    with open(health_path, "r") as file:
        health_data = json.load(file)
    
    metrics = health_data.get("health_metrics", [])
    if not metrics:
        print("❌ No health metrics found.")
        return
    
    # Find the equipment and add a new excellent reading
    equipment_found = False
    for metric in metrics:
        if metric.get("equipment_id") == equipment_id:
            equipment_found = True
            
            # Create a new reading showing excellent performance after hardware replacement
            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Add metrics showing hardware replacement benefits
            new_reading = {
                "timestamp": current_time,
                "cpu_utilization_percent": 12,  # Very low CPU with new hardware
                "memory_utilization_percent": 20,  # Excellent memory performance
                "temperature_celsius": 38,  # Cool running temperature
                "packet_loss_percent": 0.001,  # Virtually no packet loss
                "latency_ms": 1.8  # Excellent latency with new hardware
            }
            
            # Add new reading to the beginning of the list
            metric["recent_readings"].insert(0, new_reading)
            
            # Keep only the last 10 readings
            if len(metric["recent_readings"]) > 10:
                metric["recent_readings"] = metric["recent_readings"][:10]
            
            # Update the overall health score to excellent after hardware replacement
            old_score = metric.get("health_score", 0)
            metric["health_score"] = 95.8  # Excellent health score
            metric["status"] = "Operational"
            
            print(f"✅ Health score updated from {old_score} to {metric['health_score']}!")
            print(f"✅ Added new health metric reading for device {equipment_id}")
            break
    
    if not equipment_found:
        print(f"⚠️ Equipment {equipment_id} not found in health metrics")

    with open(health_path, "w") as file:
        json.dump(health_data, file, indent=2)

    print(f"✅ Hardware replacement completed successfully!")

if __name__ == "__main__":
    print("🔧 Testing hardware replacement functionality...")
    mock_replace_hardware()