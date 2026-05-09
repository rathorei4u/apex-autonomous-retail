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
