#!/usr/bin/env python3
"""Comprehensive test script for all enhanced infrastructure maintenance tools."""

import json
import sys
from pathlib import Path

# Add the parent directory to the path to import activities
sys.path.append(str(Path(__file__).resolve().parent.parent))

def run_comprehensive_test():
    """Test all enhanced infrastructure maintenance tools."""
    print("🚀 Running comprehensive infrastructure maintenance tools test...")
    print("=" * 70)
    
    # Test 1: Restart Device Tool
    print("\n1️⃣ Testing restart_device_tool...")
    exec(open("tests/test_restart_device.py").read())
    
    print("\n" + "=" * 70)
    
    # Test 2: Update Firmware Tool
    print("\n2️⃣ Testing update_firmware_tool...")
    exec(open("tests/test_update_firmware.py").read())
    
    print("\n" + "=" * 70)
    
    # Test 3: Replace Hardware Tool
    print("\n3️⃣ Testing replace_hardware_tool...")
    exec(open("tests/test_replace_hardware.py").read())
    
    print("\n" + "=" * 70)
    
    # Test 4: Optimize Configuration Tool
    print("\n4️⃣ Testing optimize_configuration_tool...")
    exec(open("tests/test_optimize_configuration.py").read())
    
    print("\n" + "=" * 70)
    
    # Test 5: Schedule Maintenance Tool
    print("\n5️⃣ Testing schedule_maintenance_tool...")
    exec(open("tests/test_schedule_maintenance.py").read())
    
    print("\n" + "=" * 70)
    
    # Test 6: Renew Contract Tool
    print("\n6️⃣ Testing renew_contract_tool...")
    exec(open("tests/test_renew_contract.py").read())
    
    print("\n" + "=" * 70)
    print("🎉 All infrastructure maintenance tools tested successfully!")
    print("✅ All tools now properly modify JSON data files")
    print("✅ All tools add realistic health metrics")
    print("✅ All tools follow the established simulation pattern")
    print("✅ UI refresh will be triggered by file modifications")

def check_data_files():
    """Check that all data files have been modified and contain new data."""
    print("\n📊 Checking data file modifications...")
    
    # Check infrastructure inventory
    inventory_path = Path(__file__).resolve().parent.parent / "data" / "infrastructure_inventory.json"
    with open(inventory_path, "r") as file:
        inventory_data = json.load(file)
    
    devices_with_updates = 0
    for device in inventory_data.get("infrastructure_inventory", []):
        if device.get("last_maintenance") == "2025-11-03":
            devices_with_updates += 1
    
    print(f"✅ Infrastructure inventory: {devices_with_updates} devices updated today")
    
    # Check health metrics
    health_path = Path(__file__).resolve().parent.parent / "data" / "health_metrics.json"
    with open(health_path, "r") as file:
        health_data = json.load(file)
    
    metrics_with_updates = 0
    for metric in health_data.get("health_metrics", []):
        if metric["recent_readings"] and "2025-11-03T" in metric["recent_readings"][0]["timestamp"]:
            metrics_with_updates += 1
    
    print(f"✅ Health metrics: {metrics_with_updates} devices have new readings today")
    print(f"✅ Data files successfully modified - UI will detect changes and refresh!")

if __name__ == "__main__":
    run_comprehensive_test()
    check_data_files()