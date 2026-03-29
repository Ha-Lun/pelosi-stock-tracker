import logging
import sys
from src.pipeline.pipeline import run_mcp_pipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Pelosi Tracker Update...")

    try:
        results = run_mcp_pipeline(days_back=365)

        logger.info(f"Update complete! Added {results['new_trades']} new trades and updated {results['new_prices']} prices")
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()