"""Calculation utilities for infrastructure metrics."""

import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple


def calculate_equipment_age(install_date_str: str) -> float:
    """Calculate equipment age in years from install date string."""
    try:
        install_date = pd.to_datetime(install_date_str)
        today = datetime.now()
        age_days = (today - install_date).days
        return round(age_days / 365.25, 1)
    except:
        return 0.0


def calculate_remaining_life(age_years: float, expected_life_years: float) -> float:
    """Calculate remaining life years."""
    return max(0, expected_life_years - age_years)


def calculate_life_percentage(age_years: float, expected_life_years: float) -> float:
    """Calculate percentage of life used."""
    if expected_life_years == 0:
        return 100.0
    return min(100.0, (age_years / expected_life_years) * 100)


def get_lifecycle_status(life_percentage: float) -> str:
    """Determine lifecycle status based on percentage of life used."""
    if life_percentage >= 90:
        return "Critical"
    elif life_percentage >= 75:
        return "Warning"
    else:
        return "Good"


def calculate_days_until_contract_expiry(expiry_date_str: str) -> int:
    """Calculate days until maintenance contract expires."""
    try:
        expiry_date = pd.to_datetime(expiry_date_str)
        today = datetime.now()
        days = (expiry_date - today).days
        return days
    except:
        return 0


def get_contract_status(days_until_expiry: int) -> str:
    """Determine contract status based on days until expiry."""
    if days_until_expiry < 0:
        return "Expired"
    elif days_until_expiry < 30:
        return "Expiring Soon"
    elif days_until_expiry < 90:
        return "Warning"
    else:
        return "Active"


def get_health_status_color(status: str) -> str:
    """Get color code for health status."""
    status_colors = {
        "Operational": "#28a745",  # Green
        "Degraded": "#ffc107",      # Orange
        "Down": "#dc3545"           # Red
    }
    return status_colors.get(status, "#6c757d")  # Gray as default


def get_severity_color(severity: str) -> str:
    """Get color code for alert severity."""
    severity_colors = {
        "critical": "#dc3545",  # Red
        "warning": "#ffc107",    # Orange
        "info": "#17a2b8"        # Blue
    }
    return severity_colors.get(severity, "#6c757d")  # Gray as default


def calculate_health_score_status(health_score: float) -> str:
    """Determine health score status category."""
    if health_score >= 70:
        return "Good"
    elif health_score >= 40:
        return "Fair"
    else:
        return "Poor"


def get_health_score_color(health_score: float) -> str:
    """Get color code for health score."""
    if health_score >= 70:
        return "#28a745"  # Green
    elif health_score >= 40:
        return "#ffc107"  # Orange
    else:
        return "#dc3545"  # Red


def get_lifecycle_color(life_percentage: float) -> str:
    """Get color code for lifecycle percentage."""
    if life_percentage >= 90:
        return "#dc3545"  # Red
    elif life_percentage >= 75:
        return "#ffc107"  # Orange
    else:
        return "#28a745"  # Green
