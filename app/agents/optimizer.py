"""
Agent 3: Optimizer
Responsibility: Multi-objective optimization for rail selection
"""

import time
from typing import Dict, Tuple

class OptimizerAgent:
    """Selects optimal payment rail using ML-based optimization"""
    
    def __init__(self):
        # Optimization weights
        self.weights = {
            "cost": 0.40,
            "speed": 0.30,
            "success_probability": 0.20,
            "compliance_risk": 0.10
        }
    
    def optimize_route(self, state: Dict) -> Dict:
        """
        Optimize payment routing using multi-objective optimization
        
        Returns:
            Dict with selected rail and optimization reasoning
        """
        print("\n[Agent 3: Optimizer] Starting route optimization...")
        start_time = time.time()
        
        available_rails = state["corridor_metadata"].get("available_rails", [])
        rail_performance = state.get("rail_performance", {})
        predicted_times = state.get("predicted_processing_times", {})
        
        if not available_rails:
            print("  ✗ No available rails for this corridor")
            return {
                "selected_rail": "NONE",
                "backup_rail": "NONE",
                "routing_score": {},
                "optimization_reasoning": "No available payment rails for this corridor"
            }
        
        # Score each rail
        rail_scores = {}
        for rail in available_rails:
            if rail not in rail_performance:
                continue
            
            score = self._calculate_rail_score(
                rail,
                rail_performance[rail],
                predicted_times.get(rail, 24),
                state["amount"],
                state["risk_score"]
            )
            rail_scores[rail] = score
        
        # Select best rail and backup
        sorted_rails = sorted(rail_scores.items(), key=lambda x: x[1]["total_score"], reverse=True)
        
        if not sorted_rails:
            return {
                "selected_rail": "NONE",
                "backup_rail": "NONE",
                "routing_score": {},
                "optimization_reasoning": "No suitable rails found"
            }
        
        selected_rail = sorted_rails[0][0]
        selected_score = sorted_rails[0][1]
        
        backup_rail = sorted_rails[1][0] if len(sorted_rails) > 1 else "NONE"
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            selected_rail,
            selected_score,
            state["amount"],
            predicted_times.get(selected_rail, 24)
        )
        
        optimization_time = time.time() - start_time
        
        print(f"  ✓ Evaluated {len(rail_scores)} rails")
        print(f"  ✓ Selected: {selected_rail} (Score: {selected_score['total_score']:.3f})")
        print(f"  ✓ Backup: {backup_rail}")
        print(f"  ✓ Optimization completed in {optimization_time:.3f}s")
        
        return {
            "selected_rail": selected_rail,
            "backup_rail": backup_rail,
            "routing_score": rail_scores,
            "optimization_reasoning": reasoning
        }
    
    def _calculate_rail_score(
        self,
        rail_name: str,
        performance: Dict,
        predicted_time: float,
        amount: float,
        risk_score: float
    ) -> Dict:
        """
        Calculate multi-objective score for a rail
        
        ML Model in production: TensorFlow model trained on historical data
        """
        # 1. Cost score (normalized, inverse - lower cost is better)
        cost = performance["avg_cost_usd"]
        # Normalize cost: $5-$50 range
        cost_score = 1 - ((cost - 5) / 45) if cost <= 50 else 0
        cost_score = max(0, min(1, cost_score))
        
        # 2. Speed score (normalized, inverse - lower time is better)
        processing_hours = predicted_time
        # Normalize time: 1-48 hours range
        speed_score = 1 - ((processing_hours - 1) / 47) if processing_hours <= 48 else 0
        speed_score = max(0, min(1, speed_score))
        
        # 3. Success probability score
        success_rate = performance["success_rate"]
        availability = performance["availability"]
        success_score = (success_rate + availability) / 2
        
        # 4. Compliance risk score (inverse - lower risk is better)
        compliance_score = 1 - risk_score
        
        # Apply business rules
        # High-value transactions prefer SWIFT GPI for tracking
        if amount > 100000 and rail_name == "SWIFT_GPI":
            success_score *= 1.2
        
        # Penalize rails with high load
        if performance.get("current_load") == "HIGH":
            speed_score *= 0.7
            success_score *= 0.9
        
        # Calculate weighted total score
        total_score = (
            cost_score * self.weights["cost"] +
            speed_score * self.weights["speed"] +
            success_score * self.weights["success_probability"] +
            compliance_score * self.weights["compliance_risk"]
        )
        
        return {
            "total_score": total_score,
            "cost_score": cost_score,
            "speed_score": speed_score,
            "success_score": success_score,
            "compliance_score": compliance_score,
            "breakdown": {
                "cost_usd": cost,
                "processing_hours": processing_hours,
                "success_rate": success_rate,
                "availability": availability
            }
        }
    
    def _generate_reasoning(
        self,
        rail: str,
        score: Dict,
        amount: float,
        predicted_time: float
    ) -> str:
        """Generate human-readable optimization reasoning"""
        reasons = []
        
        # Identify dominant factors
        scores_dict = {
            "cost efficiency": score["cost_score"],
            "speed": score["speed_score"],
            "reliability": score["success_score"],
            "compliance": score["compliance_score"]
        }
        
        top_factor = max(scores_dict.items(), key=lambda x: x[1])
        
        reasons.append(f"Selected {rail} based on optimal {top_factor[0]}")
        
        if score["cost_score"] > 0.8:
            reasons.append(f"Low transaction cost (${score['breakdown']['cost_usd']:.2f})")
        
        if score["speed_score"] > 0.8:
            reasons.append(f"Fast processing ({score['breakdown']['processing_hours']:.1f} hours)")
        
        if score["success_score"] > 0.95:
            reasons.append(f"High reliability ({score['breakdown']['success_rate']*100:.1f}% success rate)")
        
        if amount > 100000:
            reasons.append("High-value transaction requires enhanced tracking")
        
        return "; ".join(reasons)
