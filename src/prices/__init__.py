import logging
import yfinance as yf
from datetime import datetime
from ..database import get_trades, insert_prices

logger = logging.getLogger(__name__)

def fetch_current_prices():
    trades = get_trades()
    tickers = {t.ticker for t in trades if t.ticker and ":" in t.ticker}
    
    clean_tickers = list({t.split(":")[0] for t in tickers})

    if not clean_tickers:
        logger.info(f"No tickers found in database to update")
        return 0
    
    logger.info(f"Fetching current prices for: {', '.join(clean_tickers)}")

    try:
        data = yf.download(clean_tickers, period="1d", group_by='ticker', progress=False)
        price_records = []
        now = datetime.now().date()

        for ticker in clean_tickers:
            try:
                if len(clean_tickers) == 1:
                    latest_price = data['Close'].iloc[-1]
                    volume = data['Volume'].iloc[-1]
                else:
                    if ticker not in data.columns.levels[0]:
                        continue
                    latest_price = data[ticker]['Close'].iloc[-1]
                    volume = data[ticker]['Volume'].iloc[-1]
                
                original_ticker = next((t for t in tickers if t.startswith(ticker)), ticker)

                price_records.append({
                    "ticker": original_ticker,
                    "date": now,
                    "open": 0,
                    "high": 0,
                    "low": 0,
                    "close": float(latest_price),
                    "volume": float(volume)
                })
            except Exception as e:
                logger.warning(f"Could not get price for {ticker}: {e}")
                
        if price_records:
            insert_prices(price_records)
            logger.info(f"Successfully updated {len(price_records)} prices")
            return len(price_records)
    except Exception as e:
        logger.error(f"Failed to fetch prices: {e}")
        return 0
    
    return 0
