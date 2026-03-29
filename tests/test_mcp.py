import logging
import json
from src.mcp import MCPClient, CapitolTradesWrapper

logging.basicConfig(level=logging.INFO)

def run_test():
    client = MCPClient("npx -y @anguslin/mcp-capitol-trades")

    wrapper = CapitolTradesWrapper(client)
    
    try:
        print(f"Fetching Pelosi trades from the last 90 days...")
        trades = wrapper.get_pelosi_trades(days_back=90)
        print(f"\n Success! Found {len(trades)} trades")

        if trades:
            # Fixed json.dump to json.dumps
            print(f"\nHere is what a cleaned trade dictionary looks like (ready for database):\n {json.dumps(trades[0], indent=2)}")

    except Exception as e:
        print(f"\nError occured: {e}")
    
    finally:
        print(f"\nStopping client...")
        client.stop()

if __name__ == "__main__":
    run_test()
