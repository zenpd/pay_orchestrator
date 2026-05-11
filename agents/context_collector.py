"""
Agent 1: Context Collector
Responsibility: Data aggregation and enrichment
"""

import time
from typing import Dict
from datetime import datetime

class ContextCollectorAgent:
    """Collects and enriches payment context with real-time data"""
    
    def __init__(self):
        # Mock data sources (in production: Redis, Neo4j, TimescaleDB)
        self.fx_rates_cache = self._init_fx_rates()
        self.corridor_metadata = self._init_corridor_metadata()
        self.rail_performance_history = self._init_rail_performance()
    
    def _init_fx_rates(self) -> Dict[str, float]:
        """Initialize FX rates (mock Redis cache)"""
        return {
            "ZAR_USD": 0.054,
            "ZAR_EUR": 0.049,
            "ZAR_GBP": 0.042,
            "USD_ZAR": 18.52,
            "EUR_ZAR": 20.41,
            "GBP_ZAR": 23.81,
            "USD_EUR": 0.91,
            "EUR_USD": 1.10
        }
    
    def _init_corridor_metadata(self) -> Dict:
        """Initialize corridor metadata (mock Neo4j graph)"""
        return {
            "ZA_US": {
                "available_rails": ["SWIFT_GPI", "TAG", "CORRESPONDENT"],
                "compliance_level": "HIGH",
                "average_processing_hours": 24,
                "common_sanctions_issues": False,
                "regulatory_requirements": ["FICA", "SARB_APPROVAL", "FinCEN"],
                "popular_corridors": True
            },
            "ZA_GB": {
                "available_rails": ["SWIFT_GPI", "CORRESPONDENT"],
                "compliance_level": "MEDIUM",
                "average_processing_hours": 12,
                "common_sanctions_issues": False,
                "regulatory_requirements": ["FICA", "SARB_APPROVAL"],
                "popular_corridors": True
            },
            "ZA_ZW": {
                "available_rails": ["TAG", "RTGS"],
                "compliance_level": "HIGH",
                "average_processing_hours": 6,
                "common_sanctions_issues": True,
                "regulatory_requirements": ["FICA", "SARB_APPROVAL", "OFAC_CHECK"],
                "popular_corridors": False
            }
        }
    
    def _init_rail_performance(self) -> Dict:
        """Initialize rail performance metrics (mock TimescaleDB)"""
        return {
            "SWIFT_GPI": {
                "success_rate": 0.98,
                "avg_processing_time_hours": 4,
                "avg_cost_usd": 25.00,
                "availability": 0.995,
                "current_load": "NORMAL"
            },
            "TAG": {
                "success_rate": 0.96,
                "avg_processing_time_hours": 2,
                "avg_cost_usd": 15.00,
                "availability": 0.990,
                "current_load": "NORMAL"
            },
            "BANKSERV": {
                "success_rate": 0.99,
                "avg_processing_time_hours": 24,
                "avg_cost_usd": 5.00,
                "availability": 0.998,
                "current_load": "NORMAL"
            },
            "CORRESPONDENT": {
                "success_rate": 0.94,
                "avg_processing_time_hours": 48,
                "avg_cost_usd": 35.00,
                "availability": 0.980,
                "current_load": "HIGH"
            },
            "RTGS": {
                "success_rate": 0.97,
                "avg_processing_time_hours": 1,
                "avg_cost_usd": 20.00,
                "availability": 0.992,
                "current_load": "NORMAL"
            }
        }
    
    def collect_context(self, state: Dict) -> Dict:
        """
        Collect and enrich payment context
        
        Returns:
            Dict with enriched context data
        """
        print("\n[Agent 1: Context Collector] Starting context enrichment...")
        start_time = time.time()
        
        # Get FX rate
        fx_pair = f"{state['currency_from']}_{state['currency_to']}"
        fx_rate = self._get_fx_rate(fx_pair)
        
        # Get corridor metadata
        corridor_key = f"{state['sender_country']}_{state['receiver_country']}"
        corridor_data = self._get_corridor_metadata(corridor_key)
        
        # Get rail performance for available rails
        rail_performance = self._get_rail_performance(corridor_data.get("available_rails", []))
        
        # Predict processing times
        predicted_times = self._predict_processing_times(
            state['amount'],
            corridor_data,
            rail_performance
        )
        
        enrichment_time = time.time() - start_time
        
        print(f"  ✓ FX Rate: {state['currency_from']}/{state['currency_to']} = {fx_rate}")
        print(f"  ✓ Corridor: {corridor_key}")
        print(f"  ✓ Available Rails: {', '.join(corridor_data.get('available_rails', []))}")
        print(f"  ✓ Enrichment completed in {enrichment_time:.3f}s")
        
        return {
            "fx_rate": fx_rate,
            "corridor_metadata": corridor_data,
            "rail_performance": rail_performance,
            "predicted_processing_times": predicted_times
        }
    
    def _get_fx_rate(self, fx_pair: str) -> float:
        """Get FX rate from cache (mock Redis)"""
        return self.fx_rates_cache.get(fx_pair, 1.0)
    
    def _get_corridor_metadata(self, corridor_key: str) -> Dict:
        """Get corridor metadata from graph (mock Neo4j)"""
        return self.corridor_metadata.get(corridor_key, {
            "available_rails": ["SWIFT_GPI"],
            "compliance_level": "HIGH",
            "average_processing_hours": 24,
            "common_sanctions_issues": False,
            "regulatory_requirements": ["STANDARD_COMPLIANCE"],
            "popular_corridors": False
        })
    
    def _get_rail_performance(self, rail_list: list) -> Dict:
        """Get performance metrics for specific rails"""
        performance = {}
        for rail in rail_list:
            if rail in self.rail_performance_history:
                performance[rail] = self.rail_performance_history[rail]
        return performance
    
    def _predict_processing_times(self, amount: float, corridor_data: Dict, rail_performance: Dict) -> Dict:
        """Predict processing times for each rail using ML models"""
        predictions = {}
        
        # Simple prediction based on historical data + amount factor
        for rail, perf in rail_performance.items():
            base_time = perf["avg_processing_time_hours"]
            
            # High-value payments (+20% time), Low-value payments (-10% time)
            if amount > 100000:
                time_factor = 1.2
            elif amount < 10000:
                time_factor = 0.9
            else:
                time_factor = 1.0
            
            # Popular corridors are faster
            corridor_factor = 0.9 if corridor_data.get("popular_corridors") else 1.1
            
            predicted_time = base_time * time_factor * corridor_factor
            predictions[rail] = round(predicted_time, 2)
        
        return predictions
