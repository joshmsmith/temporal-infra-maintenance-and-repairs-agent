"""
Tests for the infrastructure maintenance activities.
"""

import pytest
import json
from unittest.mock import patch, mock_open
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from activities import load_infrastructure_data, load_health_metrics_data, load_equipment_life_expectancy_data, sanitize_json_response, parse_json_response, get_infrastructure_tools


def test_load_infrastructure_data():
    """Test loading infrastructure data from JSON file."""
    # Mock data
    mock_data = {
        "infrastructure_inventory": [
            {
                "id": "EQ-TEST-001",
                "vendor": "Cisco",
                "model": "Test Switch",
                "status": "Operational"
            }
        ]
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        result = load_infrastructure_data()
        assert len(result) == 1
        assert result[0]["id"] == "EQ-TEST-001"
        assert result[0]["vendor"] == "Cisco"


def test_load_health_metrics_data():
    """Test loading health metrics data from JSON file."""
    # Mock data
    mock_data = {
        "health_metrics": [
            {
                "equipment_id": "EQ-TEST-001",
                "status": "Operational",
                "health_score": 95.5
            }
        ]
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        result = load_health_metrics_data()
        assert len(result) == 1
        assert result[0]["equipment_id"] == "EQ-TEST-001"
        assert result[0]["health_score"] == 95.5


def test_load_equipment_life_expectancy_data():
    """Test loading equipment life expectancy data from JSON file."""
    # Mock data
    mock_data = {
        "equipment_life_expectancy": [
            {
                "model": "Test Switch",
                "type": "Network Switch",
                "vendor": "Cisco",
                "expected_life_years": 10
            }
        ]
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        result = load_equipment_life_expectancy_data()
        assert len(result) == 1
        assert result[0]["model"] == "Test Switch"
        assert result[0]["vendor"] == "Cisco"
        assert result[0]["expected_life_years"] == 10


def test_sanitize_json_response():
    """Test JSON response sanitization."""
    # Test with markdown code blocks
    markdown_json = '''```json
    {
        "confidence_score": 0.85,
        "additional_notes": "Test message"
    }
    ```'''
    
    result = sanitize_json_response(markdown_json)
    expected = '''    {
        "confidence_score": 0.85,
        "additional_notes": "Test message"
    }'''
    assert result.strip() == expected.strip()
    
    # Test with regular JSON
    regular_json = '{"test": "value"}'
    result = sanitize_json_response(regular_json)
    assert result == regular_json


def test_parse_json_response():
    """Test JSON response parsing."""
    json_string = '{"confidence_score": 0.75, "issues": []}'
    result = parse_json_response(json_string)
    
    assert isinstance(result, dict)
    assert result["confidence_score"] == 0.75
    assert result["issues"] == []


def test_get_infrastructure_tools():
    """Test getting available infrastructure tools."""
    tools = get_infrastructure_tools()
    
    assert isinstance(tools, dict)
    assert len(tools) > 0
    assert "restart_device" in tools
    assert "update_firmware" in tools
    assert "schedule_maintenance" in tools
    
    # Check tool structure
    restart_tool = tools["restart_device"]
    assert "description" in restart_tool
    assert "parameters" in restart_tool
    assert isinstance(restart_tool["parameters"], list)


def test_infrastructure_tools_completeness():
    """Test that all infrastructure tools have required fields."""
    tools = get_infrastructure_tools()
    
    for tool_name, tool_info in tools.items():
        assert "description" in tool_info, f"Tool {tool_name} missing description"
        assert "parameters" in tool_info, f"Tool {tool_name} missing parameters"
        assert isinstance(tool_info["description"], str), f"Tool {tool_name} description should be string"
        assert isinstance(tool_info["parameters"], list), f"Tool {tool_name} parameters should be list"
        assert len(tool_info["description"]) > 10, f"Tool {tool_name} description too short"
        assert len(tool_info["parameters"]) > 0, f"Tool {tool_name} should have parameters"


if __name__ == "__main__":
    pytest.main([__file__])