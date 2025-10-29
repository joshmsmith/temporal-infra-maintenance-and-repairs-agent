"""Data loading utilities for infrastructure monitoring dashboard."""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class DataLoader:
    """Handles loading and merging of infrastructure data."""
    
    def __init__(self, data_dir: str = "data"):
        # Get the project root directory (parent of ui directory)
        project_root = Path(__file__).parent.parent.parent
        self.data_dir = project_root / data_dir
        
    def load_infrastructure_inventory(self) -> pd.DataFrame:
        """Load infrastructure inventory data."""
        file_path = self.data_dir / "infrastructure_inventory.json"
        with open(file_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data['infrastructure_inventory'])
    
    def load_health_metrics(self) -> pd.DataFrame:
        """Load health metrics data."""
        file_path = self.data_dir / "health_metrics.json"
        with open(file_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data['health_metrics'])
    
    def load_equipment_life_expectancy(self) -> pd.DataFrame:
        """Load equipment life expectancy data."""
        file_path = self.data_dir / "equipment_life_expectancy.json"
        with open(file_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data['equipment_life_expectancy'])
    
    def merge_all_data(self) -> pd.DataFrame:
        """Merge all data sources into a single DataFrame."""
        # Load all datasets
        inventory = self.load_infrastructure_inventory()
        health = self.load_health_metrics()
        life_expectancy = self.load_equipment_life_expectancy()
        
        # Merge inventory with health metrics on equipment_id/id
        merged = pd.merge(
            inventory, 
            health, 
            left_on='id', 
            right_on='equipment_id', 
            how='left',
            suffixes=('', '_health')
        )
        
        # Merge with life expectancy on model
        merged = pd.merge(
            merged,
            life_expectancy,
            on='model',
            how='left',
            suffixes=('', '_life')
        )
        
        # Clean up duplicate columns
        if 'equipment_id' in merged.columns:
            merged = merged.drop(columns=['equipment_id'])
        
        # Handle duplicate status columns if they exist
        if 'status_health' in merged.columns:
            merged = merged.drop(columns=['status_health'])
            
        # Handle duplicate type columns
        if 'type_life' in merged.columns:
            merged = merged.drop(columns=['type_life'])
            
        # Handle duplicate vendor columns
        if 'vendor_life' in merged.columns:
            merged = merged.drop(columns=['vendor_life'])
        
        return merged
    
    def get_recent_readings_for_equipment(self, equipment_id: str) -> List[Dict]:
        """Get recent readings for a specific equipment."""
        health = self.load_health_metrics()
        equipment_health = health[health['equipment_id'] == equipment_id]
        if not equipment_health.empty:
            return equipment_health.iloc[0]['recent_readings']
        return []


def load_all_data() -> pd.DataFrame:
    """Convenience function to load and merge all data."""
    loader = DataLoader()
    return loader.merge_all_data()
