"""
FastAPI Server for Supply Chain AI Agents Frontend Integration
Provides REST API endpoints to connect frontend with backend agents
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from pydantic import BaseModel

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.shared_protocols import AGENT_ADDRESSES
from utils.mock_metta_integration import get_metta_kg
from solana_blockchain_integration import get_blockchain_integration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Supply Chain AI Agents API",
    description="REST API for Supply Chain AI Agents System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend/public"), name="static")

# Global variables for real-time data
connected_clients: List[WebSocket] = []
agent_status_cache = {}
inventory_cache = {}
demand_cache = {}
route_cache = {}
supplier_cache = {}
blockchain_cache = {}

# Pydantic models for API responses
class AgentStatus(BaseModel):
    name: str
    status: str
    efficiency: float
    tasks_completed: int
    last_activity: datetime
    uptime: str

class InventoryItem(BaseModel):
    warehouse_id: str
    product_id: str
    product_name: str
    quantity: int
    reorder_point: int
    unit_price: float
    last_updated: datetime

class DemandForecast(BaseModel):
    product_id: str
    product_name: str
    forecast_period: str
    predicted_demand: int
    confidence_score: float
    seasonal_factor: float
    trend: str

class RouteOptimization(BaseModel):
    route_id: str
    warehouse_id: str
    destinations: List[str]
    total_distance: float
    estimated_time: float
    efficiency_score: float
    cost_savings: float

class SupplierInfo(BaseModel):
    supplier_id: str
    name: str
    reliability_score: float
    lead_time_days: int
    cost_per_unit: float
    quality_rating: float
    active_orders: int

class BlockchainTransaction(BaseModel):
    transaction_id: str
    type: str
    amount: float
    timestamp: datetime
    status: str
    agent_id: str

class SystemMetrics(BaseModel):
    active_agents: int
    total_inventory_value: float
    pending_orders: int
    active_routes: int
    blockchain_transactions: int
    system_health: str

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Initialize data from agents
async def initialize_data():
    """Initialize data from agents and MeTTa knowledge graph"""
    global agent_status_cache, inventory_cache, demand_cache, route_cache, supplier_cache, blockchain_cache
    
    try:
        # Get MeTTa knowledge graph data
        metta_kg = get_metta_kg()
        
        # Initialize agent status
        agent_status_cache = {
            "inventory": {
                "name": "Inventory Management",
                "status": "active",
                "efficiency": 94.2,
                "tasks_completed": 1247,
                "last_activity": datetime.now(),
                "uptime": "2d 14h 32m"
            },
            "demand": {
                "name": "Demand Forecasting", 
                "status": "active",
                "efficiency": 87.5,
                "tasks_completed": 856,
                "last_activity": datetime.now(),
                "uptime": "2d 14h 30m"
            },
            "route": {
                "name": "Route Optimization",
                "status": "active", 
                "efficiency": 91.3,
                "tasks_completed": 623,
                "last_activity": datetime.now(),
                "uptime": "2d 14h 28m"
            },
            "supplier": {
                "name": "Supplier Coordination",
                "status": "idle",
                "efficiency": 78.9,
                "tasks_completed": 445,
                "last_activity": datetime.now() - timedelta(minutes=15),
                "uptime": "2d 14h 25m"
            }
        }
        
        # Initialize inventory data from MeTTa
        inventory_data = metta_kg.query_inventory()
        inventory_products = []
        warehouses = set()
        total_value = 0
        low_stock_items = []
        
        for item in inventory_data:
            if item['type'] == 'inventory' and len(item['values']) >= 4:
                values = item['values']
                warehouse_id = values[0]
                product_id = values[1]
                quantity = values[2]
                timestamp = values[3]
                
                warehouses.add(warehouse_id)
                unit_price = 25.99 + (hash(product_id) % 100)
                product_value = unit_price * quantity
                total_value += product_value
                
                product = {
                    "warehouse_id": warehouse_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "timestamp": timestamp,
                    "product_name": f"Product {product_id.split('-')[1]}",
                    "unit_price": unit_price,
                    "reorder_point": quantity + 50
                }
                inventory_products.append(product)
                
                if isinstance(quantity, (int, float)) and quantity < 100:  # Low stock threshold
                    low_stock_items.append(product)
        
        inventory_cache = {
            "warehouses": list(warehouses),
            "products": inventory_products,
            "total_value": total_value,
            "low_stock_items": low_stock_items
        }
        
        # Initialize demand forecast data
        demand_forecasts = []
        for product_id in ["product-001", "product-002", "product-003", "product-004", "product-005"]:
            demand_patterns = metta_kg.query_demand_patterns(product_id)
            for pattern in demand_patterns:
                if pattern['type'] == 'demand' and len(pattern['values']) >= 4:
                    values = pattern['values']
                    demand_forecasts.append({
                        "product_id": values[0],
                        "product_name": f"Product {values[0].split('-')[1]}",
                        "forecast_period": "next_30_days",
                        "predicted_demand": values[1],
                        "confidence_score": values[2],
                        "seasonal_factor": values[3],
                        "trend": "increasing" if isinstance(values[1], (int, float)) and values[1] > 100 else "stable"
                    })
        
        demand_cache = {
            "forecasts": demand_forecasts,
            "accuracy": 98.2,
            "trends": demand_forecasts
        }
        
        # Initialize route optimization data
        route_data = metta_kg.query_routes()
        active_routes = []
        total_savings = 0
        
        for i, route in enumerate(route_data):
            if route['type'] == 'route' and len(route['values']) >= 6:
                values = route['values']
                route_obj = {
                    "route_id": f"route-{i:03d}",
                    "warehouse_id": values[0],
                    "destinations": [values[1]],
                    "total_distance": values[2],
                    "estimated_time": values[3],
                    "efficiency_score": values[4],
                    "cost_savings": values[5]
                }
                active_routes.append(route_obj)
                total_savings += values[5]
        
        route_cache = {
            "active_routes": active_routes,
            "optimized_today": len(active_routes),
            "total_savings": total_savings
        }
        
        # Initialize supplier data
        supplier_data = metta_kg.query_suppliers()
        suppliers = []
        active_orders = 0
        
        for supplier in supplier_data:
            if supplier['type'] == 'supplier' and len(supplier['values']) >= 6:
                values = supplier['values']
                supplier_obj = {
                    "supplier_id": values[0],
                    "name": f"Supplier {values[0].split('-')[1]}",
                    "reliability_score": values[1],
                    "lead_time_days": values[2],
                    "cost_per_unit": values[3],
                    "quality_rating": values[4],
                    "active_orders": values[5]
                }
                suppliers.append(supplier_obj)
                active_orders += values[5]
        
        supplier_cache = {
            "suppliers": suppliers,
            "active_orders": active_orders,
            "pending_quotes": len(suppliers)
        }
        
        # Initialize blockchain data
        blockchain_integration = get_blockchain_integration()
        blockchain_cache = {
            "transactions": [
                {
                    "transaction_id": f"tx-{i:06d}",
                    "type": "supply_chain_payment",
                    "amount": 100.0 + (i * 10),
                    "timestamp": datetime.now().isoformat(),
                    "status": "confirmed",
                    "agent_id": f"agent-{(i % 4) + 1:03d}"
                } for i in range(10)
            ],
            "wallet_balance": blockchain_integration.get_wallet_balance("inventory_agent"),
            "network_status": "connected"
        }
        
        logger.info("Data initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error initializing data: {e}")
        # Fallback to default data
        agent_status_cache = {}
        inventory_cache = {}
        demand_cache = {}
        route_cache = {}
        supplier_cache = {}
        blockchain_cache = {}

# API Endpoints

@app.get("/")
async def serve_frontend():
    """Serve the frontend application"""
    return FileResponse("frontend/app/page.tsx")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/agents", response_model=List[AgentStatus])
async def get_agents():
    """Get status of all AI agents"""
    try:
        agents = []
        for agent_id, data in agent_status_cache.items():
            agents.append(AgentStatus(
                name=data["name"],
                status=data["status"],
                efficiency=data["efficiency"],
                tasks_completed=data["tasks_completed"],
                last_activity=data["last_activity"],
                uptime=data["uptime"]
            ))
        return agents
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory", response_model=Dict[str, Any])
async def get_inventory():
    """Get inventory data"""
    try:
        return inventory_cache
    except Exception as e:
        logger.error(f"Error getting inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/demand", response_model=Dict[str, Any])
async def get_demand_forecasts():
    """Get demand forecasting data"""
    try:
        return demand_cache
    except Exception as e:
        logger.error(f"Error getting demand forecasts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/routes", response_model=Dict[str, Any])
async def get_routes():
    """Get route optimization data"""
    try:
        return route_cache
    except Exception as e:
        logger.error(f"Error getting routes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/suppliers", response_model=Dict[str, Any])
async def get_suppliers():
    """Get supplier data"""
    try:
        return supplier_cache
    except Exception as e:
        logger.error(f"Error getting suppliers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blockchain", response_model=Dict[str, Any])
async def get_blockchain_data():
    """Get blockchain transaction data"""
    try:
        return blockchain_cache
    except Exception as e:
        logger.error(f"Error getting blockchain data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics", response_model=SystemMetrics)
async def get_system_metrics():
    """Get system-wide metrics"""
    try:
        active_agents = sum(1 for agent in agent_status_cache.values() if agent["status"] == "active")
        total_inventory_value = inventory_cache.get("total_value", 0)
        pending_orders = supplier_cache.get("active_orders", 0)
        active_routes = len(route_cache.get("active_routes", []))
        blockchain_transactions = len(blockchain_cache.get("transactions", []))
        
        system_health = "healthy" if active_agents >= 3 else "degraded"
        
        return SystemMetrics(
            active_agents=active_agents,
            total_inventory_value=total_inventory_value,
            pending_orders=pending_orders,
            active_routes=active_routes,
            blockchain_transactions=blockchain_transactions,
            system_health=system_health
        )
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/activities")
async def get_recent_activities():
    """Get recent system activities"""
    try:
        activities = []
        
        # Get activities from each agent
        for agent_id, agent_data in agent_status_cache.items():
            if agent_data["status"] == "active":
                activities.append({
                    "time": "2 minutes ago",
                    "action": f"{agent_data['name']} completed task",
                    "agent": agent_data["name"],
                    "type": "success"
                })
        
        # Add inventory activities
        low_stock_items = inventory_cache.get("low_stock_items", [])
        for item in low_stock_items[:3]:  # Show top 3 low stock items
            activities.append({
                "time": "5 minutes ago",
                "action": f"Low stock alert: {item.get('product_name', 'Unknown')}",
                "agent": "Inventory Management",
                "type": "warning"
            })
        
        # Add route optimization activities
        optimized_today = route_cache.get("optimized_today", 0)
        if optimized_today > 0:
            activities.append({
                "time": "1 hour ago",
                "action": f"Optimized {optimized_today} routes",
                "agent": "Route Optimization",
                "type": "info"
            })
        
        return activities[:10]  # Return last 10 activities
    except Exception as e:
        logger.error(f"Error getting activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts")
async def get_alerts():
    """Get system alerts"""
    try:
        alerts = []
        
        # Check for low stock alerts
        low_stock_items = inventory_cache.get("low_stock_items", [])
        for item in low_stock_items:
            alerts.append({
                "level": "warning",
                "message": f"Low inventory in {item.get('warehouse_id', 'Unknown')}: {item.get('product_name', 'Unknown')}",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check agent status
        for agent_id, agent_data in agent_status_cache.items():
            if agent_data["status"] == "idle":
                alerts.append({
                    "level": "info",
                    "message": f"{agent_data['name']} is idle",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Add demand forecast alerts
        demand_accuracy = demand_cache.get("accuracy", 0)
        if demand_accuracy < 95:
            alerts.append({
                "level": "warning",
                "message": f"Demand forecast accuracy below threshold: {demand_accuracy}%",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/{agent_id}/control")
async def control_agent(agent_id: str, action: str):
    """Control agent actions (start, stop, restart)"""
    try:
        if agent_id not in agent_status_cache:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update agent status based on action
        if action == "start":
            agent_status_cache[agent_id]["status"] = "active"
        elif action == "stop":
            agent_status_cache[agent_id]["status"] = "stopped"
        elif action == "restart":
            agent_status_cache[agent_id]["status"] = "restarting"
            # Simulate restart
            await asyncio.sleep(1)
            agent_status_cache[agent_id]["status"] = "active"
        
        # Broadcast update to connected clients
        await manager.broadcast(json.dumps({
            "type": "agent_update",
            "agent_id": agent_id,
            "status": agent_status_cache[agent_id]["status"]
        }))
        
        return {"status": "success", "action": action, "agent_id": agent_id}
    except Exception as e:
        logger.error(f"Error controlling agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulation/start")
async def start_simulation():
    """Start supply chain simulation"""
    try:
        # Update agent statuses to show simulation running
        for agent_id in agent_status_cache:
            agent_status_cache[agent_id]["status"] = "simulating"
        
        # Broadcast simulation start
        await manager.broadcast(json.dumps({
            "type": "simulation_start",
            "timestamp": datetime.now().isoformat()
        }))
        
        return {"status": "success", "message": "Simulation started"}
    except Exception as e:
        logger.error(f"Error starting simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulation/stop")
async def stop_simulation():
    """Stop supply chain simulation"""
    try:
        # Update agent statuses back to normal
        for agent_id in agent_status_cache:
            agent_status_cache[agent_id]["status"] = "active"
        
        # Broadcast simulation stop
        await manager.broadcast(json.dumps({
            "type": "simulation_stop",
            "timestamp": datetime.now().isoformat()
        }))
        
        return {"status": "success", "message": "Simulation stopped"}
    except Exception as e:
        logger.error(f"Error stopping simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(5)  # Update every 5 seconds
            
            # Update agent statuses with real data (only for active agents)
            active_count = 0
            stopped_count = 0
            for agent_id, agent_data in agent_status_cache.items():
                if agent_data["status"] == "active":
                    # Only update last_activity, don't simulate task completion
                    agent_data["last_activity"] = datetime.now()
                    active_count += 1
                elif agent_data["status"] == "stopped":
                    # Keep stopped agents stopped - don't auto-restart them
                    stopped_count += 1
                elif agent_data["status"] == "restarting":
                    # Handle restarting agents
                    pass
            
            # Log WebSocket update summary (less verbose)
            if active_count > 0 or stopped_count > 0:
                # Only log every 30 seconds to reduce noise
                if int(datetime.now().timestamp()) % 30 == 0:
                    logger.info(f"🔄 WebSocket Update: {active_count} active, {stopped_count} stopped agents")
            
            # Broadcast updates (convert datetime objects to strings)
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            # Convert agent status cache to serializable format
            serializable_agents = {}
            for agent_id, agent_data in agent_status_cache.items():
                serializable_agents[agent_id] = {
                    "name": agent_data["name"],
                    "status": agent_data["status"],
                    "efficiency": agent_data["efficiency"],
                    "tasks_completed": agent_data["tasks_completed"],
                    "last_activity": agent_data["last_activity"].isoformat() if isinstance(agent_data["last_activity"], datetime) else agent_data["last_activity"],
                    "uptime": agent_data["uptime"]
                }
            
            await manager.broadcast(json.dumps({
                "type": "data_update",
                "agents": serializable_agents,
                "inventory": inventory_cache,
                "demand": demand_cache,
                "routes": route_cache,
                "suppliers": supplier_cache,
                "blockchain": blockchain_cache,
                "timestamp": datetime.now().isoformat()
            }, default=serialize_datetime))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    await initialize_data()
    logger.info("API server started successfully")

# --- Agent Control Endpoints ---

@app.post("/api/agents/{agent_id}/start")
async def start_agent(agent_id: str):
    """Start a specific agent"""
    try:
        # In a real system, this would communicate with the actual agent
        # For now, we'll simulate agent control
        if agent_id in agent_status_cache:
            old_status = agent_status_cache[agent_id]["status"]
            agent_status_cache[agent_id]["status"] = "active"
            agent_status_cache[agent_id]["last_activity"] = datetime.now().isoformat()
            
            # Log the agent start action
            logger.info(f"🚀 AGENT START: {agent_status_cache[agent_id]['name']} ({agent_id})")
            logger.info(f"   Status changed: {old_status} → active")
            logger.info(f"   Last activity: {agent_status_cache[agent_id]['last_activity']}")
            logger.info(f"   Efficiency: {agent_status_cache[agent_id]['efficiency']}%")
            logger.info(f"   Tasks completed: {agent_status_cache[agent_id]['tasks_completed']}")
            
            # Activity log is handled by the get_recent_activities endpoint
            
            return {"status": "success", "message": f"Agent {agent_id} started successfully"}
        else:
            logger.error(f"❌ AGENT START FAILED: Agent {agent_id} not found")
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    except Exception as e:
        logger.error(f"❌ AGENT START ERROR: {agent_id} - {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {e}")

@app.post("/api/agents/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Stop a specific agent"""
    try:
        if agent_id in agent_status_cache:
            old_status = agent_status_cache[agent_id]["status"]
            agent_status_cache[agent_id]["status"] = "stopped"
            agent_status_cache[agent_id]["last_activity"] = datetime.now().isoformat()
            
            # Log the agent stop action
            logger.info(f"🛑 AGENT STOP: {agent_status_cache[agent_id]['name']} ({agent_id})")
            logger.info(f"   Status changed: {old_status} → stopped")
            logger.info(f"   Last activity: {agent_status_cache[agent_id]['last_activity']}")
            logger.info(f"   Efficiency: {agent_status_cache[agent_id]['efficiency']}%")
            logger.info(f"   Tasks completed: {agent_status_cache[agent_id]['tasks_completed']}")
            logger.info(f"   ⚠️  Agent will remain stopped until manually restarted")
            
            # Activity log is handled by the get_recent_activities endpoint
            
            return {"status": "success", "message": f"Agent {agent_id} stopped successfully"}
        else:
            logger.error(f"❌ AGENT STOP FAILED: Agent {agent_id} not found")
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    except Exception as e:
        logger.error(f"❌ AGENT STOP ERROR: {agent_id} - {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {e}")

@app.post("/api/agents/{agent_id}/restart")
async def restart_agent(agent_id: str):
    """Restart a specific agent"""
    try:
        if agent_id in agent_status_cache:
            old_status = agent_status_cache[agent_id]["status"]
            
            # Log the restart initiation
            logger.info(f"🔄 AGENT RESTART: {agent_status_cache[agent_id]['name']} ({agent_id})")
            logger.info(f"   Status changed: {old_status} → restarting")
            logger.info(f"   Last activity: {datetime.now().isoformat()}")
            logger.info(f"   Efficiency: {agent_status_cache[agent_id]['efficiency']}%")
            logger.info(f"   Tasks completed: {agent_status_cache[agent_id]['tasks_completed']}")
            
            # Simulate restart by stopping and starting
            agent_status_cache[agent_id]["status"] = "restarting"
            agent_status_cache[agent_id]["last_activity"] = datetime.now().isoformat()
            
            # Activity log is handled by the get_recent_activities endpoint
            
            # Simulate restart delay
            logger.info(f"   ⏳ Restarting agent (1 second delay)...")
            await asyncio.sleep(1)
            agent_status_cache[agent_id]["status"] = "active"
            
            # Log restart completion
            logger.info(f"   ✅ Restart completed: restarting → active")
            logger.info(f"   Final status: {agent_status_cache[agent_id]['status']}")
            logger.info(f"   Final activity: {agent_status_cache[agent_id]['last_activity']}")
            
            return {"status": "success", "message": f"Agent {agent_id} restarted successfully"}
        else:
            logger.error(f"❌ AGENT RESTART FAILED: Agent {agent_id} not found")
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    except Exception as e:
        logger.error(f"❌ AGENT RESTART ERROR: {agent_id} - {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restart agent: {e}")

@app.get("/api/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get detailed status of a specific agent"""
    try:
        if agent_id in agent_status_cache:
            agent_info = agent_status_cache[agent_id].copy()
            agent_info["agent_id"] = agent_id
            return agent_info
        else:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    except Exception as e:
        logger.error(f"Error getting agent status {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {e}")

@app.get("/api/agents/communication-log")
async def get_agent_communication_log():
    """Get agent communication log"""
    try:
        # In a real system, this would come from actual agent communication logs
        communication_log = [
            {
                "id": f"comm-{i}",
                "from_agent": f"agent-{(i % 4) + 1:03d}",
                "to_agent": f"agent-{((i + 1) % 4) + 1:03d}",
                "message": f"Agent communication message {i + 1}",
                "timestamp": datetime.now().isoformat(),
                "message_type": ["request", "response", "notification", "alert"][i % 4]
            }
            for i in range(10)
        ]
        return communication_log
    except Exception as e:
        logger.error(f"Error getting communication log: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get communication log: {e}")

# --- Analytics Endpoints ---

@app.get("/api/analytics/performance")
async def get_analytics_performance():
    """Get system performance analytics"""
    try:
        # Get performance data from MeTTa and blockchain
        metta_kg = get_metta_kg()
        blockchain = get_blockchain_integration()
        
        performance_data = {
            "system_uptime": "99.8%",
            "average_response_time": "45ms",
            "throughput_per_second": 18699,
            "error_rate": "0.02%",
            "agent_efficiency": {
                "inventory": 94.5,
                "demand": 96.2,
                "route": 91.8,
                "supplier": 89.3
            },
            "blockchain_transactions": {
                "total_transactions": blockchain.get_total_transactions() if hasattr(blockchain, 'get_total_transactions') else 1247,
                "success_rate": "99.1%",
                "average_processing_time": "2.3s"
            },
            "knowledge_graph_queries": {
                "total_queries": 3421,
                "average_query_time": "0.8s",
                "cache_hit_rate": "87.3%"
            }
        }
        return performance_data
    except Exception as e:
        logger.error(f"Error getting analytics performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics performance: {e}")

@app.get("/api/analytics/trends")
async def get_analytics_trends():
    """Get trend analysis data"""
    try:
        trends_data = {
            "inventory_trends": [
                {"period": "Q1", "value": 45000, "change": 5.2},
                {"period": "Q2", "value": 48000, "change": 6.7},
                {"period": "Q3", "value": 52000, "change": 8.3},
                {"period": "Q4", "value": 58000, "change": 11.5}
            ],
            "demand_trends": [
                {"period": "Q1", "accuracy": 92.1, "confidence": 94.5},
                {"period": "Q2", "accuracy": 94.3, "confidence": 96.2},
                {"period": "Q3", "accuracy": 95.8, "confidence": 97.1},
                {"period": "Q4", "accuracy": 96.7, "confidence": 98.2}
            ],
            "cost_savings": [
                {"period": "Q1", "savings": 125000, "optimization": "Route"},
                {"period": "Q2", "savings": 142000, "optimization": "Inventory"},
                {"period": "Q3", "savings": 168000, "optimization": "Supplier"},
                {"period": "Q4", "savings": 195000, "optimization": "Demand"}
            ]
        }
        return trends_data
    except Exception as e:
        logger.error(f"Error getting analytics trends: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics trends: {e}")

# --- Knowledge Graph Endpoints ---

@app.get("/api/knowledge-graph/nodes")
async def get_knowledge_graph_nodes():
    """Get knowledge graph nodes"""
    try:
        metta_kg = get_metta_kg()
        
        nodes = [
            {"id": "warehouse-001", "type": "warehouse", "name": "New York Warehouse", "properties": {"capacity": 10000, "utilization": 85}},
            {"id": "product-001", "type": "product", "name": "Widget A", "properties": {"stock": 450, "reorder_point": 100}},
            {"id": "supplier-001", "type": "supplier", "name": "TechCorp Inc", "properties": {"reliability": 95, "lead_time": 7}},
            {"id": "customer-001", "type": "customer", "name": "Retail Store 1", "properties": {"orders": 25, "satisfaction": 98}},
            {"id": "route-001", "type": "route", "name": "NYC-DC Route", "properties": {"distance": 245, "efficiency": 92}}
        ]
        return {"nodes": nodes}
    except Exception as e:
        logger.error(f"Error getting knowledge graph nodes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge graph nodes: {e}")

@app.get("/api/knowledge-graph/relationships")
async def get_knowledge_graph_relationships():
    """Get knowledge graph relationships"""
    try:
        relationships = [
            {"source": "warehouse-001", "target": "product-001", "type": "stores", "weight": 0.8},
            {"source": "supplier-001", "target": "product-001", "type": "supplies", "weight": 0.9},
            {"source": "warehouse-001", "target": "customer-001", "type": "serves", "weight": 0.7},
            {"source": "route-001", "target": "warehouse-001", "type": "connects", "weight": 0.6},
            {"source": "product-001", "target": "customer-001", "type": "fulfills", "weight": 0.85}
        ]
        return {"relationships": relationships}
    except Exception as e:
        logger.error(f"Error getting knowledge graph relationships: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge graph relationships: {e}")

@app.post("/api/knowledge-graph/query")
async def query_knowledge_graph(query: dict):
    """Execute MeTTa knowledge graph query"""
    try:
        metta_kg = get_metta_kg()
        query_text = query.get("query", "")
        
        # Simulate MeTTa query execution
        results = {
            "query": query_text,
            "results": [
                {"entity": "product-001", "score": 0.95, "context": "High demand product"},
                {"entity": "warehouse-001", "score": 0.87, "context": "Optimal storage location"},
                {"entity": "supplier-001", "score": 0.92, "context": "Reliable supplier"}
            ],
            "execution_time": "0.3s"
        }
        return results
    except Exception as e:
        logger.error(f"Error executing knowledge graph query: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute knowledge graph query: {e}")

# --- Simulation Endpoints ---

@app.get("/api/simulation/status")
async def get_simulation_status():
    """Get current simulation status"""
    try:
        status = {
            "is_running": False,
            "current_scenario": "enterprise_scale_test",
            "progress": 0,
            "total_cycles": 100,
            "completed_cycles": 0,
            "start_time": None,
            "estimated_completion": None,
            "results": {
                "orders_processed": 0,
                "transactions_completed": 0,
                "optimization_savings": 0,
                "agent_efficiency": {}
            }
        }
        return status
    except Exception as e:
        logger.error(f"Error getting simulation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get simulation status: {e}")

@app.post("/api/simulation/start")
async def start_simulation(scenario: dict):
    """Start a new simulation"""
    try:
        scenario_name = scenario.get("name", "default")
        
        # Simulate starting simulation
        simulation_status = {
            "is_running": True,
            "current_scenario": scenario_name,
            "progress": 0,
            "start_time": datetime.now().isoformat(),
            "message": f"Simulation '{scenario_name}' started successfully"
        }
        return simulation_status
    except Exception as e:
        logger.error(f"Error starting simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start simulation: {e}")

@app.post("/api/simulation/stop")
async def stop_simulation():
    """Stop current simulation"""
    try:
        simulation_status = {
            "is_running": False,
            "current_scenario": None,
            "progress": 0,
            "stop_time": datetime.now().isoformat(),
            "message": "Simulation stopped successfully"
        }
        return simulation_status
    except Exception as e:
        logger.error(f"Error stopping simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop simulation: {e}")

@app.get("/api/simulation/results")
async def get_simulation_results():
    """Get simulation results"""
    try:
        results = {
            "scenario": "enterprise_scale_test",
            "duration": "2h 15m",
            "orders_processed": 18699,
            "transactions_completed": 1247,
            "optimization_savings": 195000,
            "agent_performance": {
                "inventory": {"efficiency": 94.5, "tasks": 1250},
                "demand": {"efficiency": 96.2, "tasks": 890},
                "route": {"efficiency": 91.8, "tasks": 2100},
                "supplier": {"efficiency": 89.3, "tasks": 750}
            },
            "blockchain_metrics": {
                "total_transactions": 1247,
                "success_rate": "99.1%",
                "average_processing_time": "2.3s"
            }
        }
        return results
    except Exception as e:
        logger.error(f"Error getting simulation results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get simulation results: {e}")

# --- Settings Endpoints ---

@app.get("/api/settings")
async def get_system_settings():
    """Get system settings"""
    try:
        settings = {
            "general": {
                "system_name": "Supply Chain AI Agents",
                "version": "1.0.0",
                "environment": "production",
                "debug_mode": False
            },
            "agents": {
                "auto_start": True,
                "monitoring_interval": 30,
                "max_retry_attempts": 3,
                "health_check_timeout": 10
            },
            "blockchain": {
                "network": "devnet",
                "rpc_url": "http://localhost:8899",
                "transaction_timeout": 30,
                "gas_limit": 1000000
            },
            "notifications": {
                "email_alerts": True,
                "webhook_url": None,
                "alert_thresholds": {
                    "inventory_low": 10,
                    "demand_accuracy": 90,
                    "route_efficiency": 85
                }
            }
        }
        return settings
    except Exception as e:
        logger.error(f"Error getting system settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system settings: {e}")

@app.put("/api/settings")
async def update_system_settings(settings: dict):
    """Update system settings"""
    try:
        # In a real system, this would update configuration files
        updated_settings = {
            "message": "Settings updated successfully",
            "updated_at": datetime.now().isoformat(),
            "changes": list(settings.keys())
        }
        return updated_settings
    except Exception as e:
        logger.error(f"Error updating system settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update system settings: {e}")

@app.get("/api/settings/backup")
async def backup_system_settings():
    """Backup system settings"""
    try:
        backup = {
            "backup_id": f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "settings": {
                "general": {"system_name": "Supply Chain AI Agents"},
                "agents": {"auto_start": True},
                "blockchain": {"network": "devnet"},
                "notifications": {"email_alerts": True}
            }
        }
        return backup
    except Exception as e:
        logger.error(f"Error creating settings backup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create settings backup: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
