"""
Inventory Management Agent for the Supply Chain AI Agents system.
Monitors stock levels, tracks SKU availability, and triggers reorder events.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Dict, List, Optional
import httpx

from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

from shared_protocols import (
    InventoryUpdate,
    ReorderRequest,
    DemandForecast,
    create_text_chat,
    create_acknowledgement,
    AGENT_ADDRESSES
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.mock_metta_integration import get_metta_kg

# Backend API URL
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the agent
agent = Agent(
    name="inventory_management_agent",
    seed="inventory_agent_seed_phrase_here",
    port=8001,
    endpoint="http://localhost:8001/submit",
)

# Fund the agent if needed (with proper wallet handling)
try:
    fund_agent_if_low(agent.wallet)
except Exception as e:
    logger.warning(f"Could not fund agent wallet: {e}")
    logger.info("Agent will run without funding (for demo purposes)")

# Initialize MeTTa knowledge graph
metta_kg = get_metta_kg()

# Initialize the chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

# Agent state
agent_state = {
    "warehouses": {
        "warehouse-001": {"location": "New York", "capacity": 1000},
        "warehouse-002": {"location": "Los Angeles", "capacity": 1500},
    },
    "inventory": {},
    "reorder_points": {
        "product-123": 100,
        "product-456": 50,
        "product-789": 75,
    },
    "pending_orders": {},
    "last_check": datetime.utcnow()
}


def check_inventory_levels() -> List[Dict]:
    """Check current inventory levels against reorder points."""
    low_stock_items = []
    
    try:
        # Query MeTTa for current inventory levels
        inventory_data = metta_kg.query_inventory()
        
        for item in inventory_data:
            if len(item.get('values', [])) >= 3:
                warehouse_id = item['values'][0]
                product_id = item['values'][1]
                quantity = int(item['values'][2])
                
                # Check if below reorder point
                reorder_point = agent_state["reorder_points"].get(product_id, 0)
                if quantity <= reorder_point:
                    low_stock_items.append({
                        "warehouse_id": warehouse_id,
                        "product_id": product_id,
                        "current_quantity": quantity,
                        "reorder_point": reorder_point,
                        "shortage": reorder_point - quantity
                    })
                    logger.info(f"Low stock alert: {product_id} in {warehouse_id} - {quantity}/{reorder_point}")
        
        return low_stock_items
        
    except Exception as e:
        logger.error(f"Error checking inventory levels: {e}")
        return []


def calculate_reorder_quantity(product_id: str, current_quantity: int, reorder_point: int) -> int:
    """Calculate optimal reorder quantity based on demand patterns."""
    try:
        # Query MeTTa for demand patterns
        demand_data = metta_kg.query_demand_patterns(product_id)
        
        # Calculate average monthly demand
        monthly_demands = []
        for item in demand_data:
            if len(item.get('values', [])) >= 2:
                try:
                    demand = int(item['values'][1])
                    monthly_demands.append(demand)
                except (ValueError, IndexError):
                    continue
        
        if monthly_demands:
            avg_monthly_demand = sum(monthly_demands) / len(monthly_demands)
            # Reorder quantity = 2 months of demand + safety buffer
            reorder_quantity = int(avg_monthly_demand * 2.5)
        else:
            # Default reorder quantity if no historical data
            reorder_quantity = reorder_point * 3
        
        logger.info(f"Calculated reorder quantity for {product_id}: {reorder_quantity}")
        return reorder_quantity
        
    except Exception as e:
        logger.error(f"Error calculating reorder quantity: {e}")
        return reorder_point * 3  # Fallback


async def get_agent_address(agent_id: str) -> Optional[str]:
    """Get agent address from backend registry"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_API_URL}/api/agents/discover", params={"agent_id": agent_id}, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("agent_address")
            else:
                logger.warning(f"Agent {agent_id} not found in registry, using fallback")
                return AGENT_ADDRESSES.get(agent_id)
    except Exception as e:
        logger.warning(f"Error discovering agent {agent_id}: {e}, using fallback")
        return AGENT_ADDRESSES.get(agent_id)

async def report_activity(activity_type: str, details: Dict):
    """Report agent activity to backend"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{BACKEND_API_URL}/api/agents/report-activity",
                json={
                    "agent_id": "inventory",
                    "activity_type": activity_type,
                    "details": details,
                    "timestamp": datetime.utcnow().isoformat()
                },
                timeout=2.0
            )
    except Exception as e:
        logger.debug(f"Could not report activity to backend: {e}")

async def request_demand_forecast(ctx: Context, product_id: str) -> Optional[DemandForecast]:
    """Request demand forecast from Demand Forecasting Agent."""
    try:
        # Try to get actual agent address from registry
        demand_agent = await get_agent_address("demand")
        
        if not demand_agent:
            logger.warning("Demand agent address not available, skipping request")
            return None
        
        # Create demand forecast request
        request_data = {
            "product_id": product_id,
            "forecast_period": "next_30_days",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send request to demand agent
        message = create_text_chat(json.dumps(request_data))
        await ctx.send(demand_agent, message)
        
        logger.info(f"Sent demand forecast request for {product_id} to demand agent")
        
        # Report activity
        await report_activity("demand_forecast_request", {"product_id": product_id})
        
        return None  # Will receive response asynchronously
        
    except Exception as e:
        logger.error(f"Error requesting demand forecast: {e}")
        return None


async def create_reorder_approval(product_id: str, quantity: int, warehouse_id: str, current_quantity: int, reorder_point: int) -> bool:
    """Create a pending approval for reorder instead of auto-executing."""
    try:
        # Estimate cost (simplified - in real system would query supplier prices)
        estimated_unit_cost = 25.0 + (hash(product_id) % 50)  # $25-$75 per unit
        estimated_cost = estimated_unit_cost * quantity
        
        # Create approval request with unique ID (using UUID to prevent collisions)
        approval_data = {
            "id": f"reorder-{product_id}-{warehouse_id}-{uuid4().hex[:8]}",
            "type": "reorder",
            "agent_id": "inventory",
            "title": f"Reorder Request: {product_id}",
            "description": f"Low stock detected for {product_id} in {warehouse_id}. Current: {current_quantity}, Reorder Point: {reorder_point}",
            "details": {
                "product_id": product_id,
                "warehouse_id": warehouse_id,
                "quantity": quantity,
                "current_quantity": current_quantity,
                "reorder_point": reorder_point,
                "estimated_unit_cost": estimated_unit_cost,
                "urgency": "medium"
            },
            "estimated_cost": estimated_cost,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "status": "pending"
        }
        
        # Send to backend API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_API_URL}/api/approvals",
                json=approval_data,
                timeout=5.0
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("auto_approved"):
                    logger.info(f"Reorder auto-approved for {product_id} (below threshold)")
                    return True
                else:
                    logger.info(f"Created pending approval for reorder: {product_id}")
                    return False
            else:
                logger.error(f"Failed to create approval: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Error creating reorder approval: {e}")
        return False

async def trigger_supplier_order(ctx: Context, product_id: str, quantity: int, warehouse_id: str):
    """Trigger reorder with Supplier Coordination Agent (called after approval)."""
    try:
        # Try to get actual agent address from registry
        supplier_agent = await get_agent_address("supplier")
        
        if not supplier_agent:
            logger.warning("Supplier agent address not available, skipping request")
            return
        
        # Create reorder request
        reorder_request = ReorderRequest(
            product_id=product_id,
            quantity=quantity,
            warehouse_id=warehouse_id,
            urgency="medium",
            preferred_suppliers=["supplier-001", "supplier-002"],
            timestamp=datetime.utcnow(),
            agent_id=agent.address
        )
        
        # Send reorder request to supplier agent
        request_data = {
            "type": "reorder_request",
            "data": {
                "product_id": product_id,
                "quantity": quantity,
                "warehouse_id": warehouse_id,
                "urgency": "medium",
                "preferred_suppliers": ["supplier-001", "supplier-002"],
                "timestamp": datetime.utcnow().isoformat(),
                "agent_id": agent.address
            }
        }
        
        message = create_text_chat(json.dumps(request_data))
        await ctx.send(supplier_agent, message)
        
        logger.info(f"Sent reorder request for {product_id} to supplier agent")
        
        # Report activity
        await report_activity("reorder_request", {
            "product_id": product_id,
            "quantity": quantity,
            "warehouse_id": warehouse_id
        })
        
    except Exception as e:
        logger.error(f"Error triggering supplier order: {e}")


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages."""
    ctx.logger.info(f"Received message from {sender}")
    
    # Always send back an acknowledgement
    await ctx.send(sender, create_acknowledgement(msg.msg_id))
    
    try:
        # Process each content item
        for item in msg.content:
            if isinstance(item, StartSessionContent):
                ctx.logger.info(f"Session started with {sender}")
                
            elif isinstance(item, TextContent):
                ctx.logger.info(f"Text message from {sender}: {item.text}")
                
                try:
                    # Parse message data
                    message_data = json.loads(item.text)
                    message_type = message_data.get("type")
                    
                    if message_type == "demand_forecast_response":
                        # Handle demand forecast response
                        forecast_data = message_data.get("data", {})
                        product_id = forecast_data.get("product_id")
                        predicted_demand = forecast_data.get("predicted_demand", 0)
                        
                        ctx.logger.info(f"Received demand forecast for {product_id}: {predicted_demand}")
                        
                        # Update MeTTa with forecast data
                        metta_kg.add_demand_forecast(
                            product_id, 
                            "next_30_days", 
                            predicted_demand, 
                            forecast_data.get("confidence_score", 0.8)
                        )
                    
                    elif message_type == "order_confirmation":
                        # Handle order confirmation from supplier agent
                        order_data = message_data.get("data", {})
                        product_id = order_data.get("product_id")
                        quantity = order_data.get("quantity")
                        supplier_id = order_data.get("supplier_id")
                        
                        ctx.logger.info(f"Order confirmed: {product_id} x {quantity} from {supplier_id}")
                        
                        # Update pending orders
                        agent_state["pending_orders"][product_id] = {
                            "quantity": quantity,
                            "supplier_id": supplier_id,
                            "status": "confirmed",
                            "timestamp": datetime.utcnow()
                        }
                    
                except json.JSONDecodeError:
                    ctx.logger.warning(f"Could not parse JSON message: {item.text}")
                
            elif isinstance(item, EndSessionContent):
                ctx.logger.info(f"Session ended with {sender}")
                
            else:
                ctx.logger.info(f"Received unexpected content type from {sender}")
                
    except Exception as e:
        ctx.logger.error(f"Error handling message: {e}")


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle message acknowledgements."""
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")


@agent.on_interval(period=30.0)
async def inventory_monitoring_cycle(ctx: Context):
    """Periodic inventory monitoring and reorder logic."""
    ctx.logger.info("Starting inventory monitoring cycle")
    
    try:
        # Check inventory levels
        low_stock_items = check_inventory_levels()
        
        if low_stock_items:
            ctx.logger.info(f"Found {len(low_stock_items)} items below reorder point")
            
            for item in low_stock_items:
                product_id = item["product_id"]
                warehouse_id = item["warehouse_id"]
                current_quantity = item["current_quantity"]
                reorder_point = item["reorder_point"]
                
                # Calculate reorder quantity
                reorder_quantity = calculate_reorder_quantity(
                    product_id, current_quantity, reorder_point
                )
                
                # Request demand forecast (for information in approval)
                await request_demand_forecast(ctx, product_id)
                
                # Create pending approval instead of auto-executing
                auto_approved = await create_reorder_approval(
                    product_id, reorder_quantity, warehouse_id, current_quantity, reorder_point
                )
                
                # Only trigger supplier order if auto-approved
                if auto_approved:
                    await trigger_supplier_order(ctx, product_id, reorder_quantity, warehouse_id)
                    ctx.logger.info(f"Auto-approved and triggered reorder for {product_id}: {reorder_quantity} units")
                else:
                    ctx.logger.info(f"Created pending approval for {product_id}: {reorder_quantity} units")
                
                # Update MeTTa with inventory update
                metta_kg.add_inventory_update(warehouse_id, product_id, current_quantity)
            
            # Report activity
            await report_activity("inventory_check", {
                "low_stock_items": len(low_stock_items),
                "items": [{"product_id": item["product_id"], "warehouse_id": item["warehouse_id"]} for item in low_stock_items]
            })
        else:
            ctx.logger.info("All inventory levels are adequate")
            # Report activity even when all is good
            await report_activity("inventory_check", {"low_stock_items": 0, "status": "adequate"})
            
    except Exception as e:
        ctx.logger.error(f"Error in inventory monitoring cycle: {e}")


@agent.on_interval(period=300.0)  # Every 5 minutes
async def periodic_inventory_update(ctx: Context):
    """Periodic inventory updates to MeTTa knowledge graph."""
    try:
        # Update MeTTa with current inventory state
        for warehouse_id, warehouse_data in agent_state["warehouses"].items():
            # This would typically come from real inventory system
            # For demo purposes, we'll use sample data
            sample_products = ["product-123", "product-456", "product-789"]
            for product_id in sample_products:
                # Simulate inventory levels (in real system, this would be actual data)
                import random
                quantity = random.randint(50, 200)
                metta_kg.add_inventory_update(warehouse_id, product_id, quantity)
        
        ctx.logger.info("Updated inventory data in MeTTa knowledge graph")
        
    except Exception as e:
        ctx.logger.error(f"Error updating inventory data: {e}")


# Include the chat protocol and publish manifest
agent.include(chat_proto, publish_manifest=True)


async def register_with_backend():
    """Register this agent with the backend API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_API_URL}/api/agents/register",
                json={
                    "agent_id": "inventory",
                    "agent_address": str(agent.address),
                    "agent_name": agent.name,
                    "port": 8001,
                    "endpoint": "http://localhost:8001/submit"
                },
                timeout=5.0
            )
            if response.status_code == 200:
                logger.info("✅ Successfully registered with backend API")
            else:
                logger.warning(f"Failed to register with backend: {response.status_code}")
    except Exception as e:
        logger.warning(f"Could not register with backend API: {e}")
        logger.info("Agent will continue running without backend registration")

if __name__ == "__main__":
    logger.info(f"Inventory Management Agent starting...")
    logger.info(f"Agent address: {agent.address}")
    logger.info(f"Agent name: {agent.name}")
    
    # Register with backend
    asyncio.run(register_with_backend())
    
    # Start the agent
    agent.run()
