from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ToolNode:
    """Node that executes tools based on agent decisions"""
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given input
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Parameters for the tool
            
        Returns:
            Tool execution result
        """
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            logger.error(f"Tool not found: {tool_name}")
            return {
                "status": "error",
                "message": f"Tool '{tool_name}' not found. Available tools: {', '.join(self.tool_registry.tools.keys())}"
            }
        
        logger.info(f"Executing tool: {tool_name} with input: {tool_input}")
        try:
            # Execute the tool
            result = tool.run(**tool_input)
            
            # Format result for consistent output
            return {
                "status": "success",
                "tool": tool_name,
                "input": tool_input,
                "output": result
            }
        except Exception as e:
            logger.exception(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "status": "error",
                "tool": tool_name,
                "message": f"Error executing tool: {str(e)}"
            }