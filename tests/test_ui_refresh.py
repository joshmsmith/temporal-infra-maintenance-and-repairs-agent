#!/usr/bin/env python3
"""
Test utility for UI data refresh functionality.

This script modifies infrastructure data files to test the dashboard's
automatic data change detection and refresh capabilities.

Usage:
    python tests/test_ui_refresh.py

The script will interactively modify data files and prompt you to observe
the UI refresh notifications and controls.
"""

import json
import os
from pathlib import Path
import time
from datetime import datetime

def modify_infrastructure_data():
    """Modify infrastructure inventory data to test refresh."""
    project_root = Path(__file__).parent.parent
    data_file = project_root / "data" / "infrastructure_inventory.json"
    
    print(f"Modifying {data_file}")
    
    # Load current data
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Find first equipment and modify its status
    if data['infrastructure_inventory']:
        equipment = data['infrastructure_inventory'][0]
        current_status = equipment.get('status', 'Operational')
        
        # Toggle status for testing
        new_status = 'Down' if current_status == 'Operational' else 'Operational'
        equipment['status'] = new_status
        
        # Update last modified timestamp
        equipment['last_modified'] = datetime.now().isoformat()
        
        print(f"Changed equipment {equipment['id']} status from {current_status} to {new_status}")
    
    # Save modified data
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Data file updated at {datetime.now()}")
    print("You should see a notification in the UI about updated data files!")

def modify_health_metrics():
    """Modify health metrics to test refresh."""
    project_root = Path(__file__).parent.parent
    data_file = project_root / "data" / "health_metrics.json"
    
    print(f"Modifying {data_file}")
    
    # Load current data
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Find first equipment and modify health score
    if data['health_metrics']:
        equipment = data['health_metrics'][0]
        current_score = equipment.get('health_score', 85)
        
        # Modify health score
        import random
        new_score = random.randint(60, 100)
        equipment['health_score'] = new_score
        
        print(f"Changed equipment {equipment['equipment_id']} health score from {current_score} to {new_score}")
    
    # Save modified data
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Health metrics updated at {datetime.now()}")

if __name__ == "__main__":
    print("=" * 50)
    print("Infrastructure Data Modification Test")
    print("=" * 50)
    print()
    print("This script will modify the infrastructure data files")
    print("to test the UI refresh functionality.")
    print()
    print("Make sure the UI is running and watch for:")
    print("1. '📝 Data files have been updated!' notification in sidebar")
    print("2. 'Load Updated Data' button appearing")
    print("3. Success message when data is refreshed")
    print()
    
    input("Press Enter to modify infrastructure inventory data...")
    modify_infrastructure_data()
    
    print()
    input("Press Enter to modify health metrics data...")
    modify_health_metrics()
    
    print()
    print("✅ Data modification complete!")
    print("Check the UI to see the refresh notifications.")