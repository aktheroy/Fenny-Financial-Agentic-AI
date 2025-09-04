import requests
import os
from dotenv import load_dotenv
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class CurrencyExchangeTool:
    """Tool for currency exchange rates using exchangerate-api.com"""
    
    def __init__(self):
        self.name = "currency_exchange"
        self.description = "Get current currency exchange rates or convert between currencies"
        self.parameters = {
            "base": {
                "type": "string",
                "description": "Base currency code (e.g., USD, EUR)",
                "required": False
            },
            "target": {
                "type": "string",
                "description": "Target currency code (e.g., EUR, JPY)",
                "required": False
            },
            "amount": {
                "type": "number",
                "description": "Amount to convert (default: 1)",
                "required": False
            }
        }
        
        # Get API key from environment
        self.api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        if not self.api_key:
            logger.warning("EXCHANGE_RATE_API_KEY not found in environment")
        
        self.base_url = "https://v6.exchangerate-api.com/v6"
    
    def run(self, base: str = "USD", target: str = None, amount: float = 1.0) -> Dict[str, Any]:
        """
        Get exchange rates or convert currency
        
        Args:
            base: Base currency code (default: USD)
            target: Target currency code (if not provided, returns all rates)
            amount: Amount to convert (default: 1)
            
        Returns:
            Dictionary with exchange rate information
        """
        # Validate API key
        if not self.api_key:
            logger.error("EXCHANGE_RATE_API_KEY not configured")
            return {
                "status": "error",
                "message": "Currency API key not configured. Please set EXCHANGE_RATE_API_KEY environment variable."
            }
        
        try:
            base = base.upper().strip()
            amount = float(amount)
            
            if not target:
                # Get latest rates for base currency
                endpoint = f"/{self.api_key}/latest/{base}"
                url = f"{self.base_url}{endpoint}"
                logger.debug(f"Making API request to: {url}")
                
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Check if API call was successful
                if data.get("result") != "success":
                    error_msg = data.get("error-type", "Unknown API error")
                    logger.error(f"API error response: {error_msg}")
                    return {
                        "status": "error",
                        "message": f"API error: {error_msg}"
                    }
                
                # Format all rates
                rates = {k: round(v, 4) for k, v in data["conversion_rates"].items()}
                return {
                    "status": "success",
                    "output": {
                        "base": data["base_code"],  # CORRECTED: Using base_code from API
                        "rates": rates,
                        "timestamp": data.get("time_last_update_utc", "N/A")
                    }
                }
            
            # Convert specific amount
            target = target.upper().strip()
            endpoint = f"/{self.api_key}/pair/{base}/{target}/{amount}"
            url = f"{self.base_url}{endpoint}"
            logger.debug(f"Making API request to: {url}")
            
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Check if API call was successful
            if data.get("result") != "success":
                error_msg = data.get("error-type", "Unknown API error")
                logger.error(f"API error response: {error_msg}")
                return {
                    "status": "error",
                    "message": f"API error: {error_msg}"
                }
            
            # CORRECTED: Using proper field names from API response
            return {
                "status": "success",
                "output": {
                    "base": data["base_code"],  # CORRECTED
                    "target": data["target_code"],  # CORRECTED
                    "amount": amount,
                    "converted_amount": round(data["conversion_result"], 4),
                    "rate": round(data["conversion_rate"], 4),
                    "timestamp": data.get("time_last_update_utc", "N/A")
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in currency exchange: {str(e)}")
            return {
                "status": "error",
                "message": "Network error connecting to currency service. Please check your internet connection."
            }
        except Exception as e:
            logger.exception(f"Unexpected error in currency exchange: {str(e)}")
            return {
                "status": "error",
                "message": "Unexpected error processing currency request."
            }