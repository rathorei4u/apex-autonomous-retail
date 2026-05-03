import streamlit as st
import pandas as pd
import snowflake.connector
import os
import time
from dotenv import load_dotenv
from src.graph.orchestrator import orchestrator
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# 1. LOAD CONFIG
load_dotenv()

# 2. SNOWFLAKE DATA FUNCTIONS (For the Enterprise Tabs)
@st.cache_data(ttl=60)
def get_snowflake_data(query):
    try:
        account = os.getenv('SNOWFLAKE_ACCOUNT')
        if not account: return pd.DataFrame()

        ctx = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=account,
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
        cursor = ctx.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=columns)
        
        cursor.close()
        ctx.close()
        return df
    except Exception as e:
        return pd.DataFrame()

# 3. PAGE UI CONFIG & SESSION STATE
st.set_page_config(page_title="Apex Autonomous Retail", layout="wide", page_icon="🏙️")

# SIMULATE USER LOGIN & CONVERSATIONAL STATE
if "current_user" not in st.session_state: st.session_state.current_user = "C-1001"
if "demo_stage" not in st.session_state: st.session_state.demo_stage = "intake"
if "messages" not in st.session_state: st.session_state.messages = []

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .agent-log { font-family: 'Courier New', monospace; color: #1565c0; font-size: 0.85rem; padding: 8px; border-bottom: 1px solid #eee; background-color: #e3f2fd; margin-bottom: 5px; border-radius: 5px;}
    .agent-success { font-family: 'Courier New', monospace; color: #2e7d32; font-size: 0.85rem; padding: 8px; border-bottom: 1px solid #eee; background-color: #e8f5e9; margin-bottom: 5px; border-radius: 5px;}
    </style>
    """, unsafe_allow_html=True)

# 4. SIDEBAR: LIVE CUSTOMER CONTEXT & TOOL LOGS
with st.sidebar:
    cust_df = get_snowflake_data(f"SELECT * FROM CUSTOMERS WHERE CUSTOMER_ID = '{st.session_state.current_user}'")
    
    if not cust_df.empty:
        st.image(cust_df['AVATAR_URL'].values[0], width=100)
        st.title(cust_df['FULL_NAME'].values[0])
        st.markdown(f"⭐ **{cust_df['TIER'].values[0]} Member**")
    else:
        st.warning("Customer profile not found.")
    
    st.markdown("---")
    st.subheader("⚙️ Live MCP Executions")
    st.caption("Watch the agents trigger enterprise tools automatically.")
    log_area = st.empty()

# 5. MAIN DASHBOARD LAYOUT
col_chat, col_viz = st.columns([1.2, 1])

with col_chat:
    st.header("💬 AI Commerce Assistant")

    # Render previous messages (ignoring System and Tool messages for the clean UI)
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"): st.markdown(msg.content)
        elif isinstance(msg, AIMessage) and msg.content:
            with st.chat_message("assistant"): st.markdown(msg.content)

    if prompt := st.chat_input("Start by asking for a laptop..."):
        # Append User Message to history
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            thinking_box = st.empty()
            thinking_box.info("🔍 AI is reasoning and checking enterprise tools...")
            
            # 🚀 RUN THE MASTER ORCHESTRATOR 🚀
            res = orchestrator.invoke({
                "messages": st.session_state.messages, 
                "customer_id": st.session_state.current_user,
                "stage": st.session_state.demo_stage
            })
            
            # Update stage tracking and message history
            st.session_state.demo_stage = res["stage"]
            st.session_state.messages = res["messages"]
            
            thinking_box.empty()

            # DISPLAY FINAL ASSISTANT RESPONSE
            final_response = res["messages"][-1].content
            if final_response:
                st.markdown(final_response)

            # EXTRACT TOOL CALLS FOR THE SIDEBAR LOGS
            logs_html = ""
            for m in res["messages"]:
                if hasattr(m, 'tool_calls') and m.tool_calls:
                    for tc in m.tool_calls:
                        logs_html += f"<div class='agent-log'>🛠️ <b>Calling Tool:</b> {tc['name']}</div>"
                elif isinstance(m, ToolMessage):
                    logs_html += f"<div class='agent-success'>✅ <b>Success:</b> Data returned to AI</div>"
            
            log_area.markdown(logs_html, unsafe_allow_html=True)

with col_viz:
    st.header("📊 Enterprise State")
    tab_cat, tab_inv, tab_ops = st.tabs(["📦 Catalog", "📉 Inventory", "🧾 Orders"])

    with tab_cat:
        st.info("Product Catalog synced with Snowflake Data Lakehouse.")
        prod_df = get_snowflake_data("SELECT SKU, PRODUCT_NAME, BASE_PRICE FROM PRODUCTS LIMIT 3")
        if not prod_df.empty: st.dataframe(prod_df, use_container_width=True)

    with tab_inv:
        st.info("Live Warehouse Telemetry.")
        inv_df = get_snowflake_data("SELECT SKU, WAREHOUSE_LOCATION, STOCK_LEVEL FROM INVENTORY LIMIT 3")
        if not inv_df.empty: st.dataframe(inv_df, use_container_width=True)

    with tab_ops:
        st.info(f"Recent Orders for {st.session_state.current_user}")
        ord_df = get_snowflake_data(f"SELECT ORDER_ID, ORDER_STATUS, PAYMENT_STATUS FROM ORDERS WHERE CUSTOMER_ID = '{st.session_state.current_user}' LIMIT 3")
        if not ord_df.empty: st.dataframe(ord_df, use_container_width=True)