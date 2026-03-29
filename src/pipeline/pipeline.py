import logging
from ..mcp import MCPClient, CapitolTradesWrapper
from ..database import insert_trade, init_database
from ..prices import fetch_current_prices

logger = logging.getLogger(__name__)

def run_mcp_pipeline(days_back: int = 30):
    init_database()

    client = MCPClient("npx -y @anguslin/mcp-capitol-trades")
    wrapper = CapitolTradesWrapper(client)

    try:
        trades = wrapper.get_pelosi_trades(days_back=days_back)
        logger.info(f"Pipeline fetched {len(trades)} trades from MCP")

        count=0
        for trade in trades:
            if insert_trade(trade):
                count+=1
        logger.info(f"Pipeline successfully inserted {count} new trades into the database")
        
        price_count = fetch_current_prices()
        return{
            "new_trades":count,
            "new_prices":price_count
        }
    
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise
    
    finally:
        if client.is_running():
            client.stop()

