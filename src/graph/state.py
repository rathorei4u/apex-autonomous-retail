from typing import Annotated, Optional, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class OrderState(TypedDict):
    """
    The upgraded 'Digital Folder' holding the full conversation history 
    and context for the ReAct multi-agent flow.
    """
    
    # 1. Conversation History (LangGraph automatically appends new messages here)
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # 2. Customer Context
    customer_id: str
    
    # 3. Journey Tracking
    stage: str # Tracks the demo journey: intake, recovery, logistics, post_purchase
    
    # 4. Order Details
    order_id: Optional[str]