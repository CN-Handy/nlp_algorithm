import random
from fastmcp import FastMCP
from typing import List, Optional
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent
from datetime import datetime
from pydantic import BaseModel, Field

mcp = FastMCP(name="Dice Roller")

@mcp.tool
def roll_dice(n_dice: int) -> List[int]:
    """Roll `n_dice` 6-sided dice and return the results."""
    return [random.randint(10, 60) for _ in range(n_dice)]

@mcp.tool
def get_news() -> ToolResult:
    """Get latest news."""
    return ToolResult(
        content=[TextContent(type="text", text="Human-readable summary")],
        structured_content={"data": "value", "count": 42}
    )

class WeatherData(BaseModel):
    """Structured weather data response"""

    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(description="Humidity percentage (0-100)")
    condition: str = Field(description="Weather condition (sunny, cloudy, rainy, etc.)")
    wind_speed: float = Field(description="Wind speed in km/h")
    location: str = Field(description="Location name")
    timestamp: datetime = Field(default_factory=datetime.now, description="Observation time")


@mcp.tool()
def get_weather(city: str) -> WeatherData:
    """Get current weather for a city 城市名字 with full structured data"""
    # In a real implementation, this would fetch from a weather API
    return WeatherData(temperature=22.5, humidity=65.0, condition="partly cloudy", wind_speed=12.3, location=city)

if __name__ == "__main__":
    mcp.run(transport="sse", port=8900)