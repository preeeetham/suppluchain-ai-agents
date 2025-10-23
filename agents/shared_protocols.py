"""
Shared protocols and message types for the Supply Chain AI Agents system.
This module defines the communication protocols used between agents.
"""

from datetime import datetime
from uuid import uuid4
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)


@dataclass
class InventoryUpdate:
    """Message for inventory updates between agents."""
    warehouse_id: str
    product_id: str
    quantity: int
    timestamp: datetime
    agent_id: str


@dataclass
class DemandForecast:
    """Message for demand forecasting between agents."""
    product_id: str
    forecast_period: str  # e.g., "next_7_days", "next_30_days"
    predicted_demand: int
    confidence_score: float
    seasonal_factor: float
    timestamp: datetime
    agent_id: str


@dataclass
class ReorderRequest:
    """Message for reorder requests from Inventory to Supplier agents."""
    product_id: str
    quantity: int
    warehouse_id: str
    urgency: str  # "low", "medium", "high"
    preferred_suppliers: List[str]
    timestamp: datetime
    agent_id: str


@dataclass
class SupplierQuote:
    """Message for supplier quotes and responses."""
    supplier_id: str
    product_id: str
    quantity: int
    unit_price: float
    total_cost: float
    lead_time_days: int
    availability: bool
    quality_rating: float
    timestamp: datetime
    agent_id: str


@dataclass
class RouteOptimization:
    """Message for route optimization requests and responses."""
    warehouse_id: str
    destinations: List[str]
    vehicle_capacity: int
    priority: str  # "time", "cost", "distance"
    constraints: Dict[str, Any]
    timestamp: datetime
    agent_id: str


@dataclass
class RouteSolution:
    """Message for route optimization solutions."""
    route_id: str
    optimized_route: List[str]
    total_distance: float
    estimated_time: float
    total_cost: float
    efficiency_score: float
    timestamp: datetime
    agent_id: str


@dataclass
class OrderConfirmation:
    """Message for order confirmations."""
    order_id: str
    supplier_id: str
    product_id: str
    quantity: int
    total_cost: float
    expected_delivery: datetime
    status: str  # "confirmed", "processing", "shipped", "delivered"
    timestamp: datetime
    agent_id: str


# Protocol definitions for agent communication
class InventoryProtocol:
    """Protocol for inventory-related communications."""
    pass


class DemandProtocol:
    """Protocol for demand forecasting communications."""
    pass


class RouteProtocol:
    """Protocol for route optimization communications."""
    pass


class SupplierProtocol:
    """Protocol for supplier coordination communications."""
    pass


def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    """Utility function to wrap plain text into a ChatMessage."""
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent())
    else:
        content.append(StartSessionContent())
    
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=content,
    )


def create_acknowledgement(acknowledged_msg_id: str) -> ChatAcknowledgement:
    """Create an acknowledgement message."""
    return ChatAcknowledgement(
        timestamp=datetime.utcnow(),
        acknowledged_msg_id=acknowledged_msg_id
    )


def serialize_message(message: Any) -> str:
    """Serialize a message object to JSON string."""
    import json
    from dataclasses import asdict
    
    if hasattr(message, '__dict__'):
        return json.dumps(asdict(message), default=str)
    return json.dumps(message, default=str)


def deserialize_message(json_str: str, message_type: type) -> Any:
    """Deserialize a JSON string to a message object."""
    import json
    
    data = json.loads(json_str)
    return message_type(**data)


# Agent addresses and identifiers
AGENT_ADDRESSES = {
    "inventory": "inventory_agent_0x1234",
    "demand": "demand_agent_0x5678", 
    "route": "route_agent_0x9abc",
    "supplier": "supplier_agent_0xdef0"
}

# Message types for protocol handling
MESSAGE_TYPES = {
    "inventory_update": InventoryUpdate,
    "demand_forecast": DemandForecast,
    "reorder_request": ReorderRequest,
    "supplier_quote": SupplierQuote,
    "route_optimization": RouteOptimization,
    "route_solution": RouteSolution,
    "order_confirmation": OrderConfirmation
}
