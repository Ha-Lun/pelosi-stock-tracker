# 🏛️ Pelosi Trade Tracker

A Python-based automated system that tracks and visualizes stock trades by Nancy Pelosi. It uses a modern "Model Context Protocol" (MCP) server to fetch live data directly from Capitol Trades.

## 🚀 Key Features

*   **Automated Data Fetching**: Uses the `@anguslin/mcp-capitol-trades` MCP server to get the latest disclosures.
*   **Market Analysis**: Integrates with `yfinance` to fetch real-time closing prices for all traded stocks.
*   **Robust Data Storage**: Stores history in a local SQLite database using the Peewee ORM.
*   **Interactive Dashboard**: A web-based interface built with Dash (Plotly) and Bootstrap for visualizing trade trends and counts.

## 🛠️ Architecture

The project is divided into several clean modules:
*   **`src/mcp`**: Handles low-level JSON-RPC communication with the MCP subprocess and high-level data transformation.
*   **`src/database`**: Manages the SQLite schema and data persistence.
*   **`src/prices`**: Fetches current market data from Yahoo Finance.
*   **`src/pipeline`**: The "brain" that orchestrates the full data collection flow.
*   **`src/dashboard`**: The web interface for data visualization.

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd pelosi-tracker
   ```

2. **Set up the virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install the MCP server (requires Node.js)**:
   ```bash
   npm install -g @anguslin/mcp-capitol-trades
   ```

## 📈 Usage

### 1. Update the Data
To fetch the latest trades and prices, run the main pipeline:
```bash
python main.py
```

### 2. View the Dashboard
To launch the web interface, run:
```bash
python run_dashboard.py
```
Then visit `http://127.0.0.1:8050` in your browser.

## 🔒 License
MIT
