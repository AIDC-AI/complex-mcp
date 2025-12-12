from fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("TimeServer")

@mcp.tool
async def now():
    cur = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(cur)

    return cur
