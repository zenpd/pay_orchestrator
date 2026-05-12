"""
Agent 5: Feedback
Responsibility: Continuous learning and improvement
"""

import time
from typing import Dict
from datetime import datetime

class FeedbackAgent:
    """Monitors transaction outcomes and enables continuous learning"""
    
    def __init__(self):
        # Training data store (in production: MLflow)
        self.training_examples = []
        
        # Performance metrics
        self.metrics = {
            "total_transactions": 0,
            "successful_transactions": 0,
            "failed_transactions": 0,
            "total_cost": 0.0,
            "total_processing_time": 0.0
        }
    
    def process_feedback(self, state: Dict) -> Dict:
        """
        Process transaction feedback and update models
        
        Returns:
            Dict with actual performance metrics
        """
        print("\n[Agent 5: Feedback] Processing transaction feedback...")
        start_time = time.time()
        
        # Extract actual outcomes
        success = state.get("execution_status") == "SUCCESS"
        selected_rail = state.get("selected_rail")
        execution_time = state.get("execution_time", 0)
        
        # Calculate actual cost
        actual_cost = self._calculate_actual_cost(
            selected_rail,
            state.get("amount", 0),
            state.get("rail_performance", {})
        )
        
        # Calculate actual processing time
        actual_processing_time = self._calculate_actual_processing_time(
            selected_rail,
            state.get("predicted_processing_times", {}),
            success
        )
        
        # Compare predicted vs actual
        performance_delta = self._calculate_performance_delta(state, {
            "actual_cost": actual_cost,
            "actual_processing_time": actual_processing_time,
            "success": success
        })
        
        # Store training example
        training_example = self._create_training_example(state, performance_delta)
        self._store_training_example(training_example)
        
        # Update metrics
        self._update_metrics(success, actual_cost, actual_processing_time)
        
        # Check if model retraining is needed
        retrain_needed = self._check_retraining_trigger()
        
        # Generate feedback notes
        feedback_notes = self._generate_feedback_notes(
            performance_delta,
            retrain_needed
        )
        
        feedback_time = time.time() - start_time
        
        print(f"  ✓ Actual Cost: ${actual_cost:.2f}")
        print(f"  ✓ Actual Processing Time: {actual_processing_time:.2f}h")
        print(f"  ✓ Success: {success}")
        print(f"  ✓ Performance Delta: {performance_delta['cost_delta']:.1f}% cost, {performance_delta['time_delta']:.1f}% time")
        if retrain_needed:
            print(f"  ⚠ Model retraining recommended")
        print(f"  ✓ Feedback processed in {feedback_time:.3f}s")
        
        return {
            "actual_cost": actual_cost,
            "actual_processing_time": actual_processing_time,
            "success": success,
            "feedback_notes": feedback_notes
        }
    
    def _calculate_actual_cost(self, rail: str, amount: float, rail_performance: Dict) -> float:
        """Calculate actual transaction cost"""
        if rail not in rail_performance:
            return 25.0  # Default cost
        
        base_cost = rail_performance[rail].get("avg_cost_usd", 25.0)
        
        # Add variance (+/- 10%)
        import random
        variance = random.uniform(-0.1, 0.1)
        actual_cost = base_cost * (1 + variance)
        
        # High-value surcharge
        if amount > 100000:
            actual_cost += 10.0
        
        return round(actual_cost, 2)
    
    def _calculate_actual_processing_time(
        self,
        rail: str,
        predicted_times: Dict,
        success: bool
    ) -> float:
        """Calculate actual processing time"""
        predicted = predicted_times.get(rail, 24.0)
        
        if not success:
            # Failed transactions take longer
            return predicted * 1.5
        
        # Add realistic variance
        import random
        variance = random.uniform(-0.15, 0.25)
        actual = predicted * (1 + variance)
        
        return round(actual, 2)
    
    def _calculate_performance_delta(self, state: Dict, actual: Dict) -> Dict:
        """Calculate difference between predicted and actual performance"""
        selected_rail = state.get("selected_rail")
        routing_score = state.get("routing_score", {})
        
        if selected_rail not in routing_score:
            return {
                "cost_delta": 0.0,
                "time_delta": 0.0,
                "accuracy": 0.0
            }
        
        predicted_cost = routing_score[selected_rail]["breakdown"]["cost_usd"]
        predicted_time = routing_score[selected_rail]["breakdown"]["processing_hours"]
        predicted_success = routing_score[selected_rail]["breakdown"]["success_rate"]
        
        # Calculate percentage deltas
        cost_delta = ((actual["actual_cost"] - predicted_cost) / predicted_cost) * 100
        time_delta = ((actual["actual_processing_time"] - predicted_time) / predicted_time) * 100
        
        # Success prediction accuracy
        success_delta = abs((1.0 if actual["success"] else 0.0) - predicted_success) * 100
        
        return {
            "cost_delta": round(cost_delta, 1),
            "time_delta": round(time_delta, 1),
            "success_delta": round(success_delta, 1),
            "accuracy": round(100 - ((abs(cost_delta) + abs(time_delta)) / 2), 1)
        }
    
    def _create_training_example(self, state: Dict, performance_delta: Dict) -> Dict:
        """Create labeled training example for model retraining"""
        return {
            "timestamp": datetime.now().isoformat(),
            "features": {
                "amount": state.get("amount"),
                "currency_pair": f"{state.get('currency_from')}_{state.get('currency_to')}",
                "corridor": f"{state.get('sender_country')}_{state.get('receiver_country')}",
                "selected_rail": state.get("selected_rail"),
                "risk_score": state.get("risk_score", 0.0),
                "fx_rate": state.get("fx_rate", 1.0)
            },
            "predictions": {
                "cost": state.get("routing_score", {}).get(state.get("selected_rail"), {}).get("breakdown", {}).get("cost_usd", 0),
                "time": state.get("predicted_processing_times", {}).get(state.get("selected_rail"), 0),
                "success_probability": state.get("routing_score", {}).get(state.get("selected_rail"), {}).get("breakdown", {}).get("success_rate", 0)
            },
            "actuals": {
                "cost": state.get("actual_cost", 0),
                "time": state.get("actual_processing_time", 0),
                "success": state.get("success", False)
            },
            "performance_delta": performance_delta
        }
    
    def _store_training_example(self, example: Dict):
        """Store training example for model retraining (mock MLflow)"""
        self.training_examples.append(example)
        
        # In production: Store in MLflow
        # mlflow.log_metrics({...})
        # mlflow.log_params({...})
    
    def _update_metrics(self, success: bool, cost: float, processing_time: float):
        """Update aggregate performance metrics"""
        self.metrics["total_transactions"] += 1
        
        if success:
            self.metrics["successful_transactions"] += 1
        else:
            self.metrics["failed_transactions"] += 1
        
        self.metrics["total_cost"] += cost
        self.metrics["total_processing_time"] += processing_time
    
    def _check_retraining_trigger(self) -> bool:
        """Check if model retraining should be triggered"""
        # Trigger retraining after N examples
        if len(self.training_examples) >= 100:
            return True
        
        # Trigger if performance degrades significantly
        if len(self.training_examples) > 10:
            recent_examples = self.training_examples[-10:]
            avg_accuracy = sum(ex["performance_delta"]["accuracy"] for ex in recent_examples) / 10
            
            if avg_accuracy < 70:  # Accuracy dropped below 70%
                return True
        
        return False
    
    def _generate_feedback_notes(self, performance_delta: Dict, retrain_needed: bool) -> str:
        """Generate human-readable feedback notes"""
        notes = []
        
        # Cost variance notes
        if abs(performance_delta["cost_delta"]) > 20:
            direction = "higher" if performance_delta["cost_delta"] > 0 else "lower"
            notes.append(f"Actual cost {direction} than predicted by {abs(performance_delta['cost_delta']):.1f}%")
        
        # Time variance notes
        if abs(performance_delta["time_delta"]) > 20:
            direction = "slower" if performance_delta["time_delta"] > 0 else "faster"
            notes.append(f"Processing {direction} than predicted by {abs(performance_delta['time_delta']):.1f}%")
        
        # Accuracy notes
        if performance_delta["accuracy"] > 90:
            notes.append("High prediction accuracy")
        elif performance_delta["accuracy"] < 70:
            notes.append("Low prediction accuracy - model update recommended")
        
        # Retraining recommendation
        if retrain_needed:
            notes.append("Model retraining triggered")
        
        return "; ".join(notes) if notes else "Performance within expected range"
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of performance metrics"""
        if self.metrics["total_transactions"] == 0:
            return self.metrics
        
        return {
            **self.metrics,
            "success_rate": self.metrics["successful_transactions"] / self.metrics["total_transactions"],
            "avg_cost": self.metrics["total_cost"] / self.metrics["total_transactions"],
            "avg_processing_time": self.metrics["total_processing_time"] / self.metrics["total_transactions"]
        }
