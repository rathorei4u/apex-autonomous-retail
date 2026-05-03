# 🛍️ Apex Autonomous Retail: Multi-Agent Reference Architecture

This repository presents a conceptual guide and practical implementation for architecting robust multi-agent systems in Enterprise Retail. The focus is on the orchestration, governance, and scaling of specialized AI agents interacting with enterprise Lakehouses (Snowflake) via the Model Context Protocol (MCP).

These recommendations are grounded in composable, headless engineering principles, providing a blueprint for transitioning from static chatbots to true **ReAct (Reasoning + Acting) Agentic Workflows**.

---

## 📑 Table of Contents
1. [Introduction](#introduction)
2. [Building Blocks](#building-blocks)
3. [Design Options](#design-options)
4. [Agents Registry](#agents-registry)
5. [Memory](#memory)
6. [Agents Communication](#agents-communication)
7. [Observability](#observability)
8. [Evaluation](#evaluation)
9. [Security](#security)
10. [Governance](#governance)
11. [Reference Architecture](#reference-architecture)

---

## Introduction
Generative AI is advancing rapidly. This reference architecture shifts the paradigm from "LLMs as text generators" to "LLMs as system orchestrators." The Apex Autonomous Retail solution demonstrates how AI can autonomously navigate complex business logic—including Out-of-Stock (OOS) recovery, proactive logistics rerouting, and ERP write-backs—without human intervention, while maintaining a premium conversational interface.

## Building Blocks
- **Reasoning Engine:** Anthropic Claude 3.5 Sonnet (Optimized for complex tool calling).
- **Orchestration Layer:** LangGraph (Stateful, deterministic routing).
- **Data Bridge:** Model Context Protocol / MCP Tools (Standardized enterprise integration).
- **Enterprise Lakehouse:** Snowflake (Live inventory, customer profiles, billing).
- **Experience Layer:** Streamlit (Headless, composable UI).

## Design Options
When designing multi-agent systems, architects must choose between Decentralized Swarms (agents operating independently) and Centralized Orchestrators. 
**Our Approach:** We utilize a **Centralized ReAct Orchestrator**. LangGraph acts as the state machine (`stage_manager_node`), dictating the bounds of the conversation, while Claude is given autonomy *within* those bounds to select MCP tools.

## Agents Registry
Instead of disparate scripts, the system relies on dynamic personas executed by the primary reasoning engine:
- **The Concierge:** Handles discovery, configuration, and upsells (ApexCare+).
- **The Recovery Swarm:** Authorized to perform margin-aware resolutions (e.g., deducting 200 Loyalty Points for an Ultra upgrade).
- **The Logistics Sentinel:** Monitors external carrier telemetry and executes reroutes (e.g., bypassing a Memphis storm via DHL).
- **The Policy Enforcer:** Validates warehouse picking status before executing instant ERP cancellations.

## Memory
The architecture utilizes a Dual-Memory design to prevent "Agent Amnesia":
1. **Short-Term (Conversational Context):** Managed by LangGraph's `OrderState`, tracking the `messages` array and dynamic intent variables (like `active_sku`) throughout a single session.
2. **Long-Term (Persistent Context):** Managed via the `manage_customer_memory` MCP tool, allowing agents to store facts (e.g., "Traveling on Friday") back to the Enterprise Database for future interactions.

## Agents Communication
Communication is handled via a **Shared State Schema** (The "Digital Folder"). Rather than passing raw strings between agents, the system passes a typed dictionary containing the conversation history, the active SKU, and the customer ID. This allows tools (like `process_payment` and `create_order`) to execute transactionally based on shared context.

## Observability
Agentic workflows are naturally opaque. This architecture implements a "Glass-Box" observability pattern. 
By utilizing Streamlit's sidebar, all Agent-to-Agent (A2A) communications and MCP Tool executions are surfaced to the UI in real-time, allowing engineers and stakeholders to verify that the AI is executing the `check_inventory` or `update_delivery_address` tools securely.

## Evaluation
Testing multi-agent systems requires simulating full business lifecycles rather than single prompts. This repository evaluates success across a 4-turn journey:
1. Intent Recognition & Config.
2. Transaction Execution & Conflict Recovery.
3. Proactive Telemetry Monitoring.
4. Transactional Write-Backs (Address Updates/Invoicing).

## Security
- **API Boundary:** The LLM does not write SQL. It communicates exclusively via bounded Python functions (MCP tools).
- **Authentication:** Model access is secured via API keys (or corporate LLM Gateways) managed securely in `.env` files.
- **Data Privacy:** PII and addresses are fetched dynamically during the session and are never hardcoded into the system prompts.

## Governance
To prevent AI hallucination during critical transactions (like taking payments), the `stage_manager_node` enforces strict transitions. The AI cannot access the "Post-Purchase" tools (like `update_delivery_address`) until the Stage Manager confirms the "Intake" stage is complete.

## Reference Architecture

```mermaid
graph TD
    UI[Experience Layer: Streamlit] -->|User Input| LG[Orchestrator: LangGraph]
    
    subgraph Multi-Agent Brain
        LG --> SM[Supervisor: Stage Manager]
        
        subgraph Specialized CrewAI Swarms
            SM -->|Intake| CA[The Concierge]
            SM -->|Out of Stock| RS[The Recovery Swarm]
            SM -->|Tracking| LS[The Logistics Sentinel]
            SM -->|Post-Purchase| PE[The Policy Enforcer]
        end
        
        CA & RS & LS & PE <-->|ReAct Loop| CL[Claude 3.5 Sonnet]
    end
    
    subgraph Enterprise Data Bridge
        CA --> T1(Customer Profile)
        RS --> T2(Live Inventory)
        LS --> T3(Logistics API)
        PE --> T4(ERP / Payment)
    end
    
    T1 & T2 & T3 & T4 <-->|MCP Protocol| SNOW[(Snowflake Lakehouse)]
