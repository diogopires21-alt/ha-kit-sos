"""Serviços falsos para testes locais: um Home Assistant e um Grocy mínimos.

Uso: python3 tests/fake_services.py  (HA em :18123, Grocy em :18080)
"""
import json
import threading
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HA_CALLS: list[dict] = []
TODAY = date.today()


def d(days: int) -> str:
    return (TODAY + timedelta(days=days)).isoformat()


GROCY = {
    "products": [
        {"id": 1, "name": "Água 1,5 L", "product_group_id": 1, "location_id": 1, "qu_id_stock": 1,
         "min_stock_amount": "6", "description": "<p>Garrafões para <b>3 dias</b></p>", "active": 1},
        {"id": 2, "name": "Pilhas AA", "product_group_id": 2, "location_id": 2, "qu_id_stock": 2,
         "min_stock_amount": "0", "description": None, "active": 1},
        {"id": 3, "name": "Atum em lata", "product_group_id": 3, "location_id": 1, "qu_id_stock": 3,
         "min_stock_amount": "4", "description": "", "active": 1},
        {"id": 4, "name": "Ben-u-ron 500", "product_group_id": 4, "location_id": 3, "qu_id_stock": 4,
         "min_stock_amount": "1", "description": "", "active": 1},
        {"id": 5, "name": "Lanterna", "product_group_id": 2, "location_id": 2, "qu_id_stock": 1,
         "min_stock_amount": "0", "description": "", "active": 1},
        {"id": 6, "name": "Produto antigo", "product_group_id": 1, "location_id": 1, "qu_id_stock": 1,
         "min_stock_amount": "0", "description": "", "active": 0},
        {"id": 7, "name": "Manta térmica", "product_group_id": 5, "location_id": 2, "qu_id_stock": 1,
         "min_stock_amount": "2", "description": "", "active": 1},
    ],
    "product_groups": [
        {"id": 1, "name": "Água", "active": 1}, {"id": 2, "name": "Energia e luz", "active": 1},
        {"id": 3, "name": "Comida", "active": 1}, {"id": 4, "name": "Medicamentos", "active": 1},
        {"id": 5, "name": "Abrigo", "active": 1},
    ],
    "locations": [
        {"id": 1, "name": "Despensa", "active": 1}, {"id": 2, "name": "Mochila SOS", "active": 1},
        {"id": 3, "name": "Armário WC", "active": 1},
    ],
    "quantity_units": [
        {"id": 1, "name": "Unidade", "name_plural": "Unidades", "active": 1},
        {"id": 2, "name": "Pilha", "name_plural": "Pilhas", "active": 1},
        {"id": 3, "name": "Lata", "name_plural": "Latas", "active": 1},
        {"id": 4, "name": "Caixa", "name_plural": "Caixas", "active": 1},
    ],
    "stock": [
        {"id": 11, "product_id": 1, "amount": "4", "best_before_date": d(20), "location_id": 1, "note": ""},
        {"id": 12, "product_id": 1, "amount": "2", "best_before_date": d(20), "location_id": 1, "note": "lote Continente"},
        {"id": 13, "product_id": 1, "amount": "6", "best_before_date": d(400), "location_id": 1},
        {"id": 14, "product_id": 2, "amount": "8", "best_before_date": "2999-12-31", "location_id": 2},
        {"id": 15, "product_id": 3, "amount": "5", "best_before_date": d(-3), "location_id": 1},
        {"id": 16, "product_id": 4, "amount": "1", "best_before_date": d(45), "location_id": 3},
        {"id": 17, "product_id": 6, "amount": "1", "best_before_date": d(5), "location_id": 1},
        {"id": 18, "product_id": 7, "amount": "1", "best_before_date": "2999-12-31", "location_id": 2},
    ],
}
GROCY_KEY = "segredo123"


class HA(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.headers.get("Authorization") != "Bearer test-token":
            return self._json({"message": "401"}, 401)
        if self.path == "/api/config":
            return self._json({"time_zone": "Europe/Lisbon", "language": "pt"})
        if self.path == "/api/_calls":
            return self._json(HA_CALLS)
        self._json({}, 404)

    def do_POST(self):
        if self.headers.get("Authorization") != "Bearer test-token":
            return self._json({"message": "401"}, 401)
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n) or b"{}")
        HA_CALLS.append({"path": self.path, "body": body})
        if self.path == "/api/_reset":
            HA_CALLS.clear()
        self._json([])


class Grocy(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.headers.get("GROCY-API-KEY") != GROCY_KEY:
            self.send_response(401)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        key = self.path.replace("/api/objects/", "")
        if key not in GROCY:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        body = json.dumps(GROCY[key]).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start(ha_port=18123, grocy_port=18080):
    servers = [ThreadingHTTPServer(("127.0.0.1", ha_port), HA), ThreadingHTTPServer(("127.0.0.1", grocy_port), Grocy)]
    for s in servers:
        threading.Thread(target=s.serve_forever, daemon=True).start()
    return servers


if __name__ == "__main__":
    start()
    print("HA falso em :18123, Grocy falso em :18080 (Ctrl+C para sair)")
    threading.Event().wait()
