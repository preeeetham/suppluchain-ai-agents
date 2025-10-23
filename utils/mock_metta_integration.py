"""
Mock MeTTa Knowledge Graph integration for testing purposes.
This provides the same interface as the real MeTTa integration but uses in-memory data.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockMeTTaKnowledgeGraph:
    """
    Mock MeTTa Knowledge Graph integration for supply chain data.
    Provides the same interface as the real MeTTa integration but uses in-memory data.
    """
    
    def __init__(self):
        """Initialize mock knowledge graph."""
        self.data = {
            "inventory": [],
            "demand": [],
            "supplier": [],
            "route": []
        }
        self._setup_sample_data()
        logger.info("Mock MeTTa knowledge graph initialized")
    
    def _setup_sample_data(self):
        """Set up sample data for testing."""
        # Expanded inventory data with 5 warehouses and 20 products
        self.data["inventory"] = []
        
        # Generate inventory data for all combinations
        warehouses = ["warehouse-001", "warehouse-002", "warehouse-003", "warehouse-004", "warehouse-005"]
        products = [f"product-{i:03d}" for i in range(1, 21)]  # product-001 to product-020
        
        for warehouse in warehouses:
            for product in products:
                # Generate realistic inventory levels
                base_quantity = 50 + (hash(warehouse + product) % 200)
                reorder_point = base_quantity + 50
                self.data["inventory"].extend([
                    (warehouse, product, base_quantity, "2024-01-15T10:00:00Z"),
                    (product, "reorder-point", reorder_point)
                ])
        
        # Expanded demand data for all products
        self.data["demand"] = []
        months = ["2023-10", "2023-11", "2023-12", "2024-01", "2024-02", "2024-03"]
        
        for product in products:
            for month in months:
                # Generate realistic demand patterns
                base_demand = 100 + (hash(product + month) % 500)
                seasonal_factor = 1.0 + 0.3 * (hash(month) % 3 - 1)  # -0.3 to +0.3
                demand = int(base_demand * seasonal_factor)
                self.data["demand"].append((product, month, demand))
            
            # Add seasonal factors for each product
            quarter = "Q4" if "12" in months[-1] else "Q1"
            seasonal_factor = 1.0 + 0.2 * (hash(product) % 3)  # 1.0 to 1.6
            self.data["demand"].append((product, "seasonal-factor", quarter, seasonal_factor))
        
        # Expanded supplier data for all products
        self.data["supplier"] = []
        suppliers = [f"supplier-{i:03d}" for i in range(1, 11)]  # supplier-001 to supplier-010
        
        for product in products:
            # Each product has 2-3 suppliers
            num_suppliers = 2 + (hash(product) % 2)  # 2 or 3 suppliers
            selected_suppliers = suppliers[:num_suppliers]
            
            for supplier in selected_suppliers:
                lead_time = 5 + (hash(supplier + product) % 10)  # 5-14 days
                reliability = 0.85 + (hash(supplier) % 15) / 100  # 0.85-0.99
                cost = 10 + (hash(product) % 50) + (hash(supplier) % 20)  # $10-$80
                self.data["supplier"].append((supplier, product, lead_time, reliability, cost))
        
        # Expanded route data for all warehouse-destination combinations
        self.data["route"] = []
        destinations = [f"destination-{chr(65+i)}" for i in range(15)]  # destination-A to destination-O
        
        for warehouse in warehouses:
            for destination in destinations:
                route_id = f"route-{warehouse}-{destination}"
                distance = 10 + (hash(warehouse + destination) % 100)  # 10-110 miles
                delivery_time = 30 + (hash(warehouse + destination) % 120)  # 30-150 minutes
                cost = 5 + (hash(warehouse + destination) % 50)  # $5-$55
                self.data["route"].append((route_id, warehouse, destination, distance, delivery_time, cost))
    
    def query_inventory(self, warehouse_id: str = None, product_id: str = None) -> List[Dict]:
        """Query inventory data from the knowledge graph."""
        try:
            results = []
            for item in self.data["inventory"]:
                if len(item) >= 3:
                    if warehouse_id and product_id:
                        if item[0] == warehouse_id and item[1] == product_id:
                            results.append({
                                'type': 'inventory',
                                'values': list(item)
                            })
                    elif warehouse_id:
                        if item[0] == warehouse_id:
                            results.append({
                                'type': 'inventory',
                                'values': list(item)
                            })
                    elif product_id:
                        if len(item) >= 2 and item[1] == product_id:
                            results.append({
                                'type': 'inventory',
                                'values': list(item)
                            })
                    else:
                        results.append({
                            'type': 'inventory',
                            'values': list(item)
                        })
            
            logger.info(f"Query inventory returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying inventory: {e}")
            return []
    
    def query_demand_patterns(self, product_id: str, period: str = None) -> List[Dict]:
        """Query demand patterns from the knowledge graph."""
        try:
            results = []
            for item in self.data["demand"]:
                if len(item) >= 2 and item[0] == product_id:
                    if period:
                        if len(item) >= 3 and item[1] == period:
                            results.append({
                                'type': 'demand',
                                'values': list(item)
                            })
                    else:
                        results.append({
                            'type': 'demand',
                            'values': list(item)
                        })
            
            logger.info(f"Query demand patterns returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying demand patterns: {e}")
            return []
    
    def query_suppliers(self, product_id: str = None) -> List[Dict]:
        """Query supplier data from the knowledge graph."""
        try:
            results = []
            for item in self.data["supplier"]:
                if len(item) >= 5:
                    if product_id:
                        if item[1] == product_id:
                            results.append({
                                'type': 'supplier',
                                'values': list(item)
                            })
                    else:
                        results.append({
                            'type': 'supplier',
                            'values': list(item)
                        })
            
            logger.info(f"Query suppliers returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying suppliers: {e}")
            return []
    
    def query_routes(self, warehouse_id: str = None) -> List[Dict]:
        """Query route data from the knowledge graph."""
        try:
            results = []
            for item in self.data["route"]:
                if len(item) >= 6:
                    if warehouse_id:
                        if item[1] == warehouse_id:
                            results.append({
                                'type': 'route',
                                'values': list(item)
                            })
                    else:
                        results.append({
                            'type': 'route',
                            'values': list(item)
                        })
            
            logger.info(f"Query routes returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying routes: {e}")
            return []
    
    def add_inventory_update(self, warehouse_id: str, product_id: str, quantity: int):
        """Add inventory update to the knowledge graph."""
        try:
            timestamp = datetime.utcnow().isoformat()
            self.data["inventory"].append((warehouse_id, product_id, quantity, timestamp))
            logger.info(f"Added inventory update: {warehouse_id}, {product_id}, {quantity}")
        except Exception as e:
            logger.error(f"Error adding inventory update: {e}")
    
    def add_demand_forecast(self, product_id: str, period: str, forecast: int, confidence: float):
        """Add demand forecast to the knowledge graph."""
        try:
            self.data["demand"].append((product_id, period, forecast, confidence))
            logger.info(f"Added demand forecast: {product_id}, {period}, {forecast}")
        except Exception as e:
            logger.error(f"Error adding demand forecast: {e}")
    
    def add_supplier_performance(self, supplier_id: str, product_id: str, performance_score: float):
        """Add supplier performance data to the knowledge graph."""
        try:
            self.data["supplier"].append((supplier_id, "performance", product_id, performance_score))
            logger.info(f"Added supplier performance: {supplier_id}, {product_id}, {performance_score}")
        except Exception as e:
            logger.error(f"Error adding supplier performance: {e}")
    
    def add_route_efficiency(self, route_id: str, efficiency_score: float):
        """Add route efficiency data to the knowledge graph."""
        try:
            self.data["route"].append((route_id, "efficiency", efficiency_score))
            logger.info(f"Added route efficiency: {route_id}, {efficiency_score}")
        except Exception as e:
            logger.error(f"Error adding route efficiency: {e}")


# Global mock MeTTa knowledge graph instance
mock_metta_kg = MockMeTTaKnowledgeGraph()


def get_metta_kg() -> MockMeTTaKnowledgeGraph:
    """Get the global mock MeTTa knowledge graph instance."""
    return mock_metta_kg
