import logging
from src.dashboard import create_dashboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info(f"Starting Nancy Pelosi Trade Tracker Dashboard...")

    app = create_dashboard()
    print("\n"+"="*50)
    print("DASHBOARD STARTING")
    print("Open your browser and go to: http://127.0.0.1:8050")
    print("="*50 + "\n")
    app.run(debug=True, port=8050)

if __name__ == "__main__":
    main()