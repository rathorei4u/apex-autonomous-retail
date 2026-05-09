# AXP Flow Diagrams

This document shows how the Agentic Experience Protocol (AXP) and Universal Checkout Protocol (UCP) integrate to orchestrate a complete enterprise Agentic Commerce lifecycle.

## Overview: AXP + UCP Architecture

```mermaid
flowchart TD
    subgraph AI [AGENTIC INTERFACE]
        direction TB
        A[AI Assistant / Shopping Agent]
    end

    subgraph PL [PROTOCOL LAYER]
        direction LR
        subgraph AXP [AXP]
            direction TB
            axp_list["• Product Data<br>• Quality Signals<br>• Embedded Experiences<br>• Trust Information"]
        end
        subgraph UCP [UCP]
            direction TB
            ucp_list["• Checkout Sessions<br>• Payment Processing<br>• Order Management<br>• Identity Linking"]
        end
        AXP <--> UCP
    end

    subgraph MB [MERCHANT BACKEND]
        direction LR
        cat[Product<br>Catalog]
        rev[Review<br>System]
        exp[Experience<br>Platform]
        com[Commerce Engine<br>& Snowflake Data Cloud]
    end

    AI --> PL
    PL --> MB
    
    classDef plain fill:#f9f9f9,stroke:#333,stroke-width:1px,color:#000;
    class AI,PL,MB,AXP,UCP plain;
    class A,axp_list,ucp_list,cat,rev,exp,com plain;



Scenario 1: Product Discovery with Recommendation Engine

sequenceDiagram
    participant User
    participant Agent as Apex Concierge
    participant AXP as AXP Protocol
    participant Backend as Merchant / Snowflake

    User->>Agent: "Find me a good laptop for engineering."
    Agent->>AXP: axp.searchProducts{query: "engineering laptop"}
    AXP->>Backend: GET /catalog/search?q=engineering
    Backend-->>AXP: Products[]
    
    rect rgb(240, 248, 255)
        Note right of AXP: Context Enrichment
        AXP->>Backend: GET /customer/profile (Loyalty, History)
        Backend-->>AXP: Profile Data (Platinum Tier)
        AXP->>Backend: GET /market/trends (Engineering workflows)
        Backend-->>AXP: Trend Data (Thermal requirements)
    end
    
    AXP-->>Agent: Products + Enriched Context
    Agent-->>User: Renders Config Matrix & Recommendation




Scenario 2: Configurable Product with Embedded Experience

sequenceDiagram
    participant User
    participant Agent as Apex Concierge
    participant AXP as AXP Protocol
    participant Backend as Merchant Backend

    User->>Agent: "Select the Apex Ultra 16"
    Agent->>AXP: axp.getProductDetails{product_id: "ultra-16"}
    AXP->>Backend: GET /products/ultra-16/specs
    Backend-->>AXP: Spec Data (10-Core, 22hr, XDR)
    
    AXP->>Backend: GET /products/ultra-16/experience_assets
    Backend-->>AXP: Hero Images & Feature Cards
    
    AXP-->>Agent: Product Payload + UI Assets
    Agent-->>User: Renders Embedded Product Details UI
