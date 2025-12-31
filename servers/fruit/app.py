from fastmcp import FastMCP

def get_fruit_info(fruit_name):
    """
    Get nutritional information for a given fruit.
    """
    import requests

    # Define the API endpoint
    api_url = f"https://www.fruityvice.com/api/fruit/{fruit_name}"

    try:
        # Make the API request
        response = requests.get(api_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            return {
                "name": data.get("name", "Unknown"),
                "family": data.get("family", "Unknown"),
                "genus": data.get("genus", "Unknown"),
                "order": data.get("order", "Unknown"),
                "nutritions": data.get("nutritions", {}),
                "id": data.get("id", "Unknown")
            }
        elif response.status_code == 404:
            return {"error": f"Fruit '{fruit_name}' not found"}
        else:
            return {"error": f"Failed to retrieve data from API. Status code: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}

# Initialize MCP server
mcp = FastMCP("fruityvice-mcp")

@mcp.tool()
async def get_fruit_nutrition(fruit_name: str) -> dict:
    """
    Get nutritional information and details for a given fruit name.

    Args:
        fruit_name: The name of the fruit to get information about (e.g., "apple", "banana", "orange")

    Returns:
        Dictionary containing fruit information including name, family, genus, order, and nutritional data
    """
    # Call the function from app.py
    result = get_fruit_info(fruit_name)
    return result

if __name__ == "__main__":
    mcp.run(transport="stdio")