import yfinance as yf
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class StocksTool:
    """Tool for retrieving stock market data using yfinance"""
    
    def __init__(self):
        self.name = "stock_price"
        self.description = "Get current stock price and basic information for a ticker symbol"
        self.parameters = {
            "ticker": {
                "type": "string",
                "description": "Stock ticker symbol (e.g., AAPL, MSFT, TSLA)",
                "required": True
            }
        }
    
    def run(self, ticker: str) -> Dict[str, Any]:
        """
        Get current stock price and basic information
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with stock information
        """
        try:
            # Format ticker to uppercase and remove any spaces
            ticker = ticker.upper().strip()
            
            # Fetch stock data
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract relevant information
            result = {
                "ticker": ticker,
                "name": info.get('shortName', ticker),
                "current_price": info.get('currentPrice', 'N/A'),
                "currency": info.get('currency', 'USD'),
                "market_open": info.get('regularMarketOpen', 'N/A'),
                "day_range": f"{info.get('dayLow', 'N/A')} - {info.get('dayHigh', 'N/A')}",
                "volume": info.get('volume', 'N/A'),
                "market_cap": info.get('marketCap', 'N/A'),
                "pe_ratio": info.get('trailingPE', 'N/A'),
                "dividend_yield": info.get('dividendYield', 'N/A')
            }
            
            # Format numerical values
            if result["current_price"] != 'N/A':
                result["current_price"] = round(float(result["current_price"]), 2)
            if result["market_cap"] != 'N/A':
                result["market_cap"] = self._format_market_cap(result["market_cap"])
                
            logger.info(f"Retrieved stock data for {ticker}: ${result['current_price']}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {ticker}: {str(e)}")
            return {
                "error": f"Could not retrieve data for {ticker}. Please check the ticker symbol and try again.",
                "details": str(e)
            }
    
    def _format_market_cap(self, market_cap: float) -> str:
        """Format market cap value into human-readable format"""
        try:
            market_cap = float(market_cap)
            if market_cap >= 1_000_000_000_000:  # Trillion
                return f"${market_cap/1_000_000_000_000:.2f}T"
            elif market_cap >= 1_000_000_000:  # Billion
                return f"${market_cap/1_000_000_000:.2f}B"
            elif market_cap >= 1_000_000:  # Million
                return f"${market_cap/1_000_000:.2f}M"
            else:
                return f"${market_cap:.2f}"
        except:
            return str(market_cap)