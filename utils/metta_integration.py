"""
MeTTa Knowledge Graph integration utilities for the Supply Chain AI Agents system.
This module provides functions to interact with SingularityNET's MeTTa Knowledge Graphs.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from hyperon import MeTTa, Atom, S, E, V, C, G, OperationAtom, GroundedAtom
from hyperon.atoms import OperationAtom, GroundedAtom
from hyperon.base import GroundedAtom, OperationAtom

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MeTTaKnowledgeGraph:
    """
    MeTTa Knowledge Graph integration class for supply chain data.
    Handles inventory, demand patterns, supplier data, and route efficiency.
    """
    
    def __init__(self):
        """Initialize MeTTa knowledge graph."""
        self.metta = MeTTa()
        self._setup_knowledge_graphs()
    
    def _setup_knowledge_graphs(self):
        """Set up the knowledge graph structure with initial data."""
        try:
            # Initialize inventory knowledge graph
            self._setup_inventory_kg()
            # Initialize demand patterns knowledge graph
            self._setup_demand_patterns_kg()
            # Initialize supplier data knowledge graph
            self._setup_supplier_data_kg()
            # Initialize route efficiency knowledge graph
            self._setup_route_efficiency_kg()
            logger.info("MeTTa knowledge graphs initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing MeTTa knowledge graphs: {e}")
            raise
    
    def _setup_inventory_kg(self):
        """Set up inventory knowledge graph with sample data."""
        inventory_data = [
            # Warehouse inventory data: (warehouse-id, product-id, quantity, timestamp)
            ("warehouse-001", "product-123", 150, "2024-01-15T10:00:00Z"),
            ("warehouse-001", "product-456", 75, "2024-01-15T10:00:00Z"),
            ("warehouse-002", "product-123", 200, "2024-01-15T10:00:00Z"),
            ("warehouse-002", "product-789", 50, "2024-01-15T10:00:00Z"),
            
            # Reorder points and buffer stock
            ("product-123", "reorder-point", 100),
            ("product-456", "reorder-point", 50),
            ("product-789", "reorder-point", 75),
            
            # Warehouse capacity and location
            ("warehouse-001", "capacity", 1000),
            ("warehouse-002", "capacity", 1500),
            ("warehouse-001", "location", "New York"),
            ("warehouse-002", "location", "Los Angeles"),
        ]
        
        for data in inventory_data:
            self._add_fact("inventory", data)
    
    def _setup_demand_patterns_kg(self):
        """Set up demand patterns knowledge graph with sample data."""
        demand_data = [
            # Historical sales data: (product-id, month, sales-quantity)
            ("product-123", "2023-10", 1200),
            ("product-123", "2023-11", 1350),
            ("product-123", "2023-12", 1800),  # Holiday season
            ("product-456", "2023-10", 800),
            ("product-456", "2023-11", 900),
            ("product-456", "2023-12", 1100),
            
            # Seasonal factors
            ("product-123", "seasonal-factor", "Q4", 1.5),  # Holiday boost
            ("product-456", "seasonal-factor", "Q4", 1.2),
            ("product-789", "seasonal-factor", "Q4", 1.1),
            
            # Trend analysis
            ("product-123", "trend", "increasing", 0.15),  # 15% monthly growth
            ("product-456", "trend", "stable", 0.02),
            ("product-789", "trend", "decreasing", -0.05),
        ]
        
        for data in demand_data:
            self._add_fact("demand", data)
    
    def _setup_supplier_data_kg(self):
        """Set up supplier data knowledge graph with sample data."""
        supplier_data = [
            # Supplier performance data: (supplier-id, product-id, lead-time, reliability, cost)
            ("supplier-001", "product-123", 7, 0.95, 25.50),
            ("supplier-002", "product-123", 5, 0.90, 27.00),
            ("supplier-001", "product-456", 10, 0.98, 15.75),
            ("supplier-003", "product-456", 8, 0.92, 16.25),
            ("supplier-002", "product-789", 6, 0.88, 35.00),
            ("supplier-003", "product-789", 9, 0.94, 32.50),
            
            # Supplier quality ratings
            ("supplier-001", "quality-rating", 4.8),
            ("supplier-002", "quality-rating", 4.5),
            ("supplier-003", "quality-rating", 4.7),
            
            # Supplier availability
            ("supplier-001", "availability", "product-123", True),
            ("supplier-002", "availability", "product-123", True),
            ("supplier-001", "availability", "product-456", True),
            ("supplier-003", "availability", "product-456", True),
        ]
        
        for data in supplier_data:
            self._add_fact("supplier", data)
    
    def _setup_route_efficiency_kg(self):
        """Set up route efficiency knowledge graph with sample data."""
        route_data = [
            # Route data: (route-id, warehouse-id, destination, distance, time, cost)
            ("route-001", "warehouse-001", "destination-A", 25.5, 45, 12.50),
            ("route-002", "warehouse-001", "destination-B", 18.2, 35, 9.10),
            ("route-003", "warehouse-002", "destination-C", 32.1, 55, 16.05),
            ("route-004", "warehouse-002", "destination-D", 28.7, 50, 14.35),
            
            # Vehicle data
            ("vehicle-001", "capacity", 1000),
            ("vehicle-002", "capacity", 1500),
            ("vehicle-001", "fuel-efficiency", 8.5),  # miles per gallon
            ("vehicle-002", "fuel-efficiency", 6.2),
            
            # Traffic patterns
            ("warehouse-001", "traffic-pattern", "morning", "heavy"),
            ("warehouse-001", "traffic-pattern", "afternoon", "moderate"),
            ("warehouse-002", "traffic-pattern", "morning", "moderate"),
            ("warehouse-002", "traffic-pattern", "afternoon", "heavy"),
        ]
        
        for data in route_data:
            self._add_fact("route", data)
    
    def _add_fact(self, graph_type: str, data: Tuple):
        """Add a fact to the knowledge graph."""
        try:
            # Convert tuple to MeTTa expression
            if len(data) == 2:
                expr = f"({data[0]} {data[1]})"
            elif len(data) == 3:
                expr = f"({data[0]} {data[1]} {data[2]})"
            elif len(data) == 4:
                expr = f"({data[0]} {data[1]} {data[2]} {data[3]})"
            else:
                expr = f"({' '.join(map(str, data))})"
            
            # Add to appropriate knowledge graph
            if graph_type == "inventory":
                self.metta.add_atom(expr)
            elif graph_type == "demand":
                self.metta.add_atom(expr)
            elif graph_type == "supplier":
                self.metta.add_atom(expr)
            elif graph_type == "route":
                self.metta.add_atom(expr)
                
        except Exception as e:
            logger.error(f"Error adding fact to {graph_type} graph: {e}")
    
    def query_inventory(self, warehouse_id: str = None, product_id: str = None) -> List[Dict]:
        """Query inventory data from the knowledge graph."""
        try:
            if warehouse_id and product_id:
                query = f"(inventory {warehouse_id} {product_id} $quantity $timestamp)"
            elif warehouse_id:
                query = f"(inventory {warehouse_id} $product $quantity $timestamp)"
            elif product_id:
                query = f"(inventory $warehouse {product_id} $quantity $timestamp)"
            else:
                query = "(inventory $warehouse $product $quantity $timestamp)"
            
            results = self.metta.query(query)
            return self._parse_query_results(results)
        except Exception as e:
            logger.error(f"Error querying inventory: {e}")
            return []
    
    def query_demand_patterns(self, product_id: str, period: str = None) -> List[Dict]:
        """Query demand patterns from the knowledge graph."""
        try:
            if period:
                query = f"(demand {product_id} {period} $sales)"
            else:
                query = f"(demand {product_id} $period $sales)"
            
            results = self.metta.query(query)
            return self._parse_query_results(results)
        except Exception as e:
            logger.error(f"Error querying demand patterns: {e}")
            return []
    
    def query_suppliers(self, product_id: str = None) -> List[Dict]:
        """Query supplier data from the knowledge graph."""
        try:
            if product_id:
                query = f"(supplier $supplier {product_id} $lead-time $reliability $cost)"
            else:
                query = "(supplier $supplier $product $lead-time $reliability $cost)"
            
            results = self.metta.query(query)
            return self._parse_query_results(results)
        except Exception as e:
            logger.error(f"Error querying suppliers: {e}")
            return []
    
    def query_routes(self, warehouse_id: str = None) -> List[Dict]:
        """Query route data from the knowledge graph."""
        try:
            if warehouse_id:
                query = f"(route $route-id {warehouse_id} $destination $distance $time $cost)"
            else:
                query = "(route $route-id $warehouse $destination $distance $time $cost)"
            
            results = self.metta.query(query)
            return self._parse_query_results(results)
        except Exception as e:
            logger.error(f"Error querying routes: {e}")
            return []
    
    def _parse_query_results(self, results) -> List[Dict]:
        """Parse MeTTa query results into Python dictionaries."""
        parsed_results = []
        try:
            for result in results:
                if hasattr(result, 'get_children'):
                    children = result.get_children()
                    if len(children) >= 2:
                        parsed_results.append({
                            'type': str(children[0]),
                            'values': [str(child) for child in children[1:]]
                        })
        except Exception as e:
            logger.error(f"Error parsing query results: {e}")
        
        return parsed_results
    
    def add_inventory_update(self, warehouse_id: str, product_id: str, quantity: int):
        """Add inventory update to the knowledge graph."""
        timestamp = datetime.utcnow().isoformat()
        self._add_fact("inventory", (warehouse_id, product_id, quantity, timestamp))
        logger.info(f"Added inventory update: {warehouse_id}, {product_id}, {quantity}")
    
    def add_demand_forecast(self, product_id: str, period: str, forecast: int, confidence: float):
        """Add demand forecast to the knowledge graph."""
        self._add_fact("demand", (product_id, period, forecast, confidence))
        logger.info(f"Added demand forecast: {product_id}, {period}, {forecast}")
    
    def add_supplier_performance(self, supplier_id: str, product_id: str, performance_score: float):
        """Add supplier performance data to the knowledge graph."""
        self._add_fact("supplier", (supplier_id, "performance", product_id, performance_score))
        logger.info(f"Added supplier performance: {supplier_id}, {product_id}, {performance_score}")
    
    def add_route_efficiency(self, route_id: str, efficiency_score: float):
        """Add route efficiency data to the knowledge graph."""
        self._add_fact("route", (route_id, "efficiency", efficiency_score))
        logger.info(f"Added route efficiency: {route_id}, {efficiency_score}")


# Global MeTTa knowledge graph instance
metta_kg = MeTTaKnowledgeGraph()


def get_metta_kg() -> MeTTaKnowledgeGraph:
    """Get the global MeTTa knowledge graph instance."""
    return metta_kg
