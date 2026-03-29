import logging
import json
from typing import List, Dict, Any, Tuple, Optional
from .client import MCPClient

logger = logging.getLogger(__name__)

def parse_price(price_str: Optional[str]) -> Optional[float]:
    if not price_str:
        return None
    try:
        clean_str = price_str.replace('$', '').replace(',', '').strip()
        return float(clean_str)
    except ValueError:
        logger.warning(f"Could not parse price: {price_str}")
        return None

def parse_amount_range(amount_str: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """Parse '$1,001 - $15,000' or '1M–5M' into (1001, 15000)"""
    if not amount_str:
        return None, None
    
    # 1. Clean up the string (remove $, commas, and handle different dashes)
    # Note: the second dash below is a special "en dash" (–) often used in financial data
    cleaned = amount_str.replace('$', '').replace(',', '').replace('–', '-').strip()

    def convert_suffix(val_str: str) -> Optional[int]:
        """Helper to handle K and M suffixes."""
        val_str = val_str.strip().upper()
        if not val_str:
            return None
        
        multiplier = 1
        if val_str.endswith('K'):
            multiplier = 1_000
            val_str = val_str[:-1]
        elif val_str.endswith('M'):
            multiplier = 1_000_000
            val_str = val_str[:-1]
            
        try:
            # Handle possible floats like 1.5M
            return int(float(val_str) * multiplier)
        except ValueError:
            return None

    try:
        # Handle ranges like "1,001 - 15,000" or "1M-5M"
        if '-' in cleaned:
            parts = cleaned.split('-')
            low = convert_suffix(parts[0])
            high = convert_suffix(parts[1])
            return low, high
            
        # Handle ">" prefix like ">1,000,000"
        if cleaned.startswith('>'):
            return convert_suffix(cleaned[1:]), None
            
        # Handle "<" prefix like "< 1K"
        if cleaned.startswith('<'):
            return 0, convert_suffix(cleaned[1:])
            
        # Handle single values
        val = convert_suffix(cleaned)
        return val, val
        
    except Exception as e:
        logger.warning(f"Could not parse amount range '{amount_str}': {e}")
        return None, None

class CapitolTradesWrapper:
    def __init__(self, client: MCPClient):
        self.client = client

    def get_pelosi_trades(self, days_back: int = 30) -> List[Dict[str, Any]]:
        if not self.client.is_running():
            logger.info("Starting and initializing MCP client...")
            self.client.start()
            self.client.initialize()
        
        logger.info(f"Fetching Pelosi trades for the last {days_back} days...")
        arguments = {
            "politician": "Nancy Pelosi",
            "days": days_back
        }
        
        response = self.client.call_tool("get_politician_trades", arguments)

        try:
            # The MCP protocol wraps text responses in a 'content' array
            text_content = response['content'][0]['text']
            parsed_data = json.loads(text_content)
            raw_trades = parsed_data.get('trades', [])
            
        except (KeyError, IndexError, json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Unexpected response format from MCP server: {response}. Error: {e}")
            return []
        
        formatted_trades = []
        for raw_trade in raw_trades:
            try:
                formatted_trade = self._transform_trade(raw_trade)
                formatted_trades.append(formatted_trade)
            except Exception as e:
                logger.error(f"Failed to transform trade {raw_trade.get('index')}: {e}")
            
        return formatted_trades
    
    def _transform_trade(self, raw_trade: Dict[str, Any]) -> Dict[str, Any]:
        issuer = raw_trade.get("issuer", {})
        transaction = raw_trade.get("transaction", {})
        dates = raw_trade.get("dates", {})

        amount_min, amount_max = parse_amount_range(transaction.get("size"))
        price = parse_price(transaction.get("price"))

        return {
            "ticker": issuer.get("ticker"),
            "issuer_name": issuer.get("name"),
            "transaction_type": transaction.get("type"),
            "transaction_date": dates.get("trade"),
            "disclosure_date": dates.get("disclosure"),
            "amount_range": transaction.get("size"),
            "amount_min": amount_min,
            "amount_max": amount_max,
            "price_at_trade": price
        }
