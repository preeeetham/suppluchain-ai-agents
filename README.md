# Autonomous Supply Chain & Logistics Optimization System

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

## Project Overview

This project implements a decentralized supply chain management platform using Fetch.ai's uAgents framework and SingularityNET's MeTTa Knowledge Graphs. The system consists of four autonomous AI agents that work together to optimize supply chain operations:

- **Inventory Management Agent**: Monitors stock levels and triggers reorders
- **Demand Forecasting Agent**: Predicts future demand using historical patterns
- **Route Optimization Agent**: Optimizes delivery routes and logistics
- **Supplier Coordination Agent**: Manages supplier relationships and orders

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Inventory     │    │   Demand        │    │   Route         │
│   Management    │◄──►│   Forecasting   │◄──►│   Optimization  │
│   Agent         │    │   Agent         │    │   Agent         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Supplier      │    │   MeTTa         │    │   Agentverse    │
│   Coordination  │    │   Knowledge     │    │   Registry      │
│   Agent         │    │   Graphs        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Agent Information

### Agent Names and Addresses
- **Inventory Management Agent**: `inventory_agent_0x1234`
- **Demand Forecasting Agent**: `demand_agent_0x5678`
- **Route Optimization Agent**: `route_agent_0x9abc`
- **Supplier Coordination Agent**: `supplier_agent_0xdef0`

## Technology Stack

- **Framework**: Fetch.ai uAgents framework
- **Knowledge Management**: SingularityNET MeTTa Knowledge Graphs
- **Communication**: Chat Protocol for ASI:One compatibility
- **Deployment**: Agentverse registry
- **Database**: JSON/SQLite for agent state persistence

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd supply-chain-agents
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MeTTa knowledge graphs:
```bash
# Install MeTTa
pip install hyperon
```

## Running the Agents

### Start Individual Agents

```bash
# Terminal 1 - Inventory Management Agent
python agents/inventory_agent.py

# Terminal 2 - Demand Forecasting Agent
python agents/demand_forecasting_agent.py

# Terminal 3 - Route Optimization Agent
python agents/route_optimization_agent.py

# Terminal 4 - Supplier Coordination Agent
python agents/supplier_coordination_agent.py
```

### Run Complete System Simulation

```bash
python run_simulation.py
```

## MeTTa Knowledge Graph Schema

### Inventory Knowledge Graph
- `(warehouse-id, product-id, quantity, timestamp)`
- `(product-id, reorder-point, buffer-stock)`
- `(warehouse-id, capacity, location)`

### Demand Patterns Knowledge Graph
- `(product-id, seasonal-factor, trend, historical-sales)`
- `(product-id, demand-pattern, confidence-score)`
- `(time-period, market-trend, external-factors)`

### Supplier Data Knowledge Graph
- `(supplier-id, lead-time, reliability-score, cost-per-unit)`
- `(supplier-id, product-id, availability, quality-rating)`
- `(supplier-id, performance-metrics, delivery-history)`

### Route Efficiency Knowledge Graph
- `(route-id, distance, delivery-time, cost, efficiency-score)`
- `(warehouse-id, destination, optimal-route, traffic-patterns)`
- `(vehicle-id, capacity, fuel-efficiency, maintenance-schedule)`

## Example Queries

### Inventory Queries
```metta
! (find-products-below-reorder-point)
! (get-warehouse-inventory "warehouse-001")
! (calculate-reorder-quantity "product-123")
```

### Demand Forecasting Queries
```metta
! (predict-demand "product-123" "next-30-days")
! (get-seasonal-factor "product-123" "Q4")
! (analyze-trend "product-123" "last-6-months")
```

### Route Optimization Queries
```metta
! (find-optimal-route "warehouse-001" "destination-list")
! (calculate-delivery-time "route-123")
! (optimize-vehicle-assignment "orders-list")
```

## Agent Communication Flow

1. **Inventory Agent** detects low stock
2. **Inventory Agent** queries **Demand Agent** for demand forecast
3. **Demand Agent** queries MeTTa for historical patterns
4. **Inventory Agent** triggers **Supplier Agent** for reorder
5. **Supplier Agent** selects optimal supplier from MeTTa data
6. **Route Agent** optimizes delivery route for new inventory
7. All agents update MeTTa with new data

## Integration with Agentverse

All agents are registered on Agentverse with the following steps:

1. **Agent Registration**: Each agent includes `publish_manifest=True`
2. **Chat Protocol**: All agents implement Chat Protocol for ASI:One
3. **Discovery**: Agents are discoverable through ASI:One interface
4. **Communication**: Agents can communicate via Chat Protocol

## Testing Multi-Agent Communication

```bash
# Test inventory reorder scenario
python tests/test_integration.py --scenario inventory_reorder

# Test demand forecasting
python tests/test_integration.py --scenario demand_forecast

# Test route optimization
python tests/test_integration.py --scenario route_optimization
```

## Dependencies

- `uagents` - Fetch.ai uAgents framework
- `hyperon` - SingularityNET MeTTa Knowledge Graphs
- `pandas` - Data manipulation
- `numpy` - Numerical computations
- `requests` - HTTP requests for external APIs
- `sqlite3` - Local database (built-in)

## Demo Video Script

1. **System Overview** (30 sec): Show architecture and agent roles
2. **Live Demo** (2 min): Run scenario showing agent collaboration
3. **Real-Time Communication** (1 min): Show agent message logs
4. **Agentverse Registration** (30 sec): Show agents on ASI:One

## Judging Criteria Alignment

- **Functionality (25%)**: Multi-agent system with real communication
- **ASI Tech Usage (20%)**: Agentverse registration, Chat Protocol, MeTTa integration
- **Innovation (20%)**: Autonomous decision-making with knowledge graphs
- **Real-World Impact (20%)**: Solves actual supply chain problems
- **UX & Presentation (15%)**: Clear demo and documentation

## Success Checklist

- [x] All 4 agents implemented and communicating
- [x] MeTTa Knowledge Graphs populated with realistic data
- [x] Agents make autonomous decisions visible in logs
- [x] Agents registered on Agentverse
- [x] Chat Protocol enabled and tested
- [x] ASI:One compatibility verified
- [x] Demo video recorded (3-5 min)
- [x] README with agent addresses and integration guide
- [x] GitHub repo public with all code
- [x] No external authentication required
- [x] All dependencies in requirements.txt

## Contributing

This project was developed for the ASI Alliance Hackathon. For questions or support, please refer to the ASI Alliance documentation.

## License

MIT License - See LICENSE file for details.
