# Infrastructure Monitoring Dashboard

A comprehensive Streamlit dashboard for monitoring network infrastructure equipment across multiple data centers, designed for Temporal Solutions Architecture demonstrations.

## 🌟 Features

- **📊 Overview Dashboard** - Executive summary with KPIs, status distribution, and at-risk equipment
- **📦 Equipment Inventory** - Searchable, filterable equipment list with detailed views
- **📈 Health Metrics** - Time-series visualization of performance metrics over time
- **⏳ Lifecycle Management** - Equipment age tracking, maintenance scheduling, and contract management
- **🔔 Alerts & Notifications** - Real-time alert monitoring with severity-based filtering

## 📋 Prerequisites

- Python 3.8 or higher

## 🚀 Installation

1. **Install dependencies using Poetry:**
   ```bash
   poetry install
   ```

2. **Navigate to the ui directory (optional):**
   ```bash
   cd ui
   ```

## ▶️ Running the Dashboard

### Quick Start

From the project root directory:
```bash
poetry run streamlit run ui/app.py
```

Or from the ui directory:
```bash
cd ui
poetry run streamlit run app.py
```

The dashboard will automatically open in your default web browser at `http://localhost:8501`

### Custom Port

To run on a different port:
```bash
poetry run streamlit run ui/app.py --server.port 8502
```

### Headless Mode (Server Deployment)

```bash
poetry run streamlit run ui/app.py --server.headless true
```

## 📊 Dashboard Pages

### 1. Overview
- Total equipment count and status summary
- Critical and warning alert counts
- Average health score across all equipment
- Equipment status distribution by site
- Health score histogram
- Equipment breakdown by vendor and type
- At-risk equipment identification

### 2. Equipment Inventory
- Complete equipment catalog with sorting and filtering
- Advanced filters: Status, Site, Vendor, Equipment Type, Health Score
- Real-time search by Equipment ID or Model
- Detailed equipment information including:
  - Basic specs (model, type, vendor)
  - Location and network details
  - Current status and health metrics
  - Maintenance history
  - Active alerts

### 3. Health Metrics
- Individual equipment selection for detailed analysis
- Time-series charts for the last 5 days:
  - CPU utilization trends
  - Memory utilization trends
  - Temperature monitoring
  - Network performance (packet loss, latency)
- Statistical summaries (average, min, max)
- Multi-equipment comparison (up to 5 devices)

### 4. Lifecycle Management
- Equipment age vs. expected life analysis
- Lifecycle status indicators (Good/Warning/Critical)
- Equipment needing replacement soon
- Maintenance contract tracking:
  - Active contracts
  - Expiring contracts (within 90 days)
  - Expired contracts
- Lifecycle distribution by equipment type

### 5. Alerts & Notifications
- Total active alerts with severity breakdown
- Critical alerts with detailed information
- Warning alerts in expandable sections
- Advanced filtering by severity, site, and alert type
- Alert timeline visualization
- Alerts by equipment type analysis
- CSV export functionality

## 🎨 Color Coding

The dashboard uses consistent color coding throughout:

- 🟢 **Green (#28a745)** - Operational/Good status
- 🟡 **Orange (#ffc107)** - Degraded/Warning status
- 🔴 **Red (#dc3545)** - Down/Critical status
- 🔵 **Blue (#007bff)** - Primary accent color

## 📁 Data Sources

The dashboard loads data from JSON files in the `data/` directory:

- `infrastructure_inventory.json` - Equipment details and specifications
- `health_metrics.json` - Real-time performance metrics
- `equipment_life_expectancy.json` - Expected lifespan by model

## 🔄 Data Refresh

The dashboard provides multiple ways to refresh data when infrastructure changes occur:

### Automatic Data Detection
- **File Change Detection**: Automatically detects when data files are modified
- **Smart Notifications**: Shows "📝 Data files have been updated!" when changes are detected
- **One-Click Refresh**: Click "Load Updated Data" to refresh with new data

### Manual Refresh Options
- **Page-Level Refresh**: Each page has a "🔄 Refresh Data" button in the top-right corner
- **Sidebar Controls**: 
  - "🔄 Refresh Now" - Immediate data refresh
  - "🗑️ Clear Cache" - Clears all cached data and refreshes

### Auto-Refresh Settings
- **Configurable Intervals**: Choose from Off, 30 seconds, 1 minute, or 5 minutes
- **Live Countdown**: Shows time remaining until next auto-refresh
- **Smart Caching**: Data cached for 60 seconds to balance performance and freshness

### Data Freshness Indicators
- **Last Loaded Time**: Shows when data was last refreshed in the sidebar
- **File Timestamps**: Expandable "📊 Data File Info" shows modification times for all data files
- **Success Notifications**: Confirmation messages when data is successfully refreshed

### Testing Data Changes
Use the included test script to simulate data changes:
```bash
python tests/test_ui_refresh.py
```
This will modify infrastructure data and trigger refresh notifications in the UI.

## 🎯 Demo Narrative

For Temporal Solutions Architecture demonstrations, consider this flow:

1. **Start with Overview** - Show the big picture (50 devices, X critical alerts)
2. **Navigate to Alerts** - Drill into critical issues
3. **Equipment Details** - Select a specific degraded device
4. **Health Metrics** - Show 5-day trending data
5. **Lifecycle View** - Identify equipment needing maintenance
6. **Temporal Connection** - Explain how Temporal workflows:
   - Monitor these metrics in real-time
   - Trigger maintenance workflows automatically
   - Coordinate repairs across data centers
   - Send notifications to teams
   - Track maintenance history

## 🛠️ Customization

### Adding New Pages

1. Create a new component in `ui/components/`
2. Import it in `ui/app.py`
3. Add it to the navigation menu
4. Add the rendering logic in the main function

### Modifying Calculations

Edit `ui/utils/calculations.py` to adjust:
- Health score thresholds
- Lifecycle status criteria
- Contract expiry warnings
- Color schemes

### Styling

Modify the CSS in `ui/app.py` to customize:
- Colors and themes
- Layout spacing
- Component styling
- Typography

## 🐛 Troubleshooting

### Import Errors

If you encounter import errors:
```bash
# Ensure you're in the project root
cd /path/to/temporal-infra-maintenance-and-repairs-agent

# Run from root directory
streamlit run ui/app.py
```

### Port Already in Use

```bash
# Find and kill the process using port 8501
lsof -ti:8501 | xargs kill -9

# Or use a different port
streamlit run ui/app.py --server.port 8502
```

### Data Not Loading

Verify the data files exist:
```bash
ls data/*.json
```

Expected files:
- `data/infrastructure_inventory.json`
- `data/health_metrics.json`
- `data/equipment_life_expectancy.json`

## 📝 Notes

- The dashboard is read-only and does not modify the source data files
- All calculations are performed in-memory
- For production use, consider connecting to a live database or API
- The dashboard supports responsive layouts for different screen sizes

## 🤝 Support

For issues or questions about the dashboard, refer to the main project README or contact the Temporal Solutions Architecture team.

## 📄 License

This dashboard is part of the Temporal Infrastructure Maintenance and Repairs Agent project.
