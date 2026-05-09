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
```

---

## Scenario 1: Product Discovery with Recommendation Engine
The agent searches for products and enriches the response with loyalty data, customer profiles, and market trends.

```mermaid
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
```

---

## Scenario 2: Configurable Product with Embedded Experience
The user selects a product, and the agent retrieves deep configuration details to render the embedded UI experience.

```mermaid
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
```

---

## Scenario 3: Checkout Flow with AXP-Enriched Products
The user proceeds to checkout. The system transitions from AXP (Discovery) to UCP (Universal Checkout Protocol) to stage the order.

```mermaid
sequenceDiagram
    participant User
    participant Agent as Apex Concierge
    participant UCP as UCP Protocol
    participant Backend as Merchant Backend

    User->>Agent: "Looks perfect. Let's checkout."
    Agent->>UCP: ucp.initSession{items[], user_id}
    UCP->>Backend: POST /checkout/session
    Backend-->>UCP: Session ID & Default Address
    
    UCP->>Backend: GET /shipping/estimates
    Backend-->>UCP: Shipping Tiers (Priority Overnight)
    
    UCP-->>Agent: Checkout Payload (Subtotal, Tax, Address)
    Agent-->>User: Renders Review Order Screen
```

---

## Scenario 4: Inventory Issues & Governance Override
The agent attempts to stage an order, discovers an inventory exception, and autonomously negotiates a loyalty-based upgrade.

```mermaid
sequenceDiagram
    participant User
    participant Agent as Apex Concierge
    participant AXP as AXP Protocol
    participant Backend as Merchant Backend

    User->>Agent: "Looks perfect. Let's checkout."
    Agent->>AXP: axp.checkInventory{product_id: "ultra-16"}
    AXP->>Backend: GET /inventory/ultra-16
    Backend-->>AXP: Exception: Out of Stock (0 units)
    
    rect rgb(255, 240, 245)
        Note right of AXP: Governance & Loyalty Override
        AXP->>Backend: axp.evaluateResolution{user_id, issue: "OOS"}
        Backend-->>AXP: Eligible for Pro Upgrade (-200 Pts)
    end
    
    AXP-->>Agent: Inventory Exception + Resolution Payload
    Agent-->>User: Renders Exception Card & Asks for Authorization
    User->>Agent: "Yes, I authorize the upgrade."
```

---

## Scenario 5: The Logistics Handoff & Address Rerouting
Post-sales flow where the user tracks the order and triggers a mid-flight address update, sinking data back to Snowflake.

```mermaid
sequenceDiagram
    participant User
    participant Agent as Apex Concierge
    participant UCP as UCP Protocol
    participant Backend as Snowflake Data Cloud

    User->>Agent: "Can you change the delivery address to my home?"
    Agent->>UCP: ucp.updateFulfillment{order_id, new_address: "Home"}
    UCP->>Backend: POST /logistics/reroute (DHL API)
    Backend-->>UCP: Success (Intercepted)
    
    rect rgb(240, 255, 240)
        Note right of UCP: Snowflake Profile Update
        UCP->>Backend: PUT /customer_360/preferences
        Backend-->>UCP: 200 OK (Profile Updated)
    end
    
    UCP-->>Agent: Reroute Confirmation Payload
    Agent
