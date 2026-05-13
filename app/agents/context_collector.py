"""
Context Collector Agent
Responsibility: Gather and contextualize payment information
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

log = logging.getLogger(__name__)


@dataclass
class PaymentContext:
    """Enriched context for payment decision-making."""
    transaction_type: str  # "domestic", "cross_border", "high_value", "urgent"
    is_high_value: bool
    is_urgent: bool
    is_high_risk: bool
    transaction_score: float  # 0-1.0 overall scoring
    corridors_available: List[str]
    rails_scored: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any]


class ContextCollectorAgent:
    """Gathers and contextualizes payment information for decision-making."""
    
    def __init__(self):
        """Initialize context thresholds and categorizations."""
        self.thresholds = {
            "high_value_amount": 100000,      # USD
            "very_high_value": 500000,
            "urgent_hours": 4,
            "standard_hours": 24,
            "high_risk_score": 0.5
        }
        
        self.transaction_types = {
            "domestic": ["same_country"],
            "cross_border": ["different_country"],
            "high_value": ["high_amount"],
            "urgent": ["short_deadline"],
            "compliance_sensitive": ["high_risk_country"]
        }
    
    def collect_and_contextualize(self,
                                 amount: float,
                                 currency: str,
                                 sender_country: str,
                                 receiver_country: str,
                                 corridor: str,
                                 deadline_hours: Optional[float],
                                 available_rails: Dict[str, Dict],
                                 compliance_risk: float,
                                 rail_scores: Optional[Dict] = None) -> PaymentContext:
        """
        Collect and contextualize payment information.
        
        Args:
            amount: Transaction amount
            currency: Currency code
            sender_country: Sender country code
            receiver_country: Receiver country code
            corridor: Payment corridor
            deadline_hours: Time constraint (optional)
            available_rails: Available payment rails
            compliance_risk: Compliance risk score (0-1.0)
            rail_scores: Pre-calculated rail scores (optional)
        
        Returns:
            PaymentContext with enriched information
        """
        
        # Classify transaction
        is_domestic = sender_country == receiver_country
        is_high_value = amount >= self.thresholds["high_value_amount"]
        is_very_high_value = amount >= self.thresholds["very_high_value"]
        is_urgent = deadline_hours and deadline_hours < self.thresholds["urgent_hours"]
        is_high_risk = compliance_risk >= self.thresholds["high_risk_score"]
        
        # Determine transaction type
        transaction_types = []
        if is_domestic:
            transaction_types.append("domestic")
        else:
            transaction_types.append("cross_border")
        
        if is_very_high_value:
            transaction_types.append("very_high_value")
        elif is_high_value:
            transaction_types.append("high_value")
        
        if is_urgent:
            transaction_types.append("urgent")
        
        if is_high_risk:
            transaction_types.append("compliance_sensitive")
        
        # Categorize as single type (priority order)
        transaction_type = transaction_types[0] if transaction_types else "standard"
        
        # Calculate transaction score
        transaction_score = self._calculate_transaction_score(
            amount=amount,
            is_high_value=is_high_value,
            is_urgent=is_urgent,
            is_high_risk=is_high_risk,
            compliance_risk=compliance_risk
        )
        
        # Available corridors
        corridors = [corridor] if corridor else self._infer_corridors(sender_country, receiver_country)
        
        # Score available rails
        rails_scored = rail_scores or self._score_available_rails(available_rails, amount, deadline_hours)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            transaction_type=transaction_type,
            amount=amount,
            deadline_hours=deadline_hours,
            is_high_risk=is_high_risk,
            available_rails=available_rails,
            rails_scored=rails_scored
        )
        
        # Build metadata
        metadata = {
            "payment_value_category": self._categorize_amount(amount),
            "processing_urgency": "urgent" if is_urgent else ("standard" if deadline_hours else "flexible"),
            "compliance_profile": "high_risk" if is_high_risk else "standard",
            "corridor_info": {
                "origin": sender_country,
                "destination": receiver_country,
                "type": "domestic" if is_domestic else "cross_border"
            },
            "deadline_feasibility": self._check_deadline_feasibility(deadline_hours, available_rails)
        }
        
        return PaymentContext(
            transaction_type=transaction_type,
            is_high_value=is_high_value,
            is_urgent=is_urgent or False,
            is_high_risk=is_high_risk,
            transaction_score=transaction_score,
            corridors_available=corridors,
            rails_scored=rails_scored,
            recommendations=recommendations,
            metadata=metadata
        )
    
    def _calculate_transaction_score(self,
                                    amount: float,
                                    is_high_value: bool,
                                    is_urgent: bool,
                                    is_high_risk: bool,
                                    compliance_risk: float) -> float:
        """Calculate overall transaction complexity score (0-1.0)."""
        score = 0.0
        
        # Amount complexity
        if amount >= self.thresholds["very_high_value"]:
            score += 0.25
        elif amount >= self.thresholds["high_value_amount"]:
            score += 0.15
        else:
            score += 0.05
        
        # Time pressure
        if is_urgent:
            score += 0.25
        else:
            score += 0.05
        
        # Compliance complexity
        score += compliance_risk * 0.30
        
        # Cross-border complexity
        # (0.15 added via corridor complexity in caller)
        
        return min(1.0, score)
    
    def _categorize_amount(self, amount: float) -> str:
        """Categorize transaction by amount."""
        if amount >= self.thresholds["very_high_value"]:
            return f"very_high_value (>${self.thresholds['very_high_value']:,.0f})"
        elif amount >= self.thresholds["high_value_amount"]:
            return f"high_value (>${self.thresholds['high_value_amount']:,.0f})"
        elif amount >= 10000:
            return "medium_value"
        else:
            return "standard_value"
    
    def _infer_corridors(self, sender_country: str, receiver_country: str) -> List[str]:
        """Infer payment corridors from countries."""
        corridor = f"{sender_country}_{receiver_country}"
        return [corridor]
    
    def _score_available_rails(self, rails: Dict[str, Dict],
                              amount: float,
                              deadline_hours: Optional[float]) -> Dict[str, Any]:
        """Score available rails with context."""
        scored = {}
        
        for rail_name, rail_data in rails.items():
            min_amount = rail_data.get("min_amount", 0)
            max_amount = rail_data.get("max_amount", float('inf'))
            time_hours = rail_data.get("processing_hours", 24)
            
            # Check eligibility
            eligible = min_amount <= amount <= max_amount
            
            # Check deadline compliance
            deadline_ok = True
            if deadline_hours:
                deadline_ok = time_hours <= deadline_hours
            
            scored[rail_name] = {
                "eligible": eligible,
                "deadline_compliant": deadline_ok,
                "time_hours": time_hours,
                "cost_usd": rail_data.get("cost_usd", 0),
                "success_rate": rail_data.get("success_rate", 0.95),
                "ineligibility_reason": self._get_ineligibility_reason(
                    amount, min_amount, max_amount, time_hours, deadline_hours
                )
            }
        
        return scored
    
    def _get_ineligibility_reason(self, amount: float, min_amt: float,
                                 max_amt: float, time_hours: float,
                                 deadline_hours: Optional[float]) -> Optional[str]:
        """Determine why a rail is ineligible."""
        if amount < min_amt:
            return f"Amount below minimum (${min_amt:,.0f})"
        if amount > max_amt:
            return f"Amount exceeds maximum (${max_amt:,.0f})"
        if deadline_hours and time_hours > deadline_hours:
            return f"Processing time ({time_hours:.1f}h) exceeds deadline ({deadline_hours:.1f}h)"
        return None
    
    def _generate_recommendations(self,
                                 transaction_type: str,
                                 amount: float,
                                 deadline_hours: Optional[float],
                                 is_high_risk: bool,
                                 available_rails: Dict,
                                 rails_scored: Dict) -> List[str]:
        """Generate contextual recommendations."""
        recommendations = []
        
        # Type-based recommendations
        if transaction_type == "very_high_value":
            recommendations.append("Consider SWIFT GPI for full tracking and traceability")
            recommendations.append("Enhanced compliance verification recommended")
            recommendations.append("Consider split routing with multiple rails")
        
        if transaction_type == "urgent":
            recommendations.append("Select fastest available rail")
            recommendations.append("Monitor real-time status closely")
        
        if transaction_type == "high_value":
            recommendations.append("Prioritize rail reliability and track record")
            recommendations.append("Consider backup rail for redundancy")
        
        if is_high_risk:
            recommendations.append("Ensure full compliance documentation")
            recommendations.append("Consider manual review before execution")
            recommendations.append("Request additional verification from beneficiary")
        
        # Rail-specific recommendations
        eligible_rails = {k: v for k, v in rails_scored.items() if v.get("eligible")}
        if len(eligible_rails) == 1:
            recommendations.append(f"Only one eligible rail: {list(eligible_rails.keys())[0]}")
        
        # Cost recommendations
        costs = [v["cost_usd"] for v in rails_scored.values() if v.get("eligible")]
        if costs:
            min_cost = min(costs)
            max_cost = max(costs)
            if max_cost - min_cost > 20:
                recommendations.append(f"Cost variation is significant (${min_cost:.2f} - ${max_cost:.2f})")
        
        return recommendations
    
    def _check_deadline_feasibility(self, deadline_hours: Optional[float],
                                  available_rails: Dict) -> str:
        """Check if deadline is feasible with available rails."""
        if not deadline_hours:
            return "no_deadline"
        
        feasible_rails = []
        for rail_name, rail_data in available_rails.items():
            if rail_data.get("processing_hours", 24) <= deadline_hours:
                feasible_rails.append(rail_name)
        
        if not feasible_rails:
            return "infeasible"
        
        if len(feasible_rails) == 1:
            return f"marginal ({len(feasible_rails)} option)"
        
        return f"feasible ({len(feasible_rails)} options)"
    
    def generate_summary(self, context: PaymentContext) -> str:
        """Generate human-readable summary of payment context."""
        lines = []
        lines.append(f"Transaction Type: {context.transaction_type.upper()}")
        lines.append(f"Complexity Score: {context.transaction_score:.1%}")
        
        if context.is_high_value:
            lines.append("⚠ High-value transaction")
        
        if context.is_urgent:
            lines.append("⏱ Time-sensitive processing")
        
        if context.is_high_risk:
            lines.append("🔒 Enhanced compliance required")
        
        lines.append(f"Available Routes: {len(context.corridors_available)}")
        lines.append(f"Rails Evaluated: {len(context.rails_scored)}")
        
        if context.recommendations:
            lines.append("\nRecommendations:")
            for rec in context.recommendations[:3]:  # Top 3
                lines.append(f"  • {rec}")
        
        return "\n".join(lines)
