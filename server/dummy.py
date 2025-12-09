from fastmcp import FastMCP

mcp = FastMCP("DummyServer")

@mcp.tool
def add(a: float, b: float) -> float:
    """Adds two numbers together."""
    
    return a + b
