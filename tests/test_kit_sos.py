"""Testes de ponta a ponta do Kit SOS (só biblioteca padrão).

Corre com:  python3 -m unittest discover -s tests -v
"""
import http.client
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))
import fake_services  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "kit_sos", "app", "server.py")
PORT = 18099
BASE = f"http://127.0.0.1:{PORT}"
TODAY = date.today()


def call(method, path, body=None, base=BASE):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"} if data else {})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def ha_calls():
    req = urllib.request.Request("http://127.0.0.1:18123/api/_calls", headers={"Authorization": "Bearer test-token"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def service_calls():
    return [c for c in ha_calls() if c["path"].startswith("/api/services/")]


def wait_port(port, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise RuntimeError(f"porta {port} não abriu")


def start_server(port, dev=True):
    tmp = tempfile.mkdtemp(prefix="kitsos-")
    with open(os.path.join(tmp, "options.json"), "w") as fh:
        json.dump({"language": "auto", "notify_enabled": False, "notify_days": 30, "notify_time": "10:00",
                   "notify_service": "telegram_bot.send_message", "notify_target": "", "sensors": True}, fh)
    env = dict(os.environ, KIT_SOS_DATA=tmp, KIT_SOS_PORT=str(port), SUPERVISOR_TOKEN="test-token",
               KIT_SOS_HA_API="http://127.0.0.1:18123/api", KIT_SOS_VERSION="1.0.0-test")
    if dev:
        env["KIT_SOS_DEV"] = "1"
    proc = subprocess.Popen([sys.executable, SERVER], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    wait_port(port)
    return proc, tmp


class KitSOSTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fakes = fake_services.start()
        cls.proc, cls.tmp = start_server(PORT)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        out = cls.proc.communicate(timeout=5)[0].decode()
        if os.environ.get("SHOW_LOG"):
            print(out)
        shutil.rmtree(cls.tmp, ignore_errors=True)
        for s in cls.fakes:
            s.shutdown()

    def item(self, name):
        st = call("GET", "/api/state")[1]
        return next(i for i in st["items"] if i["name"] == name)

    def test_01_health_and_static(self):
        self.assertEqual(call("GET", "/api/health"), (200, {"ok": True, "version": "1.0.0-test"}))
        with urllib.request.urlopen(BASE + "/") as r:
            html = r.read().decode()
        self.assertIn("app.js?v=1.0.0-test", html)
        conn = http.client.HTTPConnection("127.0.0.1", PORT)
        conn.request("GET", "/../server.py")
        self.assertEqual(conn.getresponse().status, 404)

    def test_02_grocy_wrong_key(self):
        st, body = call("POST", "/api/import/grocy", {"url": "http://127.0.0.1:18080", "api_key": "x", "dry_run": True})
        self.assertEqual((st, body["error"]), (400, "grocy_auth"))
        st, body = call("POST", "/api/import/grocy", {"url": "http://127.0.0.1:1", "api_key": "x", "dry_run": True})
        self.assertEqual(body["error"], "grocy_unreachable")

    def test_03_grocy_dry_run(self):
        st, body = call("POST", "/api/import/grocy",
                        {"url": "127.0.0.1:18080/api/", "api_key": fake_services.GROCY_KEY, "dry_run": True})
        self.assertEqual(st, 200, body)
        s = body["summary"]
        self.assertEqual((s["products"], s["items"], s["with_expiry"], s["without_stock"], s["skipped_inactive"]),
                         (6, 7, 4, 1, 1))
        self.assertEqual(call("GET", "/api/state")[1]["items"], [])

    def test_04_grocy_import(self):
        st, body = call("POST", "/api/import/grocy",
                        {"url": "http://127.0.0.1:18080", "api_key": fake_services.GROCY_KEY, "dry_run": False})
        self.assertEqual((st, body["imported"]), (200, 7))
        state = call("GET", "/api/state")[1]
        names = sorted(i["name"] for i in state["items"])
        self.assertEqual(names.count("Água 1,5 L"), 2)
        self.assertNotIn("Produto antigo", names)
        agua = [i for i in state["items"] if i["name"] == "Água 1,5 L"]
        soon = next(i for i in agua if i["days_left"] == 20)
        self.assertEqual(soon["quantity"], 6)  # 4 + 2 juntados no mesmo lote
        self.assertEqual(soon["status"], "soon")
        self.assertEqual(soon["notes"], "Garrafões para 3 dias\nlote Continente")
        self.assertEqual(soon["min_quantity"], 6)
        self.assertEqual(self.item("Atum em lata")["status"], "expired")
        self.assertEqual(self.item("Pilhas AA")["expiry"], None)
        self.assertEqual(self.item("Lanterna")["status"], "missing")
        self.assertEqual(self.item("Manta térmica")["status"], "low")
        cats = {c["name"]: c for c in state["categories"]}
        self.assertEqual(cats["Água"]["icon"], "💧")
        self.assertEqual(cats["Medicamentos"]["icon"], "💊")
        self.assertEqual({u["name"]: u["name_plural"] for u in state["units"]}["Lata"], "Latas")
        self.assertEqual(state["stats"], {"total": 6, "soon": 1, "expired": 1, "missing": 1, "low": 1})

    def test_05_month_only_expiry_uses_day_01(self):
        nm = date(TODAY.year + (TODAY.month == 12), TODAY.month % 12 + 1, 1)
        loc = call("GET", "/api/state")[1]["locations"][0]["id"]
        st, body = call("POST", "/api/items", {"name": "Barras energéticas", "quantity": "3", "expiry": nm.strftime("%Y-%m"),
                                               "location_id": loc})
        self.assertEqual(st, 201, body)
        it = self.item("Barras energéticas")
        self.assertEqual(it["expiry"], nm.strftime("%Y-%m"))
        self.assertEqual(it["days_left"], (nm - TODAY).days)
        self.assertEqual(it["status"], "soon")

    def test_06_validation(self):
        self.assertEqual(call("POST", "/api/items", {"name": " "})[1]["error"], "invalid_name")
        self.assertEqual(call("POST", "/api/items", {"name": "X", "expiry": "2026-13"})[1]["error"], "invalid_expiry")
        self.assertEqual(call("POST", "/api/items", {"name": "X", "expiry": "2026-02-30"})[1]["error"], "invalid_expiry")
        self.assertEqual(call("POST", "/api/items", {"name": "X", "quantity": -1})[1]["error"], "invalid_quantity")
        self.assertEqual(call("POST", "/api/items", {"name": "X", "category_id": 999})[1]["error"], "invalid_categories")
        self.assertEqual(call("PUT", "/api/items/99999", {"name": "X"})[0], 404)

    def test_07_notifications_once_per_expiry(self):
        before = len(service_calls())
        st, body = call("POST", "/api/notify/check")
        self.assertEqual(body, {"sent": 3, "failed": 0})  # água (20 d), atum (expirado), barras (dia 01 do mês seguinte)
        calls = service_calls()[before:]
        self.assertTrue(all(c["path"] == "/api/services/telegram_bot/send_message" for c in calls))
        self.assertTrue(all(c["body"]["parse_mode"] == "markdown" for c in calls))
        msgs = "\n".join(c["body"]["message"] for c in calls)
        self.assertIn("*Água 1,5 L* expira daqui a 20 dias", msgs)
        self.assertIn("expirou há 3 dias", msgs)
        self.assertIn("Quantidade: 6 Unidades", msgs)
        self.assertIn("Local: Despensa", msgs)
        events = [c for c in ha_calls() if c["path"] == "/api/events/kit_sos_expiring"]
        self.assertGreaterEqual(len(events), 3)
        # Segunda verificação não repete
        self.assertEqual(call("POST", "/api/notify/check")[1], {"sent": 0, "failed": 0})
        # Mudar a validade para dentro da janela gera novo aviso
        ben = self.item("Ben-u-ron 500")
        call("PUT", f"/api/items/{ben['id']}", {"expiry": (TODAY + timedelta(days=10)).isoformat()})
        self.assertEqual(call("POST", "/api/notify/check")[1], {"sent": 1, "failed": 0})
        self.assertIn("expira daqui a 10 dias", service_calls()[-1]["body"]["message"])

    def test_08_adjust(self):
        it = self.item("Pilhas AA")
        call("POST", f"/api/items/{it['id']}/adjust", {"delta": -3})
        self.assertEqual(self.item("Pilhas AA")["quantity"], 5)
        call("POST", f"/api/items/{it['id']}/adjust", {"delta": -50})
        self.assertEqual(self.item("Pilhas AA")["quantity"], 0)
        self.assertEqual(self.item("Pilhas AA")["status"], "missing")

    def test_09_lookups(self):
        st, body = call("POST", "/api/categories", {"name": "água"})
        self.assertEqual((st, body["error"]), (409, "duplicate_name"))
        st, body = call("POST", "/api/categories", {"name": "Documentos"})
        self.assertEqual(st, 201)
        cid = body["id"]
        cat = next(c for c in call("GET", "/api/state")[1]["categories"] if c["id"] == cid)
        self.assertEqual(cat["icon"], "📄")
        call("PUT", f"/api/categories/{cid}", {"name": "Papéis", "icon": "🗂️", "color": "brown"})
        cat = next(c for c in call("GET", "/api/state")[1]["categories"] if c["id"] == cid)
        self.assertEqual((cat["name"], cat["icon"], cat["color"]), ("Papéis", "🗂️", "brown"))
        # Apagar categoria em uso deixa os artigos sem categoria
        food = next(c for c in call("GET", "/api/state")[1]["categories"] if c["name"] == "Comida")
        self.assertEqual(call("DELETE", f"/api/categories/{food['id']}")[0], 200)
        self.assertIsNone(self.item("Atum em lata")["category_id"])

    def test_10_sensors_pushed(self):
        time.sleep(3)
        states = [c for c in ha_calls() if c["path"].startswith("/api/states/")]
        paths = {c["path"] for c in states}
        self.assertTrue({"/api/states/sensor.kit_sos_expiring", "/api/states/sensor.kit_sos_expired",
                         "/api/states/sensor.kit_sos_low_stock", "/api/states/sensor.kit_sos_items"} <= paths)
        last = [c for c in states if c["path"].endswith("kit_sos_expiring")][-1]["body"]
        self.assertEqual(last["attributes"]["friendly_name"], "Kit SOS a expirar")

    def test_11_backup_roundtrip(self):
        st, data = call("GET", "/api/export")
        n = len(data["items"])
        self.assertGreater(n, 5)
        call("POST", "/api/items", {"name": "Temporário"})
        st, body = call("POST", "/api/import/backup", data)
        self.assertEqual((st, body["counts"]["items"]), (200, n))
        self.assertEqual(len(call("GET", "/api/state")[1]["items"]), n)
        self.assertEqual(call("POST", "/api/import/backup", {"app": "outra"})[1]["error"], "invalid_backup")
        # Os avisos já enviados não se repetem depois de restaurar
        self.assertEqual(call("POST", "/api/notify/check")[1]["sent"], 0)

    def test_12_only_ingress_ip_allowed(self):
        proc, tmp = start_server(PORT + 1, dev=False)
        try:
            st, body = call("GET", "/api/state", base=f"http://127.0.0.1:{PORT + 1}")
            self.assertEqual((st, body["error"]), (403, "forbidden"))
        finally:
            proc.terminate()
            proc.wait(5)
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
