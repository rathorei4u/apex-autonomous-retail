import os
from typing import Literal
from langgraph.graph import StateGraph, END, START
from .state import OrderState
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

# 1. LOAD ENVIRONMENT & INITIALIZE SECRETS
load_dotenv()

# --- 2. DEFINE ALL ENTERPRISE MCP TOOLS ---

@tool
def get_customer_profile(customer_id: str):
    """Fetches customer name, loyalty tier, and stored addresses from Snowflake."""
    return {
        "name": "V. Rathore", 
        "tier": "Platinum", 
        "discount": "10%",
        "home_address": "123 Marina Bay Blvd, Unit 45, Singapore 018956",
        "office_address": "8 Cross Street, #11-00, Singapore 048424"
    }

@tool
def process_payment(amount: float, method: str = "Apple Pay"):
    """Dummy Payment Gateway. Processes Apple Pay/Credit Cards."""
    return {"status": "SUCCESS", "transaction_id": "TXN-999888"}

@tool
def create_order(customer_id: str, total_price: float = 0.0, config: str = "Custom Configuration", apex_care: bool = False):
    """Inserts a new order into Snowflake."""
    return {"status": "SUCCESS", "order_id": "ORD-5005"}

@tool
def check_inventory(sku: str = "APEX-1001"):
    """Checks Snowflake inventory for the configured laptop."""
    return {"stock": 0, "status": "OUT_OF_STOCK"}

@tool
def update_order_with_upgrade(order_id: str, points_deducted: int = 200, freebies: str = "Apex Mouse"):
    """Updates Snowflake: upgrades model, deducts points, adds freebies."""
    return {"status": "SUCCESS", "message": f"Upgraded {order_id}. {points_deducted} points used. Added {freebies}."}

@tool
def check_logistics_telemetry(order_id: str = "ORD-5005"):
    """Queries Carrier API for weather and tracking."""
    return {"status": "DELAYED", "reason": "Storm at Memphis Hub", "action_taken": "Rerouted via DHL Express", "tracking": "DHL-EXP-12345"}

@tool
def update_delivery_address(order_id: str, full_address: str, address_type: str = "Home"):
    """Updates the delivery address in the ERP."""
    return {
        "status": "SUCCESS", 
        "message": f"Order {order_id} successfully rerouted to {address_type} address: {full_address}"
    }

@tool
def generate_and_email_invoice(order_id: str):
    """Generates PDF invoice and emails it to the customer."""
    return {"status": "SUCCESS", "email_sent_to": "v.rathore@example.com"}

# --- 3. INITIALIZE DIRECT ANTHROPIC CLAUDE ---
tools = [
    get_customer_profile, process_payment, create_order, check_inventory, 
    update_order_with_upgrade, check_logistics_telemetry, 
    update_delivery_address, generate_and_email_invoice
]

# The SDK automatically uses ANTHROPIC_API_KEY from your .env file
model = ChatAnthropic(
    model="claude-sonnet-4-6", 
    temperature=0.2
)
model_with_tools = model.bind_tools(tools)

# --- 4. THE GRAPH NODES ---

def stage_manager_node(state: OrderState):
    """Monitors the chat and transitions the Demo Stage based on user intent."""
    user_msg = state["messages"][-1].content.lower()
    stage = state.get("stage", "intake")

    if "fantastic" in user_msg or "tracking" in user_msg or "arriving" in user_msg:
        stage = "logistics"
    elif "address" in user_msg or "home" in user_msg:
        stage = "post_purchase"
    elif stage == "intake" and any(word in user_msg for word in ["confirm", "pay", "yes", "place the order"]):
        stage = "recovery" 

    return {"stage": stage}

def primary_agent_node(state: OrderState):
    """The central brain. Adapts its personality based on the Stage."""
    stage = state.get("stage", "intake")
    
    sys_prompt = f"""You are the Apex AI Commerce Assistant. You provide a premium, conversational experience. 
    Customer ID: {state['customer_id']}

    YOUR CURRENT OBJECTIVE BASED ON STAGE [{stage}]:
    - intake: Greet customer by name using get_customer_profile. Guide their laptop config (Size: 13/15, Color: White/Black/Gray, CPU: M5 8/10 core). Pitch ApexCare+. Calculate total with 10% Platinum discount. Use process_payment, then create_order.
    - recovery: The order was placed, but inventory check shows base model is OUT OF STOCK. Apologize. Offer Platinum upgrade to Ultra model. Deduct 200 points, add a FREE Apex Mouse, and keep the 10% discount. Ask if they agree. Use update_order_with_upgrade.
    - logistics: Customer asks about delivery. Use check_logistics_telemetry. Tell them about the storm, but highlight that you proactively rerouted to DHL Express. Share tracking info.
    - post_purchase: Customer wants to change delivery to their Home. Look at get_customer_profile to find their actual 'home_address'. Ask for Order ID if needed. Use update_delivery_address passing the FULL physical address. Then use generate_and_email_invoice and confirm it was sent.

    CRITICAL: Do not just list options. Speak naturally, like a high-end concierge. Always read back the actual physical address to the customer for confirmation when updating addresses.
    """
    
    messages = [SystemMessage(content=sys_prompt)] + state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

# --- 5. CONSTRUCT THE GRAPH ---
workflow = StateGraph(OrderState)

workflow.add_node("stage_manager", stage_manager_node)
workflow.add_node("agent", primary_agent_node)
workflow.add_node("tools", ToolNode(tools)) 

workflow.add_edge(START, "stage_manager")
workflow.add_edge("stage_manager", "agent")
workflow.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")

orchestrator = workflow.compile()