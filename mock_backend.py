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
            region = path.split("/")[-1].strip("/")
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
        
        # Mock orchestration response
        region = request_data.get("region", "US")
        amount = request_data.get("amount", 50000)
        
        response = {
            "session_id": "session-" + str(amount),
            "stage": "completed",
            "selected_rail": "SWIFT_GPI",
            "rail_scores": {
                rail_name: {
                    "rail_type": rail_name,
                    "composite_score": (rail_data["speed"] * 0.4 + rail_data["cost"] * 0.3 + rail_data["reliability"] * 0.3),
                    "cost_score": rail_data["cost"],
                    "speed_score": rail_data["speed"],
                    "reliability_score": rail_data["reliability"],
                    "estimated_cost_usd": rail_data["cost_usd"],
                    "estimated_time_hours": rail_data["time_hours"],
                    "feasibility": "FEASIBLE"
                }
                for rail_name, rail_data in REGIONS_DATA.get(region, REGIONS_DATA["US"])["rails"].items()
            },
            "execution_result": {
                "transaction_id": f"TXN-{region}-{int(amount/1000)}K",
                "rail_used": "SWIFT_GPI",
                "status": "SUBMITTED"
            },
            "messages": [
                "Analyzed payment parameters",
                "Scored all available payment rails",
                "Selected optimal route: SWIFT_GPI",
                "Payment executed successfully"
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
