from fastmcp import FastMCP

# fastmcp 包含 mcp client 和 mcp server
mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run()

# python3 01_fastmcp环境.py