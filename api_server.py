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
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
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
        inventory_data = metta_kg.get_inventory_data()
        inventory_cache = {
            "warehouses": inventory_data.get("warehouses", []),
            "products": inventory_data.get("products", []),
            "total_value": sum(item.get("quantity", 0) * item.get("unit_price", 0) for item in inventory_data.get("products", [])),
            "low_stock_items": [item for item in inventory_data.get("products", []) if item.get("quantity", 0) < item.get("reorder_point", 0)]
        }
        
        # Initialize demand forecast data
        demand_data = metta_kg.get_demand_forecasts()
        demand_cache = {
            "forecasts": demand_data.get("forecasts", []),
            "accuracy": demand_data.get("accuracy", 98.2),
            "trends": demand_data.get("trends", [])
        }
        
        # Initialize route optimization data
        route_data = metta_kg.get_route_data()
        route_cache = {
            "active_routes": route_data.get("active_routes", []),
            "optimized_today": route_data.get("optimized_today", 24),
            "total_savings": route_data.get("total_savings", 15600.50)
        }
        
        # Initialize supplier data
        supplier_data = metta_kg.get_supplier_data()
        supplier_cache = {
            "suppliers": supplier_data.get("suppliers", []),
            "active_orders": supplier_data.get("active_orders", 0),
            "pending_quotes": supplier_data.get("pending_quotes", 0)
        }
        
        # Initialize blockchain data
        blockchain_integration = get_blockchain_integration()
        blockchain_cache = {
            "transactions": blockchain_integration.get_recent_transactions(),
            "wallet_balance": blockchain_integration.get_wallet_balance(),
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
            
            # Update agent statuses with real data
            for agent_id, agent_data in agent_status_cache.items():
                if agent_data["status"] == "active":
                    # Simulate task completion
                    agent_data["tasks_completed"] += 1
                    agent_data["last_activity"] = datetime.now()
            
            # Broadcast updates
            await manager.broadcast(json.dumps({
                "type": "data_update",
                "agents": agent_status_cache,
                "inventory": inventory_cache,
                "demand": demand_cache,
                "routes": route_cache,
                "suppliers": supplier_cache,
                "blockchain": blockchain_cache,
                "timestamp": datetime.now().isoformat()
            }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    await initialize_data()
    logger.info("API server started successfully")

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
