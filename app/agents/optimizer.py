"""
Optimizer Agent
Responsibility: Multi-objective rail selection with rich decision justification
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import logging

log = logging.getLogger(__name__)


@dataclass
class RailDecisionJustification:
    """Detailed justification for rail selection."""
    selected_rail: str
    backup_rail: Optional[str]
    total_score: float
    score_breakdown: Dict[str, float]
    cost_analysis: str
    speed_analysis: str
    reliability_analysis: str
    compliance_considerations: str
    business_rules_applied: List[str]
    decision_reasoning: str
    comparative_analysis: Dict[str, Dict[str, float]]  # Other rails comparison


@dataclass  
class RailScore:
    """Comprehensive score for a payment rail."""
    rail_name: str
    total_score: float
    
    # Component scores (0-100)
    cost_score: float
    speed_score: float
    reliability_score: float
    compliance_score: float
    
    # Metrics
    estimated_cost_usd: float
    estimated_time_hours: float
    success_rate: float
    availability: float
    
    # Status
    is_eligible: bool
    ineligibility_reason: Optional[str] = None


class OptimizerAgent:
    """Multi-objective payment rail optimization with decision justification."""
    
    def __init__(self):
        """Initialize optimization weights and business rules."""
        # Default optimization weights
        self.default_weights = {
            "cost": 0.30,          # 30% cost efficiency
            "speed": 0.25,         # 25% processing speed
            "reliability": 0.30,   # 30% success/availability
            "compliance": 0.15     # 15% compliance/regulatory
        }
        
        # Business rules for dynamic weighting
        self.business_rules = {
            "high_value_threshold": 100000,      # > $100k: prefer reliability
            "urgent_threshold_hours": 2,         # < 2h deadline: prefer speed
            "cost_sensitive_threshold": 1000,    # < $1k: prefer cost
            "standard_processing": 24             # Standard processing window
        }
    
    def optimize_and_justify(self, 
                           rails_data: Dict[str, Dict],
                           amount: float,
                           deadline_hours: Optional[float] = None,
                           region: str = "US",
                           compliance_risk: float = 0.1) -> RailDecisionJustification:
        """
        Optimize payment rail selection with detailed justification.
        
        Args:
            rails_data: Dict of available rails with their characteristics
            amount: Transaction amount
            deadline_hours: Time constraint (optional)
            region: Processing region
            compliance_risk: Risk score from compliance agent (0-1.0)
        
        Returns:
            RailDecisionJustification with full decision reasoning
        """
        
        # Score all available rails
        rail_scores = {}
        eligible_rails = {}
        
        for rail_name, rail_data in rails_data.items():
            score = self._score_rail(
                rail_name=rail_name,
                rail_data=rail_data,
                amount=amount,
                deadline_hours=deadline_hours,
                compliance_risk=compliance_risk
            )
            rail_scores[rail_name] = score
            
            if score.is_eligible:
                eligible_rails[rail_name] = score
        
        if not eligible_rails:
            # Return any rail with reason
            best_rail = max(rail_scores.values(), key=lambda x: x.total_score)
            return self._build_empty_justification(best_rail, rail_scores, amount)
        
        # Determine dynamic weights based on transaction context
        weights = self._determine_dynamic_weights(amount, deadline_hours)
        
        # Recalculate scores with dynamic weights
        weighted_scores = {}
        for rail_name, score in eligible_rails.items():
            weighted_total = (
                score.cost_score * weights["cost"] +
                score.speed_score * weights["speed"] +
                score.reliability_score * weights["reliability"] +
                score.compliance_score * weights["compliance"]
            )
            weighted_scores[rail_name] = weighted_total
        
        # Select best and backup
        sorted_rails = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)
        selected_rail_name = sorted_rails[0][0]
        selected_score = rail_scores[selected_rail_name]
        
        backup_rail_name = sorted_rails[1][0] if len(sorted_rails) > 1 else None
        
        # Build comparative analysis
        comparative = {}
        for rail_name, weighted_score in sorted_rails[:3]:  # Top 3
            score = rail_scores[rail_name]
            comparative[rail_name] = {
                "weighted_score": weighted_score,
                "cost": score.cost_score,
                "speed": score.speed_score,
                "reliability": score.reliability_score,
                "compliance": score.compliance_score,
                "cost_usd": score.estimated_cost_usd,
                "time_hours": score.estimated_time_hours
            }
        
        # Generate detailed analysis
        justification = self._generate_justification(
            selected_rail=selected_score,
            backup_rail=backup_rail_name,
            total_score=weighted_scores[selected_rail_name],
            score_breakdown=self._break_down_scores(selected_score, weights),
            amount=amount,
            deadline_hours=deadline_hours,
            weights=weights,
            comparative_analysis=comparative,
            rail_scores=rail_scores,
            region=region
        )
        
        return justification
    
    def _score_rail(self, 
                   rail_name: str,
                   rail_data: Dict,
                   amount: float,
                   deadline_hours: Optional[float],
                   compliance_risk: float) -> RailScore:
        """Score a single rail across all criteria."""
        
        # Check eligibility
        min_amount = rail_data.get("min_amount", 0)
        max_amount = rail_data.get("max_amount", float('inf'))
        
        if amount < min_amount:
            return RailScore(
                rail_name=rail_name,
                total_score=0,
                cost_score=0, speed_score=0, reliability_score=0, compliance_score=0,
                estimated_cost_usd=0, estimated_time_hours=0, success_rate=0, availability=0,
                is_eligible=False,
                ineligibility_reason=f"Amount ${amount:,.0f} below minimum ${min_amount:,.0f}"
            )
        
        if amount > max_amount:
            return RailScore(
                rail_name=rail_name,
                total_score=0,
                cost_score=0, speed_score=0, reliability_score=0, compliance_score=0,
                estimated_cost_usd=0, estimated_time_hours=0, success_rate=0, availability=0,
                is_eligible=False,
                ineligibility_reason=f"Amount ${amount:,.0f} exceeds maximum ${max_amount:,.0f}"
            )
        
        # Extract metrics
        cost_usd = rail_data.get("cost_usd", 10)
        time_hours = rail_data.get("processing_hours", 24)
        success_rate = rail_data.get("success_rate", 0.95)
        availability = rail_data.get("availability", 0.99)
        
        # Score components (0-100)
        cost_score = self._score_cost(cost_usd, amount)
        speed_score = self._score_speed(time_hours, deadline_hours)
        reliability_score = self._score_reliability(success_rate, availability)
        compliance_score = self._score_compliance(rail_data.get("compliance_tier", "standard"), compliance_risk)
        
        # Apply business rules
        cost_score, speed_score, reliability_score, compliance_score = self._apply_business_rules(
            amount=amount,
            deadline_hours=deadline_hours,
            rail_name=rail_name,
            cost_score=cost_score,
            speed_score=speed_score,
            reliability_score=reliability_score,
            compliance_score=compliance_score
        )
        
        # Calculate initial total (equally weighted for now)
        total = (cost_score + speed_score + reliability_score + compliance_score) / 4
        
        return RailScore(
            rail_name=rail_name,
            total_score=total,
            cost_score=cost_score,
            speed_score=speed_score,
            reliability_score=reliability_score,
            compliance_score=compliance_score,
            estimated_cost_usd=cost_usd,
            estimated_time_hours=time_hours,
            success_rate=success_rate,
            availability=availability,
            is_eligible=True
        )
    
    def _score_cost(self, cost_usd: float, amount: float) -> float:
        """Score cost efficiency (0-100, higher is better for low cost)."""
        # Cost ratio
        ratio = cost_usd / max(amount, 1)
        
        # Penalize high costs
        if ratio > 0.01:  # > 1% transaction fee
            return max(0, 100 - (ratio * 5000))
        
        return min(100, (1 - ratio / 0.01) * 100)
    
    def _score_speed(self, time_hours: float, deadline_hours: Optional[float]) -> float:
        """Score speed performance (0-100, higher is better for fast processing)."""
        if time_hours <= 1:
            return 100
        elif time_hours <= 2:
            return 90
        elif time_hours <= 4:
            return 75
        elif time_hours <= 24:
            return 50
        elif time_hours <= 48:
            return 30
        else:
            return 10
    
    def _score_reliability(self, success_rate: float, availability: float) -> float:
        """Score reliability (0-100, higher is better)."""
        combined_reliability = (success_rate * 0.7) + (availability * 0.3)
        return combined_reliability * 100
    
    def _score_compliance(self, compliance_tier: str, compliance_risk: float) -> float:
        """Score compliance quality (0-100)."""
        tier_scores = {
            "premium": 95,
            "standard": 80,
            "basic": 60
        }
        
        tier_score = tier_scores.get(compliance_tier, 70)
        
        # Adjust for compliance risk
        risk_penalty = compliance_risk * 30  # Up to 30 point penalty
        
        return max(0, min(100, tier_score - risk_penalty))
    
    def _apply_business_rules(self, 
                            amount: float,
                            deadline_hours: Optional[float],
                            rail_name: str,
                            cost_score: float,
                            speed_score: float,
                            reliability_score: float,
                            compliance_score: float) -> Tuple[float, float, float, float]:
        """Apply business rules to boost/penalize specific scenarios."""
        
        # High-value transactions: boost reliability
        if amount > self.business_rules["high_value_threshold"]:
            reliability_score = min(100, reliability_score * 1.15)
            if "SWIFT" in rail_name:
                compliance_score = min(100, compliance_score * 1.10)
        
        # Urgent deadlines: boost speed
        if deadline_hours and deadline_hours < self.business_rules["urgent_threshold_hours"]:
            speed_score = min(100, speed_score * 1.25)
        
        # Low-amount transactions: boost cost efficiency
        if amount < self.business_rules["cost_sensitive_threshold"]:
            cost_score = min(100, cost_score * 1.20)
        
        # Penalize slow rails for urgent transactions
        if deadline_hours and deadline_hours < 4:
            if "BATCH" in rail_name or "SLOW" in rail_name.upper():
                speed_score = max(0, speed_score * 0.5)
        
        return cost_score, speed_score, reliability_score, compliance_score
    
    def _determine_dynamic_weights(self, amount: float, 
                                  deadline_hours: Optional[float]) -> Dict[str, float]:
        """Determine optimization weights based on transaction context."""
        weights = self.default_weights.copy()
        
        # High-value transactions prioritize reliability
        if amount > self.business_rules["high_value_threshold"]:
            weights["reliability"] = 0.40
            weights["cost"] = 0.20
            weights["speed"] = 0.20
            weights["compliance"] = 0.20
        
        # Urgent transactions prioritize speed
        if deadline_hours and deadline_hours < self.business_rules["urgent_threshold_hours"]:
            weights["speed"] = 0.45
            weights["cost"] = 0.15
            weights["reliability"] = 0.25
            weights["compliance"] = 0.15
        
        # Cost-sensitive transactions
        if amount < self.business_rules["cost_sensitive_threshold"]:
            weights["cost"] = 0.45
            weights["speed"] = 0.20
            weights["reliability"] = 0.20
            weights["compliance"] = 0.15
        
        # Normalize to sum to 1.0
        total = sum(weights.values())
        return {k: v / total for k, v in weights.items()}
    
    def _break_down_scores(self, score: RailScore, weights: Dict[str, float]) -> Dict[str, float]:
        """Break down weighted contribution of each component."""
        return {
            "cost": score.cost_score * weights["cost"],
            "speed": score.speed_score * weights["speed"],
            "reliability": score.reliability_score * weights["reliability"],
            "compliance": score.compliance_score * weights["compliance"]
        }
    
    def _generate_justification(self,
                              selected_rail: RailScore,
                              backup_rail: Optional[str],
                              total_score: float,
                              score_breakdown: Dict[str, float],
                              amount: float,
                              deadline_hours: Optional[float],
                              weights: Dict[str, float],
                              comparative_analysis: Dict,
                              rail_scores: Dict,
                              region: str) -> RailDecisionJustification:
        """Generate detailed decision justification."""
        
        # Analyze cost
        cost_analysis = self._analyze_cost(selected_rail, amount, weights["cost"])
        
        # Analyze speed
        speed_analysis = self._analyze_speed(selected_rail, deadline_hours, weights["speed"])
        
        # Analyze reliability
        reliability_analysis = self._analyze_reliability(selected_rail, weights["reliability"])
        
        # Analyze compliance
        compliance_analysis = self._analyze_compliance(selected_rail, weights["compliance"])
        
        # Identify business rules applied
        rules_applied = self._identify_rules_applied(amount, deadline_hours, selected_rail.rail_name)
        
        # Generate decision reasoning
        decision_reasoning = self._generate_decision_reasoning(
            selected_rail=selected_rail,
            backup_rail=backup_rail,
            amount=amount,
            weights=weights,
            score_breakdown=score_breakdown,
            rules_applied=rules_applied
        )
        
        return RailDecisionJustification(
            selected_rail=selected_rail.rail_name,
            backup_rail=backup_rail,
            total_score=total_score,
            score_breakdown=score_breakdown,
            cost_analysis=cost_analysis,
            speed_analysis=speed_analysis,
            reliability_analysis=reliability_analysis,
            compliance_considerations=compliance_analysis,
            business_rules_applied=rules_applied,
            decision_reasoning=decision_reasoning,
            comparative_analysis=comparative_analysis
        )
    
    def _analyze_cost(self, rail: RailScore, amount: float, weight: float) -> str:
        """Generate cost analysis text."""
        ratio = (rail.estimated_cost_usd / amount) * 100 if amount > 0 else 0
        
        if rail.cost_score >= 85:
            return f"Highly cost-effective (${rail.estimated_cost_usd:.2f}, {ratio:.2f}% of amount)"
        elif rail.cost_score >= 70:
            return f"Good cost efficiency (${rail.estimated_cost_usd:.2f}, {ratio:.2f}% of amount)"
        else:
            return f"Standard cost structure (${rail.estimated_cost_usd:.2f}, {ratio:.2f}% of amount)"
    
    def _analyze_speed(self, rail: RailScore, deadline_hours: Optional[float], weight: float) -> str:
        """Generate speed analysis text."""
        if rail.estimated_time_hours <= 1:
            speed_desc = "Real-time settlement"
        elif rail.estimated_time_hours <= 2:
            speed_desc = "Ultra-fast (< 2 hours)"
        elif rail.estimated_time_hours <= 24:
            speed_desc = "Standard business day"
        else:
            speed_desc = "Multi-day processing"
        
        if deadline_hours:
            meets_deadline = rail.estimated_time_hours <= deadline_hours
            return f"{speed_desc} (~{rail.estimated_time_hours:.1f}h) - {'Meets' if meets_deadline else 'Exceeds'} deadline ({deadline_hours:.1f}h)"
        
        return f"{speed_desc} (~{rail.estimated_time_hours:.1f}h)"
    
    def _analyze_reliability(self, rail: RailScore, weight: float) -> str:
        """Generate reliability analysis text."""
        success_pct = rail.success_rate * 100
        availability_pct = rail.availability * 100
        
        if rail.reliability_score >= 90:
            return f"Highly reliable ({success_pct:.1f}% success, {availability_pct:.1f}% uptime)"
        elif rail.reliability_score >= 75:
            return f"Dependable ({success_pct:.1f}% success, {availability_pct:.1f}% uptime)"
        else:
            return f"Standard reliability ({success_pct:.1f}% success, {availability_pct:.1f}% uptime)"
    
    def _analyze_compliance(self, rail: RailScore, weight: float) -> str:
        """Generate compliance analysis text."""
        if rail.compliance_score >= 90:
            return "Premium compliance tier - suitable for high-regulation scenarios"
        elif rail.compliance_score >= 75:
            return "Standard compliance - meets most regulatory requirements"
        else:
            return "Basic compliance - suitable for low-risk transactions"
    
    def _identify_rules_applied(self, amount: float, deadline_hours: Optional[float], 
                               rail_name: str) -> List[str]:
        """Identify which business rules influenced the decision."""
        rules = []
        
        if amount > self.business_rules["high_value_threshold"]:
            rules.append(f"High-value rule (>${self.business_rules['high_value_threshold']:,.0f})")
        
        if deadline_hours and deadline_hours < self.business_rules["urgent_threshold_hours"]:
            rules.append(f"Urgent processing rule (<{self.business_rules['urgent_threshold_hours']}h)")
        
        if amount < self.business_rules["cost_sensitive_threshold"]:
            rules.append(f"Cost-sensitive rule (<${self.business_rules['cost_sensitive_threshold']:,.0f})")
        
        return rules
    
    def _generate_decision_reasoning(self, 
                                   selected_rail: RailScore,
                                   backup_rail: Optional[str],
                                   amount: float,
                                   weights: Dict[str, float],
                                   score_breakdown: Dict[str, float],
                                   rules_applied: List[str]) -> str:
        """Generate human-readable decision reasoning."""
        reasons = []
        
        # Dominant factor
        dominant = max(score_breakdown.items(), key=lambda x: x[1])
        reasons.append(f"Selected {selected_rail.rail_name} optimized for {dominant[0]}")
        
        # Rule-based reasoning
        if rules_applied:
            reasons.append(f"Applied business logic: {', '.join(rules_applied)}")
        
        # Weights explanation
        if weights["speed"] > 0.30:
            reasons.append("Priority: Fast processing required")
        if weights["reliability"] > 0.35:
            reasons.append("Priority: Maximum reliability for transaction size")
        if weights["cost"] > 0.40:
            reasons.append("Priority: Cost optimization for transaction amount")
        
        # Backup explanation
        if backup_rail:
            reasons.append(f"Fallback route: {backup_rail}")
        
        return " | ".join(reasons)
    
    def _build_empty_justification(self, rail: RailScore, rail_scores: Dict,
                                  amount: float) -> RailDecisionJustification:
        """Handle case when no rails are eligible."""
        return RailDecisionJustification(
            selected_rail=rail.rail_name,
            backup_rail=None,
            total_score=rail.total_score,
            score_breakdown={"cost": 0, "speed": 0, "reliability": 0, "compliance": 0},
            cost_analysis=f"Cost: ${rail.estimated_cost_usd:.2f}",
            speed_analysis=f"Processing time: {rail.estimated_time_hours:.1f} hours",
            reliability_analysis=f"Success rate: {rail.success_rate*100:.1f}%",
            compliance_considerations="Standard compliance applied",
            business_rules_applied=[],
            decision_reasoning=f"Selected {rail.rail_name} (reason: {rail.ineligibility_reason or 'best available'})",
            comparative_analysis={}
        )
