from fastmcp import FastMCP

mcp = FastMCP("MathServer")

@mcp.tool
async def add(a: float, b: float) -> float:
    """Adds a and b together."""
    return a + b

@mcp.tool
async def sub(a: float, b: float) -> float:
    """Subtracts b from a."""
    return a - b

@mcp.tool
async def mul(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return a * b

@mcp.tool
async def div(a: float, b: float) -> float:
    """Divides a by b."""
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

@mcp.tool
async def pow(a: float, b: float) -> float:
    """Raises a to the power of b."""
    return a ** b

