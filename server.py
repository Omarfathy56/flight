"""
Flivain Mock API & Static Server
Serves the modern Flight & Travel Booking landing page and provides a mock API
to store and retrieve reservations in `reservations.json`.
"""

import http.server
import socketserver
import json
import os
import uuid
import datetime
from urllib.parse import urlparse

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESERVATIONS_FILE = os.path.join(BASE_DIR, 'reservations.json')


if not os.path.exists(RESERVATIONS_FILE):
    initial_data = [
        {
            "id": "res_demo_001",
            "pnr": "FLV-8942A",
            "type": "flight",
            "airline": "Emirates",
            "flightNumber": "EK 319",
            "origin": "Tokyo, Japan [HND]",
            "destination": "Berlin, Germany [BER]",
            "departureDate": "Oct 18, 2026",
            "returnDate": "Dec 15, 2026",
            "travelers": "1 Adult, Economy",
            "passengerName": "Alexander Wright",
            "passengerEmail": "alex.wright@traveler.com",
            "price": "$840",
            "status": "Confirmed",
            "createdAt": "2026-09-14T20:30:00Z"
        }
    ]
    with open(RESERVATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(initial_data, f, indent=2)


class FlivainRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/reservations':
            self.handle_get_reservations()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/reservations':
            self.handle_post_reservation()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))

    def handle_get_reservations(self):
        try:
            with open(RESERVATIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            response_data = json.dumps({"success": True, "count": len(data), "reservations": data})
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_data.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def handle_post_reservation(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8')
        try:
            payload = json.loads(post_body)
        except Exception:
            payload = {}


        pnr = f"FLV-{uuid.uuid4().hex[:5].upper()}"
        res_id = f"res_{uuid.uuid4().hex[:8]}"
        created_at = datetime.datetime.utcnow().isoformat() + "Z"

        new_reservation = {
            "id": res_id,
            "pnr": pnr,
            "type": payload.get("type", "flight"),
            "airline": payload.get("airline", "Emirates"),
            "flightNumber": payload.get("flightNumber", "EK 319"),
            "origin": payload.get("origin", "Tokyo [HND]"),
            "destination": payload.get("destination", "Berlin [BER]"),
            "departureDate": payload.get("departureDate", "Oct 18, 2026"),
            "returnDate": payload.get("returnDate", "Dec 15, 2026"),
            "travelers": payload.get("travelers", "1 Adult, Economy"),
            "passengerName": payload.get("passengerName", "Discerning Traveler"),
            "passengerEmail": payload.get("passengerEmail", "flyer@example.com"),
            "price": payload.get("price", "$840"),
            "status": "Confirmed",
            "createdAt": created_at
        }

   
        try:
            if os.path.exists(RESERVATIONS_FILE):
                with open(RESERVATIONS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []

            data.insert(0, new_reservation)

            with open(RESERVATIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "success": True,
                "message": "Reservation saved successfully to reservations.json",
                "reservation": new_reservation
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))


if __name__ == '__main__':
    handler = FlivainRequestHandler
    print(f"Starting Flivain Mock API & Web Server at http://localhost:{PORT}")
    print(f"Reservations stored at: {RESERVATIONS_FILE}")
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
