"""
Demand Forecasting Agent for the Supply Chain AI Agents system.
Analyzes historical sales patterns and predicts future demand using MeTTa Knowledge Graphs.
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
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
    name="demand_forecasting_agent",
    seed="demand_agent_seed_phrase_here",
    port=8002,
    endpoint="http://localhost:8002/submit",
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
    "forecast_cache": {},
    "historical_data": {},
    "seasonal_factors": {},
    "trend_analysis": {},
    "last_update": datetime.utcnow()
}


def calculate_seasonal_factor(product_id: str, current_quarter: str) -> float:
    """Calculate seasonal factor for a product based on historical data."""
    try:
        # Query MeTTa for seasonal factors
        seasonal_data = metta_kg.query_demand_patterns(product_id)
        
        for item in seasonal_data:
            if len(item.get('values', [])) >= 3:
                if item['values'][1] == "seasonal-factor" and item['values'][2] == current_quarter:
                    return float(item['values'][3])
        
        # Default seasonal factor if no data found
        return 1.0
        
    except Exception as e:
        logger.error(f"Error calculating seasonal factor: {e}")
        return 1.0


def calculate_trend(product_id: str) -> float:
    """Calculate trend factor for a product based on historical sales."""
    try:
        # Query MeTTa for historical sales data
        sales_data = metta_kg.query_demand_patterns(product_id)
        
        monthly_sales = []
        for item in sales_data:
            if len(item.get('values', [])) >= 3:
                try:
                    # Extract month and sales quantity
                    month = item['values'][1]
                    sales = int(item['values'][2])
                    monthly_sales.append((month, sales))
                except (ValueError, IndexError):
                    continue
        
        if len(monthly_sales) < 3:
            return 0.0  # No trend if insufficient data
        
        # Sort by month and calculate trend
        monthly_sales.sort(key=lambda x: x[0])
        sales_values = [sales for _, sales in monthly_sales]
        
        # Simple linear trend calculation
        if len(sales_values) >= 2:
            # Calculate month-over-month growth rate
            growth_rates = []
            for i in range(1, len(sales_values)):
                if sales_values[i-1] > 0:
                    growth_rate = (sales_values[i] - sales_values[i-1]) / sales_values[i-1]
                    growth_rates.append(growth_rate)
            
            if growth_rates:
                avg_growth_rate = statistics.mean(growth_rates)
                return avg_growth_rate
        
        return 0.0
        
    except Exception as e:
        logger.error(f"Error calculating trend: {e}")
        return 0.0


def calculate_base_demand(product_id: str) -> int:
    """Calculate base demand for a product based on historical average."""
    try:
        # Query MeTTa for historical sales data
        sales_data = metta_kg.query_demand_patterns(product_id)
        
        sales_values = []
        for item in sales_data:
            if len(item.get('values', [])) >= 3:
                try:
                    sales = int(item['values'][2])
                    sales_values.append(sales)
                except (ValueError, IndexError):
                    continue
        
        if sales_values:
            # Calculate average monthly demand
            avg_demand = statistics.mean(sales_values)
            return int(avg_demand)
        else:
            # Default base demand if no historical data
            return 100
            
    except Exception as e:
        logger.error(f"Error calculating base demand: {e}")
        return 100


def predict_demand(product_id: str, forecast_period: str) -> Tuple[int, float]:
    """Predict demand for a product over a specified period."""
    try:
        # Get current quarter
        current_month = datetime.utcnow().month
        if current_month in [1, 2, 3]:
            current_quarter = "Q1"
        elif current_month in [4, 5, 6]:
            current_quarter = "Q2"
        elif current_month in [7, 8, 9]:
            current_quarter = "Q3"
        else:
            current_quarter = "Q4"
        
        # Calculate components
        base_demand = calculate_base_demand(product_id)
        seasonal_factor = calculate_seasonal_factor(product_id, current_quarter)
        trend_factor = calculate_trend(product_id)
        
        # Calculate forecast period multiplier
        if forecast_period == "next_7_days":
            period_multiplier = 7 / 30  # Convert to monthly equivalent
        elif forecast_period == "next_30_days":
            period_multiplier = 1.0
        elif forecast_period == "next_90_days":
            period_multiplier = 3.0
        else:
            period_multiplier = 1.0
        
        # Calculate predicted demand
        predicted_demand = int(base_demand * seasonal_factor * (1 + trend_factor) * period_multiplier)
        
        # Calculate confidence score based on data availability
        confidence_score = min(0.9, 0.5 + (len(metta_kg.query_demand_patterns(product_id)) * 0.1))
        
        logger.info(f"Demand forecast for {product_id}: {predicted_demand} (confidence: {confidence_score:.2f})")
        logger.info(f"Base: {base_demand}, Seasonal: {seasonal_factor:.2f}, Trend: {trend_factor:.2f}")
        
        return predicted_demand, confidence_score
        
    except Exception as e:
        logger.error(f"Error predicting demand: {e}")
        return 100, 0.5  # Fallback values


def analyze_market_trends() -> Dict[str, float]:
    """Analyze overall market trends from MeTTa knowledge graph."""
    try:
        # Query all products for trend analysis
        all_products = ["product-123", "product-456", "product-789"]
        market_trends = {}
        
        for product_id in all_products:
            trend = calculate_trend(product_id)
            market_trends[product_id] = trend
        
        # Calculate overall market trend
        if market_trends:
            overall_trend = statistics.mean(market_trends.values())
            market_trends["overall"] = overall_trend
        
        return market_trends
        
    except Exception as e:
        logger.error(f"Error analyzing market trends: {e}")
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
                    
                    if message_type == "demand_forecast_request":
                        # Handle demand forecast request
                        request_data = message_data.get("data", {})
                        product_id = request_data.get("product_id")
                        forecast_period = request_data.get("forecast_period", "next_30_days")
                        
                        ctx.logger.info(f"Processing demand forecast request for {product_id}")
                        
                        # Generate demand forecast
                        predicted_demand, confidence_score = predict_demand(product_id, forecast_period)
                        
                        # Create demand forecast response
                        forecast_response = {
                            "type": "demand_forecast_response",
                            "data": {
                                "product_id": product_id,
                                "forecast_period": forecast_period,
                                "predicted_demand": predicted_demand,
                                "confidence_score": confidence_score,
                                "seasonal_factor": calculate_seasonal_factor(product_id, "Q4"),
                                "trend_factor": calculate_trend(product_id),
                                "timestamp": datetime.utcnow().isoformat(),
                                "agent_id": agent.address
                            }
                        }
                        
                        # Send response back to sender
                        response_message = create_text_chat(json.dumps(forecast_response))
                        await ctx.send(sender, response_message)
                        
                        # Update MeTTa with forecast data
                        metta_kg.add_demand_forecast(product_id, forecast_period, predicted_demand, confidence_score)
                        
                        ctx.logger.info(f"Sent demand forecast response to {sender}")
                    
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


async def report_activity(activity_type: str, details: Dict):
    """Report agent activity to backend"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{BACKEND_API_URL}/api/agents/report-activity",
                json={
                    "agent_id": "demand",
                    "activity_type": activity_type,
                    "details": details,
                    "timestamp": datetime.utcnow().isoformat()
                },
                timeout=2.0
            )
    except Exception as e:
        logger.debug(f"Could not report activity to backend: {e}")

@agent.on_interval(period=60.0)  # Every minute
async def demand_analysis_cycle(ctx: Context):
    """Periodic demand analysis and trend monitoring."""
    ctx.logger.info("Starting demand analysis cycle")
    
    try:
        # Analyze market trends
        market_trends = analyze_market_trends()
        
        if market_trends:
            ctx.logger.info(f"Market trends analysis: {market_trends}")
            
            # Update agent state
            agent_state["trend_analysis"] = market_trends
            agent_state["last_update"] = datetime.utcnow()
            
            # Log significant trends
            for product_id, trend in market_trends.items():
                if product_id != "overall" and abs(trend) > 0.1:  # 10% change threshold
                    trend_direction = "increasing" if trend > 0 else "decreasing"
                    ctx.logger.info(f"Significant trend detected for {product_id}: {trend_direction} by {abs(trend)*100:.1f}%")
            
            # Report activity
            await report_activity("demand_analysis", {
                "market_trends": market_trends,
                "significant_trends": {k: v for k, v in market_trends.items() if k != "overall" and abs(v) > 0.1}
            })
        
    except Exception as e:
        ctx.logger.error(f"Error in demand analysis cycle: {e}")


@agent.on_interval(period=300.0)  # Every 5 minutes
async def forecast_cache_update(ctx: Context):
    """Update forecast cache with fresh predictions."""
    try:
        # Generate forecasts for all products
        products = ["product-123", "product-456", "product-789"]
        
        for product_id in products:
            predicted_demand, confidence_score = predict_demand(product_id, "next_30_days")
            
            # Update cache
            agent_state["forecast_cache"][product_id] = {
                "predicted_demand": predicted_demand,
                "confidence_score": confidence_score,
                "timestamp": datetime.utcnow()
            }
        
        ctx.logger.info("Updated demand forecast cache")
        
    except Exception as e:
        ctx.logger.error(f"Error updating forecast cache: {e}")


@agent.on_interval(period=3600.0)  # Every hour
async def historical_data_analysis(ctx: Context):
    """Analyze historical data patterns and update MeTTa knowledge graph."""
    try:
        # Analyze seasonal patterns
        products = ["product-123", "product-456", "product-789"]
        quarters = ["Q1", "Q2", "Q3", "Q4"]
        
        for product_id in products:
            seasonal_analysis = {}
            
            for quarter in quarters:
                seasonal_factor = calculate_seasonal_factor(product_id, quarter)
                seasonal_analysis[quarter] = seasonal_factor
            
            # Update MeTTa with seasonal analysis
            for quarter, factor in seasonal_analysis.items():
                metta_kg.add_demand_forecast(f"{product_id}_seasonal_{quarter}", quarter, int(factor * 100), 0.8)
            
            ctx.logger.info(f"Updated seasonal analysis for {product_id}: {seasonal_analysis}")
        
    except Exception as e:
        ctx.logger.error(f"Error in historical data analysis: {e}")


# Include the chat protocol and publish manifest
agent.include(chat_proto, publish_manifest=True)


async def register_with_backend():
    """Register this agent with the backend API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_API_URL}/api/agents/register",
                json={
                    "agent_id": "demand",
                    "agent_address": str(agent.address),
                    "agent_name": agent.name,
                    "port": 8002,
                    "endpoint": "http://localhost:8002/submit"
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
    logger.info(f"Demand Forecasting Agent starting...")
    logger.info(f"Agent address: {agent.address}")
    logger.info(f"Agent name: {agent.name}")
    
    # Register with backend
    asyncio.run(register_with_backend())
    
    # Start the agent
    agent.run()
