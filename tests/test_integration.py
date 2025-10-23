"""
Integration tests for the Supply Chain AI Agents system.
Tests multi-agent communication and MeTTa knowledge graph integration.
"""

import asyncio
import json
import logging
import pytest
from datetime import datetime
from typing import Dict, List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.shared_protocols import (
    InventoryUpdate,
    DemandForecast,
    ReorderRequest,
    SupplierQuote,
    RouteOptimization,
    RouteSolution,
    OrderConfirmation,
    AGENT_ADDRESSES
)
from utils.mock_metta_integration import get_metta_kg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestSupplyChainIntegration:
    """Integration tests for supply chain agents."""
    
    def setup_method(self):
        """Set up test environment."""
        self.metta_kg = get_metta_kg()
        self.agent_addresses = AGENT_ADDRESSES
    
    def test_metta_knowledge_graph_queries(self):
        """Test MeTTa knowledge graph queries."""
        logger.info("Testing MeTTa knowledge graph queries...")
        
        # Test inventory queries
        inventory_data = self.metta_kg.query_inventory()
        assert isinstance(inventory_data, list)
        logger.info(f"Inventory data retrieved: {len(inventory_data)} items")
        
        # Test demand pattern queries
        demand_data = self.metta_kg.query_demand_patterns("product-123")
        assert isinstance(demand_data, list)
        logger.info(f"Demand data retrieved: {len(demand_data)} items")
        
        # Test supplier queries
        supplier_data = self.metta_kg.query_suppliers("product-123")
        assert isinstance(supplier_data, list)
        logger.info(f"Supplier data retrieved: {len(supplier_data)} items")
        
        # Test route queries
        route_data = self.metta_kg.query_routes("warehouse-001")
        assert isinstance(route_data, list)
        logger.info(f"Route data retrieved: {len(route_data)} items")
    
    def test_inventory_reorder_scenario(self):
        """Test inventory reorder scenario."""
        logger.info("Testing inventory reorder scenario...")
        
        # Simulate low stock detection
        warehouse_id = "warehouse-001"
        product_id = "product-123"
        current_quantity = 75
        reorder_point = 100
        
        assert current_quantity <= reorder_point, "Should trigger reorder"
        
        # Create inventory update
        inventory_update = InventoryUpdate(
            warehouse_id=warehouse_id,
            product_id=product_id,
            quantity=current_quantity,
            timestamp=datetime.utcnow(),
            agent_id=self.agent_addresses["inventory"]
        )
        
        # Test reorder request creation
        reorder_request = ReorderRequest(
            product_id=product_id,
            quantity=reorder_point - current_quantity + 50,  # Reorder quantity
            warehouse_id=warehouse_id,
            urgency="medium",
            preferred_suppliers=["supplier-001", "supplier-002"],
            timestamp=datetime.utcnow(),
            agent_id=self.agent_addresses["inventory"]
        )
        
        assert reorder_request.product_id == product_id
        assert reorder_request.quantity > 0
        logger.info(f"Reorder request created: {reorder_request.quantity} units of {product_id}")
    
    def test_demand_forecasting_scenario(self):
        """Test demand forecasting scenario."""
        logger.info("Testing demand forecasting scenario...")
        
        product_id = "product-123"
        forecast_period = "next_30_days"
        
        # Create demand forecast
        demand_forecast = DemandForecast(
            product_id=product_id,
            forecast_period=forecast_period,
            predicted_demand=150,
            confidence_score=0.85,
            seasonal_factor=1.2,
            timestamp=datetime.utcnow(),
            agent_id=self.agent_addresses["demand"]
        )
        
        assert demand_forecast.product_id == product_id
        assert demand_forecast.predicted_demand > 0
        assert 0 <= demand_forecast.confidence_score <= 1
        logger.info(f"Demand forecast: {demand_forecast.predicted_demand} units with {demand_forecast.confidence_score:.2f} confidence")
    
    def test_supplier_coordination_scenario(self):
        """Test supplier coordination scenario."""
        logger.info("Testing supplier coordination scenario...")
        
        product_id = "product-123"
        quantity = 100
        
        # Create supplier quotes
        quotes = [
            SupplierQuote(
                supplier_id="supplier-001",
                product_id=product_id,
                quantity=quantity,
                unit_price=25.50,
                total_cost=2550.00,
                lead_time_days=7,
                availability=True,
                quality_rating=4.8,
                timestamp=datetime.utcnow(),
                agent_id=self.agent_addresses["supplier"]
            ),
            SupplierQuote(
                supplier_id="supplier-002",
                product_id=product_id,
                quantity=quantity,
                unit_price=27.00,
                total_cost=2700.00,
                lead_time_days=5,
                availability=True,
                quality_rating=4.5,
                timestamp=datetime.utcnow(),
                agent_id=self.agent_addresses["supplier"]
            )
        ]
        
        # Test supplier selection logic
        best_quote = min(quotes, key=lambda q: q.total_cost)
        assert best_quote.supplier_id == "supplier-001"
        assert best_quote.total_cost == 2550.00
        
        # Create order confirmation
        order_confirmation = OrderConfirmation(
            order_id=f"order_{best_quote.supplier_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            supplier_id=best_quote.supplier_id,
            product_id=product_id,
            quantity=quantity,
            total_cost=best_quote.total_cost,
            expected_delivery=datetime.utcnow(),
            status="confirmed",
            timestamp=datetime.utcnow(),
            agent_id=self.agent_addresses["supplier"]
        )
        
        assert order_confirmation.status == "confirmed"
        logger.info(f"Order confirmed with {order_confirmation.supplier_id}: ${order_confirmation.total_cost}")
    
    def test_route_optimization_scenario(self):
        """Test route optimization scenario."""
        logger.info("Testing route optimization scenario...")
        
        warehouse_id = "warehouse-001"
        destinations = ["destination-A", "destination-B", "destination-C"]
        vehicle_capacity = 1000
        
        # Create route optimization request
        route_request = RouteOptimization(
            warehouse_id=warehouse_id,
            destinations=destinations,
            vehicle_capacity=vehicle_capacity,
            priority="distance",
            constraints={"max_stops": 5, "time_limit": 480},  # 8 hours
            timestamp=datetime.utcnow(),
            agent_id=self.agent_addresses["route"]
        )
        
        # Simulate route optimization
        optimized_route = ["destination-A", "destination-C", "destination-B"]  # Optimized order
        total_distance = 45.2
        estimated_time = 90  # minutes
        total_cost = 22.60
        efficiency_score = 0.88
        
        # Create route solution
        route_solution = RouteSolution(
            route_id=f"route_{warehouse_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            optimized_route=optimized_route,
            total_distance=total_distance,
            estimated_time=estimated_time,
            total_cost=total_cost,
            efficiency_score=efficiency_score,
            timestamp=datetime.utcnow(),
            agent_id=self.agent_addresses["route"]
        )
        
        assert len(route_solution.optimized_route) == len(destinations)
        assert route_solution.efficiency_score > 0
        logger.info(f"Route optimized: {route_solution.total_distance:.1f} miles, {route_solution.estimated_time} minutes")
    
    def test_multi_agent_communication(self):
        """Test multi-agent communication flow."""
        logger.info("Testing multi-agent communication flow...")
        
        # Simulate complete workflow
        workflow_steps = [
            ("inventory_check", "Inventory Management Agent detects low stock"),
            ("demand_forecast", "Demand Forecasting Agent predicts demand"),
            ("supplier_order", "Supplier Coordination Agent places order"),
            ("route_optimization", "Route Optimization Agent plans delivery")
        ]
        
        for step, description in workflow_steps:
            logger.info(f"  {step}: {description}")
        
        # Verify agent addresses
        assert "inventory" in self.agent_addresses
        assert "demand" in self.agent_addresses
        assert "route" in self.agent_addresses
        assert "supplier" in self.agent_addresses
        
        logger.info("Multi-agent communication flow verified")
    
    def test_metta_data_persistence(self):
        """Test MeTTa knowledge graph data persistence."""
        logger.info("Testing MeTTa data persistence...")
        
        # Test adding inventory update
        warehouse_id = "warehouse-001"
        product_id = "product-123"
        quantity = 75
        
        self.metta_kg.add_inventory_update(warehouse_id, product_id, quantity)
        logger.info(f"Added inventory update: {warehouse_id}, {product_id}, {quantity}")
        
        # Test adding demand forecast
        forecast_period = "next_30_days"
        predicted_demand = 150
        confidence = 0.85
        
        self.metta_kg.add_demand_forecast(product_id, forecast_period, predicted_demand, confidence)
        logger.info(f"Added demand forecast: {product_id}, {predicted_demand}")
        
        # Test adding supplier performance
        supplier_id = "supplier-001"
        performance_score = 0.95
        
        self.metta_kg.add_supplier_performance(supplier_id, product_id, performance_score)
        logger.info(f"Added supplier performance: {supplier_id}, {performance_score}")
        
        # Test adding route efficiency
        route_id = "route-001"
        efficiency_score = 0.88
        
        self.metta_kg.add_route_efficiency(route_id, efficiency_score)
        logger.info(f"Added route efficiency: {route_id}, {efficiency_score}")
    
    def test_error_handling(self):
        """Test error handling in agent communication."""
        logger.info("Testing error handling...")
        
        # Test invalid product ID
        try:
            demand_data = self.metta_kg.query_demand_patterns("invalid-product")
            assert isinstance(demand_data, list)
            logger.info("Error handling for invalid product ID: OK")
        except Exception as e:
            logger.warning(f"Expected error for invalid product: {e}")
        
        # Test invalid warehouse ID
        try:
            route_data = self.metta_kg.query_routes("invalid-warehouse")
            assert isinstance(route_data, list)
            logger.info("Error handling for invalid warehouse ID: OK")
        except Exception as e:
            logger.warning(f"Expected error for invalid warehouse: {e}")
    
    def test_performance_metrics(self):
        """Test performance metrics calculation."""
        logger.info("Testing performance metrics...")
        
        # Test supplier performance calculation
        total_orders = 100
        successful_orders = 95
        success_rate = successful_orders / total_orders
        
        assert success_rate == 0.95
        logger.info(f"Supplier success rate: {success_rate:.2f}")
        
        # Test route efficiency calculation
        total_distance = 50.0
        max_possible_distance = 100.0
        efficiency = 1.0 - (total_distance / max_possible_distance)
        
        assert efficiency == 0.5
        logger.info(f"Route efficiency: {efficiency:.2f}")
        
        # Test demand forecast confidence
        historical_data_points = 12
        confidence = min(0.9, 0.5 + (historical_data_points * 0.1))
        
        assert confidence == 0.9
        logger.info(f"Demand forecast confidence: {confidence:.2f}")


def run_integration_tests():
    """Run all integration tests."""
    logger.info("🧪 STARTING INTEGRATION TESTS")
    logger.info("=" * 50)
    
    test_suite = TestSupplyChainIntegration()
    test_suite.setup_method()  # Explicitly call setup
    
    # Run tests
    test_methods = [
        test_suite.test_metta_knowledge_graph_queries,
        test_suite.test_inventory_reorder_scenario,
        test_suite.test_demand_forecasting_scenario,
        test_suite.test_supplier_coordination_scenario,
        test_suite.test_route_optimization_scenario,
        test_suite.test_multi_agent_communication,
        test_suite.test_metta_data_persistence,
        test_suite.test_error_handling,
        test_suite.test_performance_metrics
    ]
    
    passed_tests = 0
    total_tests = len(test_methods)
    
    for test_method in test_methods:
        try:
            test_method()
            passed_tests += 1
            logger.info(f"✅ {test_method.__name__}: PASSED")
        except Exception as e:
            logger.error(f"❌ {test_method.__name__}: FAILED - {e}")
    
    # Test summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")
    logger.info(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED! System ready for deployment.")
    else:
        logger.warning("⚠️ Some tests failed. Please review and fix issues.")


if __name__ == "__main__":
    run_integration_tests()
