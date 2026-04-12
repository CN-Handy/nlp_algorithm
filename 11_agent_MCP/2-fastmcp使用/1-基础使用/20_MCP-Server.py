from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool
def greet2(name: str) -> str:
    return f"Hello, 机器学习!"

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)