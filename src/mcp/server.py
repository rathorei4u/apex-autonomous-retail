from mcp.server.fastmcp import FastMCP

# Initialize the 'ApexRetailEngine' MCP Server
mcp = FastMCP("ApexRetailEngine")

@mcp.tool()
async def check_inventory(sku: str) -> dict:
    """Scene 2: Checks stock for high-end electronics."""
    # Simulates a query to Snowflake/Databricks
    inventory = {
        "APEX-BOOK-PRO": {"name": "ApexBook Pro 16", "stock": 0, "price": 2499},
        "APEX-TAB-10": {"name": "ApexTab Ultra", "stock": 12, "price": 899}
    }
    product = inventory.get(sku.upper())
    return product if product else {"stock": 0, "error": "SKU not found"}

@mcp.tool()
async def get_loyalty_data(customer_id: str) -> dict:
    """Retrieves customer status for resolution credits."""
    customers = {
        "C-4455": {"name": "V. Rathore", "tier": "Platinum", "credits": 250}
    }
    return customers.get(customer_id, {"tier": "Standard", "credits": 0})

@mcp.tool()
async def get_carrier_telemetry(tracking_id: str) -> dict:
    """Scene 3: Queries carrier for weather and route alerts."""
    # Simulated fault injection (The Weather Delay)
    return {
        "status": "Delayed", 
        "alert": "Severe Weather Alert: Memphis Hub closed.",
        "carrier": "FedEx"
    }

@mcp.tool()
async def execute_cancellation(order_id: str) -> dict:
    """Scene 4: Performs the actual cancellation in the ERP."""
    # This simulates a 'write' action back to your Enterprise Data Platform
    return {
        "status": "Cancelled",
        "refund_status": "Initiated",
        "confirmation": f"ERP-REF-XYZ-{order_id}"
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
