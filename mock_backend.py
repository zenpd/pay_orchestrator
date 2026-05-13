#!/usr/bin/env python3
"""Simple working regional payment orchestrator backend."""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys

# Regional payment rails data
REGIONS_DATA = {
    "US": {
        "rails": {
            "ACH": {"name": "ACH", "speed": 65, "cost": 95, "reliability": 88, "cost_usd": 0.50, "time_hours": 24.0},
            "Wire": {"name": "Wire Transfer", "speed": 95, "cost": 40, "reliability": 99, "cost_usd": 15.00, "time_hours": 0.5},
            "RTP": {"name": "Real-Time Payments", "speed": 100, "cost": 80, "reliability": 92, "cost_usd": 2.50, "time_hours": 0.02},
            "SWIFT": {"name": "SWIFT", "speed": 85, "cost": 35, "reliability": 96, "cost_usd": 25.00, "time_hours": 1.0},
        },
        "corridors": {"US_UK": "USA → UK", "US_EU": "USA → Europe", "US_CA": "USA → Canada"},
        "currencies": ["USD", "EUR", "GBP", "CAD"]
    },
    "UK": {
        "rails": {
            "Faster": {"name": "Faster Payments", "speed": 88, "cost": 85, "reliability": 91, "cost_usd": 1.25, "time_hours": 0.083},
            "BACS": {"name": "BACS", "speed": 60, "cost": 92, "reliability": 99, "cost_usd": 0.75, "time_hours": 48.0},
            "CHAPS": {"name": "CHAPS", "speed": 95, "cost": 30, "reliability": 99, "cost_usd": 8.00, "time_hours": 0.25},
            "SWIFT": {"name": "SWIFT GPI", "speed": 92, "cost": 32, "reliability": 97, "cost_usd": 22.00, "time_hours": 0.5},
        },
        "corridors": {"UK_US": "UK → USA", "UK_EU": "UK → Europe", "UK_SA": "UK → South Africa"},
        "currencies": ["GBP", "USD", "EUR", "CHF"]
    },
    "SA": {
        "rails": {
            "RTGS": {"name": "RTGS", "speed": 90, "cost": 40, "reliability": 94, "cost_usd": 12.00, "time_hours": 1.0},
            "PayShap": {"name": "PayShap Instant", "speed": 98, "cost": 92, "reliability": 93, "cost_usd": 0.25, "time_hours": 0.001},
            "EFT": {"name": "EFT", "speed": 65, "cost": 88, "reliability": 92, "cost_usd": 0.50, "time_hours": 6.0},
            "SWIFT": {"name": "SWIFT GPI", "speed": 85, "cost": 35, "reliability": 96, "cost_usd": 20.00, "time_hours": 2.0},
        },
        "corridors": {"SA_US": "SA → USA", "SA_UK": "SA → UK", "SA_EUR": "SA → Europe"},
        "currencies": ["ZAR", "USD", "EUR", "GBP"]
    },
    "EUR": {
        "rails": {
            "SEPA_Instant": {"name": "SEPA Instant", "speed": 98, "cost": 90, "reliability": 95, "cost_usd": 0.50, "time_hours": 0.01},
            "SEPA": {"name": "SEPA Standard", "speed": 70, "cost": 88, "reliability": 98, "cost_usd": 0.25, "time_hours": 24.0},
            "SWIFT": {"name": "SWIFT GPI", "speed": 90, "cost": 38, "reliability": 96, "cost_usd": 18.00, "time_hours": 1.0},
            "CHIPS": {"name": "CHIPS", "speed": 88, "cost": 28, "reliability": 97, "cost_usd": 30.00, "time_hours": 0.1},
        },
        "corridors": {"EUR_US": "EU → USA", "EUR_UK": "EU → UK", "EUR_SA": "EU → South Africa"},
        "currencies": ["EUR", "USD", "GBP", "CHF"]
    }
}

class RegionalPaymentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for regional data."""
        path = urlparse(self.path).path
        
        # CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Routes
        if path == "/api/v1/payment/regions":
            response = {
                "regions": ["US", "UK", "SA", "EUR"],
                "descriptions": {
                    "US": "United States",
                    "UK": "United Kingdom",
                    "SA": "South Africa",
                    "EUR": "Europe"
                }
            }
        elif path.startswith("/api/v1/payment/regions/"):
            # Extract region name - handle both /regions/US and /regions/US/rails
            path_parts = path.split("/")
            # path will be like: /api/v1/payment/regions/US or /api/v1/payment/regions/US/rails
            # path_parts: ['', 'api', 'v1', 'payment', 'regions', 'US'] or ['', 'api', 'v1', 'payment', 'regions', 'US', 'rails']
            if path_parts[-1] == "rails":
                region = path_parts[-2]
            else:
                region = path_parts[-1]
            
            region = region.strip("/")
            
            if region in REGIONS_DATA:
                data = REGIONS_DATA[region]
                response = {
                    "region": region,
                    "rails": data["rails"],
                    "corridors": data["corridors"],
                    "currencies": data["currencies"]
                }
            else:
                response = {"error": f"Region {region} not found"}
        elif path == "/api/v1/payment/orchestrate":
            response = {
                "session_id": "mock-session-123",
                "stage": "completed",
                "selected_rail": "SWIFT_GPI",
                "rail_scores": {
                    "SWIFT_GPI": {
                        "rail_type": "SWIFT_GPI",
                        "composite_score": 92.0,
                        "cost_score": 35,
                        "speed_score": 85,
                        "reliability_score": 96,
                        "estimated_cost_usd": 25.00,
                        "estimated_time_hours": 1.0,
                        "feasibility": "FEASIBLE"
                    }
                },
                "execution_result": {
                    "transaction_id": "TXN-2026-05-13-001",
                    "status": "SUBMITTED"
                },
                "messages": ["Payment orchestrated successfully"],
                "errors": []
            }
        else:
            response = {"message": "Payment Orchestrator API"}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests for payment orchestration."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        # Parse request
        try:
            request_data = json.loads(body)
        except:
            request_data = {}
        
        # CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Mock orchestration response with rich decision justification
        region = request_data.get("region", "US")
        amount = request_data.get("amount", 50000)
        corridor = request_data.get("corridor", "US_UK")
        
        # Calculate scores for all rails in region
        region_data = REGIONS_DATA.get(region, REGIONS_DATA["US"])
        all_rail_scores = {}
        
        for rail_name, rail_data in region_data["rails"].items():
            # Weighted scoring: speed 40%, cost 30%, reliability 30%
            composite = (rail_data["speed"] * 0.40 + rail_data["cost"] * 0.30 + rail_data["reliability"] * 0.30)
            
            # Business rule: high-value transactions prefer SWIFT
            if amount > 250000 and "SWIFT" in rail_name:
                composite += 5
            
            all_rail_scores[rail_name] = {
                "rail_type": rail_name,
                "composite_score": round(composite, 1),
                "cost_score": rail_data["cost"],
                "speed_score": rail_data["speed"],
                "reliability_score": rail_data["reliability"],
                "estimated_cost_usd": rail_data["cost_usd"],
                "estimated_time_hours": rail_data["time_hours"],
                "feasibility": "FEASIBLE" if rail_data.get("success_rate", 0.95) > 0.90 else "RISKY"
            }
        
        # Find best rail
        best_rail = max(all_rail_scores.items(), key=lambda x: x[1]["composite_score"])
        selected_rail_name = best_rail[0]
        selected_rail_data = best_rail[1]
        
        # Generate decision justification
        decision_justification = {
            "selected_rail": selected_rail_name,
            "decision_reasoning": f"Selected {selected_rail_name} based on optimal speed ({selected_rail_data['speed_score']} speed score) and balanced cost/reliability. "
                                  f"Processing time: {selected_rail_data['estimated_time_hours']} hours with {selected_rail_data['estimated_cost_usd']:.2f} USD fee.",
            "cost_analysis": f"Transaction cost: USD {selected_rail_data['estimated_cost_usd']:.2f}. Cost efficiency: {selected_rail_data['cost_score']}/100.",
            "speed_analysis": f"Expected processing time: {selected_rail_data['estimated_time_hours']} hours. Speed score: {selected_rail_data['speed_score']}/100.",
            "reliability_analysis": f"Success probability: {selected_rail_data['reliability_score']}/100. This rail is {'highly reliable' if selected_rail_data['reliability_score'] > 95 else 'reliable'}.",
            "business_rules_applied": [
                "High-value preference for SWIFT" if amount > 250000 else "Standard scoring applied",
                f"Corridor {corridor} verified"
            ],
            "comparative_analysis": {
                rail_name: {
                    "composite_score": score["composite_score"],
                    "vs_selected": round(selected_rail_data["composite_score"] - score["composite_score"], 1),
                    "reason": f"Lower speed: {score['speed_score']}" if score['speed_score'] < selected_rail_data['speed_score'] 
                              else f"Higher cost: ${score['estimated_cost_usd']:.2f}"
                }
                for rail_name, score in all_rail_scores.items() if rail_name != selected_rail_name
            }
        }
        
        response = {
            "session_id": "session-" + str(int(amount/1000)) + "K-" + region,
            "stage": "completed",
            "selected_rail": selected_rail_name,
            "rail_scores": all_rail_scores,
            "decision_justification": decision_justification,
            "compliance_validation": {
                "status": "APPROVED",
                "risk_score": 0.15,
                "checks_passed": ["AML_SCREENING", "CORRIDOR_VALIDATION", "LIMIT_CHECK"],
                "warnings": []
            },
            "execution_result": {
                "transaction_id": f"TXN-{region}-{int(amount/1000)}K",
                "rail_used": selected_rail_name,
                "status": "SUBMITTED",
                "estimated_arrival": f"{selected_rail_data['estimated_time_hours']} hours"
            },
            "messages": [
                "Analyzed payment parameters",
                "Scored all available payment rails",
                f"Selected optimal route: {selected_rail_name}",
                "Compliance validation passed",
                "Payment orchestrated successfully"
            ],
            "errors": []
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress logging."""
        pass

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8005
    server = HTTPServer((host, port), RegionalPaymentHandler)
    print(f"🚀 Regional Payment Orchestrator API running on http://localhost:{port}")
    print(f"📡 Regions: US, UK, SA, EUR")
    print(f"📊 With realistic payment rails and corridors")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Server stopped")
        sys.exit(0)
