from .Stocks_tool import StocksTool
from .Currency_tool import CurrencyExchangeTool
from typing import Dict, Any, List


class ToolRegistry:
    """Registry for all available tools"""

    def __init__(self):
        self.tools = {}
        self._register_tools()

    def _register_tools(self):
        """Register all available tools"""
        try:
            self.tools["stock_price"] = StocksTool()
        except Exception as e:
            print(f"Warning: Could not load StocksTool: {str(e)}")

        try:
            self.tools["currency_exchange"] = CurrencyExchangeTool()
        except Exception as e:
            print(f"Warning: Could not load CurrencyExchangeTool: {str(e)}")

    def get_tool(self, tool_name: str):
        """Get a tool by name"""
        return self.tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools with their parameters"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in self.tools.values()
        ]

    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool exists"""
        return tool_name in self.tools
