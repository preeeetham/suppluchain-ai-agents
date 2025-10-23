"""
Route Optimization Agent for the Supply Chain AI Agents system.
Optimizes delivery routes, calculates delivery times, and minimizes logistics costs.
"""

import asyncio
import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

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
    RouteOptimization,
    RouteSolution,
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
    name="route_optimization_agent",
    seed="route_agent_seed_phrase_here",
    port=8003,
    endpoint="http://localhost:8003/submit",
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
        "warehouse-001": {"location": "New York", "coordinates": (40.7128, -74.0060)},
        "warehouse-002": {"location": "Los Angeles", "coordinates": (34.0522, -118.2437)},
    },
    "vehicles": {
        "vehicle-001": {"capacity": 1000, "fuel_efficiency": 8.5, "cost_per_mile": 0.5},
        "vehicle-002": {"capacity": 1500, "fuel_efficiency": 6.2, "cost_per_mile": 0.7},
    },
    "active_routes": {},
    "route_history": {},
    "last_optimization": datetime.utcnow()
}


@dataclass
class DeliveryPoint:
    """Represents a delivery point with coordinates and requirements."""
    id: str
    coordinates: Tuple[float, float]
    demand: int
    priority: str
    time_window: Tuple[datetime, datetime]


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculate distance between two points using Haversine formula."""
    lat1, lon1 = point1
    lat2, lon2 = point2
    
    # Haversine formula
    R = 3959  # Earth's radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return distance


def nearest_neighbor_algorithm(warehouse_coords: Tuple[float, float], 
                              delivery_points: List[DeliveryPoint]) -> List[str]:
    """Implement nearest neighbor algorithm for route optimization."""
    if not delivery_points:
        return []
    
    # Start from warehouse
    current_point = warehouse_coords
    unvisited = delivery_points.copy()
    route = []
    
    while unvisited:
        # Find nearest unvisited point
        nearest_point = min(unvisited, 
                           key=lambda p: calculate_distance(current_point, p.coordinates))
        
        # Add to route
        route.append(nearest_point.id)
        current_point = nearest_point.coordinates
        unvisited.remove(nearest_point)
    
    return route


def calculate_route_efficiency(route: List[str], warehouse_coords: Tuple[float, float],
                             delivery_points: List[DeliveryPoint]) -> float:
    """Calculate efficiency score for a route."""
    if not route:
        return 0.0
    
    try:
        # Calculate total distance
        total_distance = 0.0
        current_coords = warehouse_coords
        
        for point_id in route:
            point = next((p for p in delivery_points if p.id == point_id), None)
            if point:
                distance = calculate_distance(current_coords, point.coordinates)
                total_distance += distance
                current_coords = point.coordinates
        
        # Calculate efficiency (lower distance = higher efficiency)
        max_possible_distance = total_distance * 2  # Theoretical maximum
        efficiency = max(0.0, 1.0 - (total_distance / max_possible_distance))
        
        return efficiency
        
    except Exception as e:
        logger.error(f"Error calculating route efficiency: {e}")
        return 0.0


def optimize_route(warehouse_id: str, destinations: List[str], 
                 vehicle_capacity: int, priority: str) -> RouteSolution:
    """Optimize delivery route for given destinations."""
    try:
        # Get warehouse coordinates
        warehouse_coords = agent_state["warehouses"][warehouse_id]["coordinates"]
        
        # Create delivery points (simplified for demo)
        delivery_points = []
        for i, dest_id in enumerate(destinations):
            # Generate sample coordinates (in real system, these would come from database)
            lat = 40.7128 + (i * 0.1)  # Sample coordinates
            lon = -74.0060 + (i * 0.1)
            delivery_points.append(DeliveryPoint(
                id=dest_id,
                coordinates=(lat, lon),
                demand=100 + (i * 50),  # Sample demand
                priority="medium",
                time_window=(datetime.utcnow(), datetime.utcnow() + timedelta(hours=8))
            ))
        
        # Apply optimization algorithm
        if priority == "distance":
            optimized_route = nearest_neighbor_algorithm(warehouse_coords, delivery_points)
        else:
            # Default to nearest neighbor
            optimized_route = nearest_neighbor_algorithm(warehouse_coords, delivery_points)
        
        # Calculate route metrics
        total_distance = 0.0
        current_coords = warehouse_coords
        
        for point_id in optimized_route:
            point = next((p for p in delivery_points if p.id == point_id), None)
            if point:
                distance = calculate_distance(current_coords, point.coordinates)
                total_distance += distance
                current_coords = point.coordinates
        
        # Calculate delivery time (assuming 30 mph average speed)
        estimated_time = total_distance / 30.0  # hours
        
        # Calculate cost
        cost_per_mile = 0.5  # Default cost per mile
        total_cost = total_distance * cost_per_mile
        
        # Calculate efficiency
        efficiency_score = calculate_route_efficiency(optimized_route, warehouse_coords, delivery_points)
        
        # Create route solution
        route_solution = RouteSolution(
            route_id=f"route_{warehouse_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            optimized_route=optimized_route,
            total_distance=total_distance,
            estimated_time=estimated_time,
            total_cost=total_cost,
            efficiency_score=efficiency_score,
            timestamp=datetime.utcnow(),
            agent_id=agent.address
        )
        
        logger.info(f"Optimized route for {warehouse_id}: {len(optimized_route)} stops, "
                   f"{total_distance:.2f} miles, {estimated_time:.2f} hours")
        
        return route_solution
        
    except Exception as e:
        logger.error(f"Error optimizing route: {e}")
        # Return empty solution on error
        return RouteSolution(
            route_id="error_route",
            optimized_route=[],
            total_distance=0.0,
            estimated_time=0.0,
            total_cost=0.0,
            efficiency_score=0.0,
            timestamp=datetime.utcnow(),
            agent_id=agent.address
        )


def analyze_traffic_patterns(warehouse_id: str) -> Dict[str, str]:
    """Analyze traffic patterns for a warehouse location."""
    try:
        # Query MeTTa for traffic patterns
        traffic_data = metta_kg.query_routes(warehouse_id)
        
        traffic_patterns = {}
        for item in traffic_data:
            if len(item.get('values', [])) >= 3:
                if item['values'][1] == "traffic-pattern":
                    time_period = item['values'][2]
                    traffic_level = item['values'][3]
                    traffic_patterns[time_period] = traffic_level
        
        return traffic_patterns
        
    except Exception as e:
        logger.error(f"Error analyzing traffic patterns: {e}")
        return {}


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
                    
                    if message_type == "route_optimization_request":
                        # Handle route optimization request
                        request_data = message_data.get("data", {})
                        warehouse_id = request_data.get("warehouse_id")
                        destinations = request_data.get("destinations", [])
                        vehicle_capacity = request_data.get("vehicle_capacity", 1000)
                        priority = request_data.get("priority", "distance")
                        
                        ctx.logger.info(f"Processing route optimization request for {warehouse_id}")
                        
                        # Optimize route
                        route_solution = optimize_route(warehouse_id, destinations, vehicle_capacity, priority)
                        
                        # Create route solution response
                        solution_response = {
                            "type": "route_solution",
                            "data": {
                                "route_id": route_solution.route_id,
                                "optimized_route": route_solution.optimized_route,
                                "total_distance": route_solution.total_distance,
                                "estimated_time": route_solution.estimated_time,
                                "total_cost": route_solution.total_cost,
                                "efficiency_score": route_solution.efficiency_score,
                                "timestamp": route_solution.timestamp.isoformat(),
                                "agent_id": agent.address
                            }
                        }
                        
                        # Send response back to sender
                        response_message = create_text_chat(json.dumps(solution_response))
                        await ctx.send(sender, response_message)
                        
                        # Update MeTTa with route data
                        metta_kg.add_route_efficiency(route_solution.route_id, route_solution.efficiency_score)
                        
                        # Store in agent state
                        agent_state["active_routes"][route_solution.route_id] = route_solution
                        
                        ctx.logger.info(f"Sent route solution to {sender}")
                    
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


@agent.on_interval(period=120.0)  # Every 2 minutes
async def route_monitoring_cycle(ctx: Context):
    """Periodic route monitoring and optimization."""
    ctx.logger.info("Starting route monitoring cycle")
    
    try:
        # Analyze traffic patterns for all warehouses
        for warehouse_id in agent_state["warehouses"]:
            traffic_patterns = analyze_traffic_patterns(warehouse_id)
            
            if traffic_patterns:
                ctx.logger.info(f"Traffic patterns for {warehouse_id}: {traffic_patterns}")
                
                # Update agent state with traffic information
                agent_state["warehouses"][warehouse_id]["traffic_patterns"] = traffic_patterns
        
        # Monitor active routes
        active_route_count = len(agent_state["active_routes"])
        if active_route_count > 0:
            ctx.logger.info(f"Monitoring {active_route_count} active routes")
            
            # Move completed routes to history
            current_time = datetime.utcnow()
            completed_routes = []
            
            for route_id, route_solution in agent_state["active_routes"].items():
                # Check if route is completed (simplified logic)
                if (current_time - route_solution.timestamp).total_seconds() > 3600:  # 1 hour
                    completed_routes.append(route_id)
                    agent_state["route_history"][route_id] = route_solution
            
            # Remove completed routes from active
            for route_id in completed_routes:
                del agent_state["active_routes"][route_id]
                ctx.logger.info(f"Moved route {route_id} to history")
        
    except Exception as e:
        ctx.logger.error(f"Error in route monitoring cycle: {e}")


@agent.on_interval(period=600.0)  # Every 10 minutes
async def route_efficiency_analysis(ctx: Context):
    """Analyze route efficiency and update MeTTa knowledge graph."""
    try:
        # Analyze route history for efficiency patterns
        if agent_state["route_history"]:
            efficiency_scores = []
            for route_id, route_solution in agent_state["route_history"].items():
                efficiency_scores.append(route_solution.efficiency_score)
            
            if efficiency_scores:
                avg_efficiency = sum(efficiency_scores) / len(efficiency_scores)
                ctx.logger.info(f"Average route efficiency: {avg_efficiency:.2f}")
                
                # Update MeTTa with efficiency analysis
                metta_kg.add_route_efficiency("overall_efficiency", avg_efficiency)
        
        # Update last optimization timestamp
        agent_state["last_optimization"] = datetime.utcnow()
        
    except Exception as e:
        ctx.logger.error(f"Error in route efficiency analysis: {e}")


# Include the chat protocol and publish manifest
agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    logger.info(f"Route Optimization Agent starting...")
    logger.info(f"Agent address: {agent.address}")
    logger.info(f"Agent name: {agent.name}")
    
    # Start the agent
    agent.run()
