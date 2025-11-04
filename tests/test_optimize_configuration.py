#!/usr/bin/env python3
"""Test script for optimize_configuration_tool functionality outside of Temporal activity context."""

import json
import sys
from pathlib import Path

# Add the parent directory to the path to import activities
sys.path.append(str(Path(__file__).resolve().parent.parent))

def mock_optimize_configuration():
    """Mock version of optimize_configuration_tool for testing outside Temporal context."""
    from datetime import datetime
    
    equipment_id = "EQ-10002"
    optimization_type = "Performance Optimization"
    optimization_details = "CPU and memory optimization"

    # Update infrastructure_inventory.json to reflect configuration optimization
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
            
            # Ensure device is operational after optimization
            device["status"] = "Operational"
            
            # Update configuration version to reflect optimization
            old_version = device.get("configuration_version", "1.0.0")
            major, minor, patch = old_version.split('.')
            new_minor = str(int(minor) + 1)
            device["configuration_version"] = f"{major}.{new_minor}.{patch}"
            
            # Remove performance-related alerts after optimization
            alerts = device.get("alerts", [])
            device["alerts"] = [alert for alert in alerts if 
                              "performance" not in alert.lower() and 
                              "slow" not in alert.lower() and
                              "cpu" not in alert.lower() and
                              "memory" not in alert.lower()]
            
            print(f"✅ Configuration version updated from {old_version} to {device['configuration_version']}")
            print(f"✅ Optimized configuration for device {equipment_id} - {optimization_type}")
            break

    if not device_found:
        print(f"❌ Device {equipment_id} not found in infrastructure inventory.")
        return

    with open(inventory_path, "w") as file:
        json.dump(data, file, indent=2)

    # Add optimized performance metrics to health_metrics.json
    health_path = Path(__file__).resolve().parent.parent / "data" / "health_metrics.json"
    with open(health_path, "r") as file:
        health_data = json.load(file)
    
    metrics = health_data.get("health_metrics", [])
    if not metrics:
        print("❌ No health metrics found.")
        return
    
    # Find the equipment and add optimized performance metrics
    equipment_found = False
    for metric in metrics:
        if metric.get("equipment_id") == equipment_id:
            equipment_found = True
            
            # Create a new reading showing improved performance after optimization
            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Get the previous reading to show improvement
            previous_reading = metric["recent_readings"][0] if metric["recent_readings"] else {}
            prev_cpu = previous_reading.get("cpu_utilization_percent", 50)
            prev_memory = previous_reading.get("memory_utilization_percent", 60)
            prev_temp = previous_reading.get("temperature_celsius", 55)
            
            # Add metrics showing configuration optimization benefits
            new_reading = {
                "timestamp": current_time,
                "cpu_utilization_percent": max(15, prev_cpu * 0.6),  # Reduce CPU usage by 40%
                "memory_utilization_percent": max(25, prev_memory * 0.7),  # Reduce memory usage by 30%
                "temperature_celsius": max(35, prev_temp * 0.9),  # Reduce temperature by 10%
                "packet_loss_percent": min(0.1, previous_reading.get("packet_loss_percent", 0.5) * 0.5),  # Halve packet loss
                "latency_ms": max(1.0, previous_reading.get("latency_ms", 5.0) * 0.8)  # Reduce latency by 20%
            }
            
            print(f"✅ CPU usage optimized: {prev_cpu}% → {new_reading['cpu_utilization_percent']:.1f}%")
            print(f"✅ Memory usage optimized: {prev_memory}% → {new_reading['memory_utilization_percent']:.1f}%")
            print(f"✅ Temperature reduced: {prev_temp}°C → {new_reading['temperature_celsius']:.1f}°C")
            
            # Add new reading to the beginning of the list
            metric["recent_readings"].insert(0, new_reading)
            
            # Keep only the last 10 readings
            if len(metric["recent_readings"]) > 10:
                metric["recent_readings"] = metric["recent_readings"][:10]
            
            # Update the overall health score to reflect optimization improvements
            old_score = metric.get("health_score", 70)
            metric["health_score"] = min(98.0, old_score + 12.5)
            metric["status"] = "Operational"
            
            print(f"✅ Health score improved from {old_score} to {metric['health_score']}!")
            print(f"✅ Added optimized performance metrics for device {equipment_id}")
            break
    
    if not equipment_found:
        print(f"⚠️ Equipment {equipment_id} not found in health metrics")

    with open(health_path, "w") as file:
        json.dump(health_data, file, indent=2)

    print(f"✅ Configuration optimization completed successfully!")

if __name__ == "__main__":
    print("⚙️ Testing configuration optimization functionality...")
    mock_optimize_configuration()