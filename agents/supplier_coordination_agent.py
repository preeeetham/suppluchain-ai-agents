"""
Supplier Coordination Agent for the Supply Chain AI Agents system.
Manages supplier relationships, negotiates pricing, and coordinates orders.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

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
    ReorderRequest,
    SupplierQuote,
    OrderConfirmation,
    create_text_chat,
    create_acknowledgement,
    AGENT_ADDRESSES
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.mock_metta_integration import get_metta_kg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the agent
agent = Agent(
    name="supplier_coordination_agent",
    seed="supplier_agent_seed_phrase_here",
    port=8004,
    endpoint="http://localhost:8004/submit",
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
    "suppliers": {
        "supplier-001": {
            "name": "Global Supply Co",
            "reliability": 0.95,
            "quality_rating": 4.8,
            "lead_time_avg": 7,
            "cost_multiplier": 1.0
        },
        "supplier-002": {
            "name": "Fast Logistics Inc",
            "reliability": 0.90,
            "quality_rating": 4.5,
            "lead_time_avg": 5,
            "cost_multiplier": 1.1
        },
        "supplier-003": {
            "name": "Premium Materials Ltd",
            "reliability": 0.94,
            "quality_rating": 4.7,
            "lead_time_avg": 9,
            "cost_multiplier": 0.95
        }
    },
    "active_orders": {},
    "order_history": {},
    "supplier_performance": {},
    "last_update": datetime.utcnow()
}


def get_supplier_quotes(product_id: str, quantity: int) -> List[SupplierQuote]:
    """Get quotes from all available suppliers for a product."""
    try:
        # Query MeTTa for supplier data
        supplier_data = metta_kg.query_suppliers(product_id)
        
        quotes = []
        for item in supplier_data:
            if len(item.get('values', [])) >= 5:
                supplier_id = item['values'][0]
                lead_time = int(item['values'][2])
                reliability = float(item['values'][3])
                cost_per_unit = float(item['values'][4])
                
                # Check if supplier is available
                if supplier_id in agent_state["suppliers"]:
                    supplier_info = agent_state["suppliers"][supplier_id]
                    
                    # Calculate total cost with reliability factor
                    base_cost = cost_per_unit * quantity
                    reliability_discount = 1.0 - (1.0 - reliability) * 0.1  # 10% discount for reliability
                    total_cost = base_cost * reliability_discount
                    
                    # Create supplier quote
                    quote = SupplierQuote(
                        supplier_id=supplier_id,
                        product_id=product_id,
                        quantity=quantity,
                        unit_price=cost_per_unit,
                        total_cost=total_cost,
                        lead_time_days=lead_time,
                        availability=True,
                        quality_rating=supplier_info["quality_rating"],
                        timestamp=datetime.utcnow(),
                        agent_id=agent.address
                    )
                    
                    quotes.append(quote)
                    logger.info(f"Generated quote from {supplier_id}: ${total_cost:.2f}")
        
        return quotes
        
    except Exception as e:
        logger.error(f"Error getting supplier quotes: {e}")
        return []


def select_optimal_supplier(quotes: List[SupplierQuote], urgency: str) -> Optional[SupplierQuote]:
    """Select the optimal supplier based on cost, reliability, and urgency."""
    if not quotes:
        return None
    
    try:
        # Calculate weighted scores for each supplier
        scored_quotes = []
        
        for quote in quotes:
            # Cost score (lower is better)
            cost_score = 1.0 / (quote.total_cost / quote.quantity)  # Normalize by quantity
            
            # Reliability score
            reliability_score = quote.quality_rating / 5.0  # Normalize to 0-1
            
            # Lead time score (lower is better)
            lead_time_score = 1.0 / (quote.lead_time_days + 1)  # Avoid division by zero
            
            # Urgency factor
            urgency_factor = 1.0
            if urgency == "high":
                urgency_factor = 2.0  # Prioritize speed
            elif urgency == "medium":
                urgency_factor = 1.5
            else:  # low
                urgency_factor = 1.0
            
            # Calculate weighted score
            if urgency == "high":
                # Prioritize lead time and reliability for high urgency
                weighted_score = (lead_time_score * 0.4 + reliability_score * 0.4 + cost_score * 0.2) * urgency_factor
            else:
                # Balance all factors for normal urgency
                weighted_score = (cost_score * 0.4 + reliability_score * 0.3 + lead_time_score * 0.3) * urgency_factor
            
            scored_quotes.append((quote, weighted_score))
        
        # Sort by weighted score (higher is better)
        scored_quotes.sort(key=lambda x: x[1], reverse=True)
        
        # Select the best supplier
        best_quote, best_score = scored_quotes[0]
        
        logger.info(f"Selected supplier {best_quote.supplier_id} with score {best_score:.3f}")
        logger.info(f"Cost: ${best_quote.total_cost:.2f}, Lead time: {best_quote.lead_time_days} days, "
                   f"Quality: {best_quote.quality_rating:.1f}")
        
        return best_quote
        
    except Exception as e:
        logger.error(f"Error selecting optimal supplier: {e}")
        return quotes[0] if quotes else None


def process_order_confirmation(quote: SupplierQuote) -> OrderConfirmation:
    """Process order confirmation with the selected supplier."""
    try:
        # Generate order ID
        order_id = f"order_{quote.supplier_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate expected delivery date
        expected_delivery = datetime.utcnow() + timedelta(days=quote.lead_time_days)
        
        # Create order confirmation
        confirmation = OrderConfirmation(
            order_id=order_id,
            supplier_id=quote.supplier_id,
            product_id=quote.product_id,
            quantity=quote.quantity,
            total_cost=quote.total_cost,
            expected_delivery=expected_delivery,
            status="confirmed",
            timestamp=datetime.utcnow(),
            agent_id=agent.address
        )
        
        # Store in agent state
        agent_state["active_orders"][order_id] = confirmation
        
        logger.info(f"Order confirmed: {order_id} with {quote.supplier_id}")
        
        return confirmation
        
    except Exception as e:
        logger.error(f"Error processing order confirmation: {e}")
        raise


def update_supplier_performance(supplier_id: str, performance_score: float):
    """Update supplier performance metrics."""
    try:
        if supplier_id not in agent_state["supplier_performance"]:
            agent_state["supplier_performance"][supplier_id] = {
                "total_orders": 0,
                "successful_orders": 0,
                "avg_lead_time": 0.0,
                "avg_quality_rating": 0.0,
                "performance_score": 0.0
            }
        
        performance_data = agent_state["supplier_performance"][supplier_id]
        performance_data["total_orders"] += 1
        
        if performance_score > 0.8:  # Consider successful if score > 0.8
            performance_data["successful_orders"] += 1
        
        # Update performance score
        success_rate = performance_data["successful_orders"] / performance_data["total_orders"]
        performance_data["performance_score"] = success_rate
        
        # Update MeTTa with performance data
        metta_kg.add_supplier_performance(supplier_id, quote.product_id, performance_score)
        
        logger.info(f"Updated performance for {supplier_id}: {performance_score:.2f}")
        
    except Exception as e:
        logger.error(f"Error updating supplier performance: {e}")


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
                    
                    if message_type == "reorder_request":
                        # Handle reorder request from inventory agent
                        request_data = message_data.get("data", {})
                        product_id = request_data.get("product_id")
                        quantity = request_data.get("quantity")
                        warehouse_id = request_data.get("warehouse_id")
                        urgency = request_data.get("urgency", "medium")
                        
                        ctx.logger.info(f"Processing reorder request for {product_id} x {quantity}")
                        
                        # Get supplier quotes
                        quotes = get_supplier_quotes(product_id, quantity)
                        
                        if quotes:
                            # Select optimal supplier
                            selected_quote = select_optimal_supplier(quotes, urgency)
                            
                            if selected_quote:
                                # Process order confirmation
                                confirmation = process_order_confirmation(selected_quote)
                                
                                # Create order confirmation response
                                confirmation_response = {
                                    "type": "order_confirmation",
                                    "data": {
                                        "order_id": confirmation.order_id,
                                        "supplier_id": confirmation.supplier_id,
                                        "product_id": confirmation.product_id,
                                        "quantity": confirmation.quantity,
                                        "total_cost": confirmation.total_cost,
                                        "expected_delivery": confirmation.expected_delivery.isoformat(),
                                        "status": confirmation.status,
                                        "timestamp": confirmation.timestamp.isoformat(),
                                        "agent_id": agent.address
                                    }
                                }
                                
                                # Send response back to sender
                                response_message = create_text_chat(json.dumps(confirmation_response))
                                await ctx.send(sender, response_message)
                                
                                ctx.logger.info(f"Sent order confirmation to {sender}")
                            else:
                                # Send error response
                                error_response = {
                                    "type": "order_error",
                                    "data": {
                                        "error": "No suitable suppliers found",
                                        "product_id": product_id,
                                        "quantity": quantity,
                                        "timestamp": datetime.utcnow().isoformat()
                                    }
                                }
                                
                                response_message = create_text_chat(json.dumps(error_response))
                                await ctx.send(sender, response_message)
                        else:
                            # Send error response
                            error_response = {
                                "type": "order_error",
                                "data": {
                                    "error": "No suppliers available for this product",
                                    "product_id": product_id,
                                    "quantity": quantity,
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            }
                            
                            response_message = create_text_chat(json.dumps(error_response))
                            await ctx.send(sender, response_message)
                    
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


@agent.on_interval(period=60.0)  # Every minute
async def order_monitoring_cycle(ctx: Context):
    """Periodic order monitoring and status updates."""
    ctx.logger.info("Starting order monitoring cycle")
    
    try:
        # Monitor active orders
        active_order_count = len(agent_state["active_orders"])
        if active_order_count > 0:
            ctx.logger.info(f"Monitoring {active_order_count} active orders")
            
            # Check for completed orders (simplified logic)
            current_time = datetime.utcnow()
            completed_orders = []
            
            for order_id, order in agent_state["active_orders"].items():
                # Check if order is completed (simplified: after expected delivery time)
                if current_time >= order.expected_delivery:
                    completed_orders.append(order_id)
                    
                    # Move to history
                    agent_state["order_history"][order_id] = order
                    
                    # Update supplier performance
                    performance_score = 0.9  # Simulate successful delivery
                    update_supplier_performance(order.supplier_id, performance_score)
                    
                    ctx.logger.info(f"Order {order_id} completed and moved to history")
            
            # Remove completed orders from active
            for order_id in completed_orders:
                del agent_state["active_orders"][order_id]
        
    except Exception as e:
        ctx.logger.error(f"Error in order monitoring cycle: {e}")


@agent.on_interval(period=300.0)  # Every 5 minutes
async def supplier_performance_analysis(ctx: Context):
    """Analyze supplier performance and update MeTTa knowledge graph."""
    try:
        # Analyze supplier performance
        for supplier_id, performance_data in agent_state["supplier_performance"].items():
            if performance_data["total_orders"] > 0:
                success_rate = performance_data["successful_orders"] / performance_data["total_orders"]
                ctx.logger.info(f"Supplier {supplier_id} performance: {success_rate:.2f} success rate")
                
                # Update MeTTa with performance data
                metta_kg.add_supplier_performance(supplier_id, "overall", success_rate)
        
        # Update last analysis timestamp
        agent_state["last_update"] = datetime.utcnow()
        
    except Exception as e:
        ctx.logger.error(f"Error in supplier performance analysis: {e}")


# Include the chat protocol and publish manifest
agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    logger.info(f"Supplier Coordination Agent starting...")
    logger.info(f"Agent address: {agent.address}")
    logger.info(f"Agent name: {agent.name}")
    
    # Start the agent
    agent.run()
