#!/usr/bin/env python3
"""Test script for renew_contract_tool functionality outside of Temporal activity context."""

import json
import sys
from pathlib import Path

# Add the parent directory to the path to import activities
sys.path.append(str(Path(__file__).resolve().parent.parent))

def mock_renew_contract():
    """Mock version of renew_contract_tool for testing outside Temporal context."""
    from datetime import datetime, timedelta
    
    equipment_id = "EQ-10004"
    contract_type = "Premium Maintenance Contract"
    contract_duration = "12 months"
    vendor = "TechSupport Pro Inc."

    # Update infrastructure_inventory.json to reflect contract renewal
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
            
            # Update contract information
            current_date = datetime.now()
            expiration_date = current_date + timedelta(days=365 if "12" in contract_duration else 180)
            
            old_contract = device.get("contract_info", {})
            device["contract_info"] = {
                "type": contract_type,
                "vendor": vendor,
                "start_date": current_date.strftime("%Y-%m-%d"),
                "expiration_date": expiration_date.strftime("%Y-%m-%d"),
                "duration": contract_duration,
                "status": "Active",
                "renewal_date": current_date.strftime("%Y-%m-%d")
            }
            
            # Update warranty status
            device["warranty_status"] = "Active"
            device["warranty_expiration"] = expiration_date.strftime("%Y-%m-%d")
            
            # Remove contract-related alerts if any
            alerts = device.get("alerts", [])
            device["alerts"] = [alert for alert in alerts if 
                              "contract" not in alert.lower() and 
                              "warranty" not in alert.lower() and
                              "expired" not in alert.lower()]
            
            # Add contract renewal confirmation alert
            device["alerts"].append(f"Contract renewed: {contract_type} active until {expiration_date.strftime('%Y-%m-%d')}")
            
            print(f"✅ Contract renewed: {contract_type}")
            print(f"✅ Vendor: {vendor}")
            print(f"✅ Contract active until: {expiration_date.strftime('%Y-%m-%d')}")
            print(f"✅ Warranty status updated: Active")
            break

    if not device_found:
        print(f"❌ Device {equipment_id} not found in infrastructure inventory.")
        return

    with open(inventory_path, "w") as file:
        json.dump(data, file, indent=2)

    # Add contract renewal note to health metrics
    health_path = Path(__file__).resolve().parent.parent / "data" / "health_metrics.json"
    with open(health_path, "r") as file:
        health_data = json.load(file)
    
    metrics = health_data.get("health_metrics", [])
    if not metrics:
        print("❌ No health metrics found.")
        return
    
    # Find the equipment and add contract renewal note
    equipment_found = False
    for metric in metrics:
        if metric.get("equipment_id") == equipment_id:
            equipment_found = True
            
            # Add contract information to the metric
            if "contract_notes" not in metric:
                metric["contract_notes"] = []
            
            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            contract_note = {
                "timestamp": current_time,
                "type": "Contract Renewed",
                "contract_type": contract_type,
                "vendor": vendor,
                "duration": contract_duration,
                "status": "Active"
            }
            
            # Add contract note
            metric["contract_notes"].append(contract_note)
            
            # Keep only the last 3 contract notes
            if len(metric["contract_notes"]) > 3:
                metric["contract_notes"] = metric["contract_notes"][-3:]
            
            # Update contract status in the metric
            metric["contract_status"] = "Active"
            metric["warranty_status"] = "Active"
            
            print(f"✅ Contract status updated: Active")
            print(f"✅ Added contract renewal note for device {equipment_id}")
            break
    
    if not equipment_found:
        print(f"⚠️ Equipment {equipment_id} not found in health metrics")

    with open(health_path, "w") as file:
        json.dump(health_data, file, indent=2)

    print(f"✅ Contract renewal completed successfully!")

if __name__ == "__main__":
    print("📋 Testing contract renewal functionality...")
    mock_renew_contract()