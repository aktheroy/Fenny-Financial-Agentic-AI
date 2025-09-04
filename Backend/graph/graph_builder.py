from .nodes import ToolNode
from typing import Dict, Any

class GraphBuilder:
    """Builder for the agent execution graph"""
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        self.nodes = {}
        self.edges = []
    
    def add_tool_node(self, name: str = "tool_node"):
        """Add a tool execution node to the graph"""
        self.nodes[name] = ToolNode(self.tool_registry)
        return self
    
    def build(self):
        """Build and return the execution graph"""
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }