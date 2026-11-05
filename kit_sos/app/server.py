#!/usr/bin/env python3
"""Kit SOS — app do Home Assistant para gerir artigos com validade.

Servidor sem dependências externas (só a biblioteca padrão do Python):
- serve a interface web pelo ingress do Home Assistant;
- guarda os dados em SQLite, na pasta /data da app (entra nas cópias de segurança);
- importa produtos, lotes e configurações do Grocy;
- avisa quando falta X dias para uma validade (por defeito via telegram_bot);
- publica sensores no Home Assistant (a expirar, expirados, em falta, total).
"""
from __future__ import annotations

import html
import json
import logging
import os
import re
import sqlite3
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# ---------------------------------------------------------------------------
# Configuração base
# ---------------------------------------------------------------------------

VERSION = os.environ.get("KIT_SOS_VERSION", "dev")
DATA_DIR = os.environ.get("KIT_SOS_DATA", "/data")
OPTIONS_FILE = os.path.join(DATA_DIR, "options.json")
DB_FILE = os.path.join(DATA_DIR, "kit_sos.db")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
PORT = int(os.environ.get("KIT_SOS_PORT", "8099"))
INGRESS_IP = "172.30.32.2"
DEV_MODE = os.environ.get("KIT_SOS_DEV") == "1"
SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
HA_API = os.environ.get("KIT_SOS_HA_API", "http://supervisor/core/api").rstrip("/")
NO_EXPIRY_GROCY = "2999-12-31"
MAX_BODY = 8 * 1024 * 1024

DEFAULT_OPTIONS = {
    "language": "auto",
    "notify_enabled": True,
    "notify_days": 30,
    "notify_time": "10:00",
    "notify_service": "telegram_bot.send_message",
    "notify_target": "",
    "sensors": True,
}

logging.basicConfig(
    level=logging.DEBUG if os.environ.get("KIT_SOS_DEBUG") == "1" else logging.INFO,
    format="%(asctime)s [kit_sos] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("kit_sos")

_db_lock = threading.RLock()
_tz: ZoneInfo | timezone = timezone.utc
_ha_language = ""
_sensor_dirty = threading.Event()
_stop = threading.Event()
_ready = threading.Event()


# ---------------------------------------------------------------------------
# Opções e utilitários
# ---------------------------------------------------------------------------

def load_options() -> dict:
    opts = dict(DEFAULT_OPTIONS)
    try:
        with open(OPTIONS_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            opts.update({k: v for k, v in data.items() if v is not None})
    except FileNotFoundError:
        pass
    except Exception as exc:  # noqa: BLE001
        log.warning("Não consegui ler options.json: %s", exc)
    try:
        opts["notify_days"] = max(0, min(3650, int(opts.get("notify_days", 30))))
    except (TypeError, ValueError):
        opts["notify_days"] = 30
    if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", str(opts.get("notify_time", ""))):
        opts["notify_time"] = "10:00"
    return opts


def resolve_language(opts: dict | None = None) -> str:
    opts = opts or load_options()
    lang = str(opts.get("language", "auto")).lower()
    if lang in ("pt", "en"):
        return lang
    src = (_ha_language or os.environ.get("LANG", "")).lower()
    return "pt" if src.startswith("pt") else "en"


def now_local() -> datetime:
    return datetime.now(_tz)


def today_local() -> date:
    return now_local().date()


def iso_now() -> str:
    return now_local().replace(microsecond=0).isoformat()


EXPIRY_RE = re.compile(r"^(\d{4})-(\d{2})(?:-(\d{2}))?$")


def normalize_expiry(value) -> str | None:
    """Aceita 'AAAA-MM-DD' ou 'AAAA-MM'. Devolve a forma normalizada ou None."""
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    m = EXPIRY_RE.match(value)
    if not m:
        raise ValueError("invalid_expiry")
    year, month, day = int(m.group(1)), int(m.group(2)), m.group(3)
    if not (1900 <= year <= 2999):
        raise ValueError("invalid_expiry")
    if day is None:
        date(year, month, 1)  # valida o mês
        return f"{year:04d}-{month:02d}"
    d = date(year, month, int(day))
    return d.isoformat()


def effective_date(expiry: str | None) -> date | None:
    """Data efetiva da validade. Sem dia (só mês/ano) assume-se o dia 01."""
    if not expiry:
        return None
    m = EXPIRY_RE.match(expiry)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3) or 1))
    except ValueError:
        return None


def days_left(expiry: str | None, today: date | None = None) -> int | None:
    eff = effective_date(expiry)
    if eff is None:
        return None
    return (eff - (today or today_local())).days


def item_status(item: dict, notify_days: int) -> str:
    qty = item.get("quantity") or 0
    if qty <= 0:
        return "missing"
    d = item.get("days_left")
    if d is not None and d < 0:
        return "expired"
    if d is not None and d <= notify_days:
        return "soon"
    min_q = item.get("min_quantity")
    if min_q is not None and qty < min_q:
        return "low"
    return "ok" if d is not None else "none"


def fmt_qty(q: float) -> str:
    if q is None:
        return "0"
    if float(q).is_integer():
        return str(int(q))
    return (f"{q:.3f}").rstrip("0").rstrip(".")


# Emoji automático por palavras-chave (pode ser alterado na interface)
EMOJI_RULES = [
    (("água", "agua", "water", "bebida"), "💧"),
    (("pilha", "bateria", "battery", "powerbank", "power bank", "carregador"), "🔋"),
    (("medic", "fármac", "farmac", "remédio", "remedio", "comprimido", "medicine", "pharma"), "💊"),
    (("socorro", "first aid", "penso", "ligadura", "curativo", "kit médico"), "🩹"),
    (("comida", "aliment", "conserva", "enlatad", "lata", "food", "snack", "barra"), "🥫"),
    (("lanterna", "luz", "vela", "light", "torch", "flashlight", "candle"), "🔦"),
    (("rádio", "radio"), "📻"),
    (("document", "papel", "cópia", "copia", "paper"), "📄"),
    (("higien", "hygien", "sabão", "sabao", "toalhit", "papel higi", "soap"), "🧼"),
    (("ferrament", "tool", "faca", "canivete", "fita"), "🛠️"),
    (("roupa", "manta", "cobertor", "agasalho", "blanket", "cloth"), "🧥"),
    (("dinheiro", "money", "cash", "moeda"), "💶"),
    (("bebé", "bebe", "baby", "fralda"), "🍼"),
    (("animal", "pet", "cão", "cao", "gato", "dog", "cat"), "🐾"),
    (("fogo", "fósforo", "fosforo", "isqueiro", "fire", "lighter", "match"), "🔥"),
    (("gás", "gas", "combust", "fuel"), "⛽"),
    (("limpeza", "clean", "lixívia", "lixivia", "desinfet"), "🧴"),
]
CATEGORY_COLORS = ["blue", "green", "orange", "purple", "teal", "indigo", "pink", "red", "yellow", "mint", "cyan", "brown"]


def guess_emoji(name: str) -> str:
    low = (name or "").lower()
    for keys, emoji in EMOJI_RULES:
        if any(k in low for k in keys):
            return emoji
    return "📦"


def sort_key(name: str) -> str:
    """Ordenação alfabética que ignora acentos e maiúsculas (Água fica junto de Abrigo)."""
    text = unicodedata.normalize("NFD", str(name or ""))
    return "".join(ch for ch in text if not unicodedata.combining(ch)).casefold()


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    text = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", value, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Base de dados
# ---------------------------------------------------------------------------

MIGRATIONS: list[str] = [
    # v1
    """
    CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE COLLATE NOCASE,
        icon TEXT,
        color TEXT,
        sort INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE COLLATE NOCASE,
        sort INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS units (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE COLLATE NOCASE,
        name_plural TEXT,
        sort INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
        location_id INTEGER REFERENCES locations(id) ON DELETE SET NULL,
        unit_id INTEGER REFERENCES units(id) ON DELETE SET NULL,
        quantity REAL NOT NULL DEFAULT 1,
        min_quantity REAL,
        expiry TEXT,
        notes TEXT,
        notified_for TEXT,
        source TEXT,
        source_id TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_items_expiry ON items(expiry);
    """,
]


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with _db_lock, db() as conn:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
        row = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
        current = int(row["value"]) if row else 0
        for idx in range(current, len(MIGRATIONS)):
            log.info("A aplicar migração da base de dados v%d", idx + 1)
            conn.executescript(MIGRATIONS[idx])
            conn.execute(
                "INSERT INTO meta(key, value) VALUES('schema_version', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(idx + 1),),
            )


def meta_get(key: str) -> str | None:
    with db() as conn:
        row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None


def meta_set(key: str, value: str) -> None:
    with _db_lock, db() as conn:
        conn.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


def rows(conn, sql, args=()):
    return [dict(r) for r in conn.execute(sql, args).fetchall()]


def get_state() -> dict:
    opts = load_options()
    nd = opts["notify_days"]
    today = today_local()
    with db() as conn:
        items = rows(conn, "SELECT * FROM items")
        cats = rows(conn, "SELECT * FROM categories")
        locs = rows(conn, "SELECT * FROM locations")
        units = rows(conn, "SELECT * FROM units")
    items.sort(key=lambda r: sort_key(r["name"]))
    for lst in (cats, locs, units):
        lst.sort(key=lambda r: sort_key(r["name"]))
    stats = {"total": 0, "soon": 0, "expired": 0, "missing": 0, "low": 0}
    for it in items:
        it.pop("notified_for", None)
        it["days_left"] = days_left(it["expiry"], today)
        it["status"] = item_status(it, nd)
        if it["status"] != "missing":
            stats["total"] += 1
        if it["status"] in stats:
            stats[it["status"]] += 1
    return {
        "version": VERSION,
        "today": today.isoformat(),
        "language": resolve_language(opts),
        "notify": {
            "enabled": bool(opts["notify_enabled"]),
            "days": nd,
            "time": opts["notify_time"],
            "service": opts["notify_service"],
            "ha_connected": bool(SUPERVISOR_TOKEN),
        },
        "items": items,
        "categories": cats,
        "locations": locs,
        "units": units,
        "stats": stats,
    }


class ApiError(Exception):
    def __init__(self, code: str, status: int = 400, detail: str = ""):
        super().__init__(code)
        self.code = code
        self.status = status
        self.detail = detail


def _num(value, field, allow_none=False):
    if value is None or value == "":
        if allow_none:
            return None
        raise ApiError(f"invalid_{field}")
    try:
        n = float(str(value).replace(",", "."))
    except ValueError as exc:
        raise ApiError(f"invalid_{field}") from exc
    if n < 0 or n > 1_000_000 or n != n:
        raise ApiError(f"invalid_{field}")
    return round(n, 3)


def _ref(conn, table, value):
    if value in (None, "", 0, "0"):
        return None
    try:
        ref = int(value)
    except (TypeError, ValueError) as exc:
        raise ApiError(f"invalid_{table}") from exc
    if not conn.execute(f"SELECT 1 FROM {table} WHERE id=?", (ref,)).fetchone():  # noqa: S608
        raise ApiError(f"invalid_{table}")
    return ref


def validate_item(conn, data: dict, partial_base: dict | None = None) -> dict:
    base = dict(partial_base or {})
    base.update(data or {})
    name = str(base.get("name") or "").strip()
    if not name or len(name) > 120:
        raise ApiError("invalid_name")
    notes = str(base.get("notes") or "").strip()
    if len(notes) > 4000:
        raise ApiError("invalid_notes")
    try:
        expiry = normalize_expiry(base.get("expiry"))
    except ValueError as exc:
        raise ApiError("invalid_expiry") from exc
    return {
        "name": name,
        "quantity": _num(base.get("quantity", 1), "quantity"),
        "min_quantity": _num(base.get("min_quantity"), "min_quantity", allow_none=True),
        "expiry": expiry,
        "notes": notes or None,
        "category_id": _ref(conn, "categories", base.get("category_id")),
        "location_id": _ref(conn, "locations", base.get("location_id")),
        "unit_id": _ref(conn, "units", base.get("unit_id")),
    }


def create_item(data: dict) -> int:
    with _db_lock, db() as conn:
        v = validate_item(conn, data)
        now = iso_now()
        cur = conn.execute(
            "INSERT INTO items(name, quantity, min_quantity, expiry, notes, category_id, location_id, unit_id, "
            "source, created_at, updated_at) VALUES(?,?,?,?,?,?,?,?, 'manual', ?, ?)",
            (v["name"], v["quantity"], v["min_quantity"], v["expiry"], v["notes"], v["category_id"],
             v["location_id"], v["unit_id"], now, now),
        )
        new_id = cur.lastrowid
    _sensor_dirty.set()
    return new_id


def update_item(item_id: int, data: dict) -> None:
    with _db_lock, db() as conn:
        row = conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
        if not row:
            raise ApiError("not_found", 404)
        v = validate_item(conn, data, dict(row))
        conn.execute(
            "UPDATE items SET name=?, quantity=?, min_quantity=?, expiry=?, notes=?, category_id=?, "
            "location_id=?, unit_id=?, updated_at=? WHERE id=?",
            (v["name"], v["quantity"], v["min_quantity"], v["expiry"], v["notes"], v["category_id"],
             v["location_id"], v["unit_id"], iso_now(), item_id),
        )
    _sensor_dirty.set()


def adjust_item(item_id: int, delta) -> None:
    try:
        d = float(delta)
    except (TypeError, ValueError) as exc:
        raise ApiError("invalid_quantity") from exc
    with _db_lock, db() as conn:
        row = conn.execute("SELECT quantity FROM items WHERE id=?", (item_id,)).fetchone()
        if not row:
            raise ApiError("not_found", 404)
        q = max(0.0, round((row["quantity"] or 0) + d, 3))
        conn.execute("UPDATE items SET quantity=?, updated_at=? WHERE id=?", (q, iso_now(), item_id))
    _sensor_dirty.set()


def delete_item(item_id: int) -> None:
    with _db_lock, db() as conn:
        cur = conn.execute("DELETE FROM items WHERE id=?", (item_id,))
        if cur.rowcount == 0:
            raise ApiError("not_found", 404)
    _sensor_dirty.set()


LOOKUPS = {
    "categories": ("name", "icon", "color", "sort"),
    "locations": ("name", "sort"),
    "units": ("name", "name_plural", "sort"),
}


def _lookup_values(kind: str, data: dict, existing: dict | None = None) -> dict:
    base = dict(existing or {})
    base.update({k: v for k, v in (data or {}).items() if k in LOOKUPS[kind]})
    name = str(base.get("name") or "").strip()
    if not name or len(name) > 60:
        raise ApiError("invalid_name")
    out = {"name": name, "sort": int(base.get("sort") or 0)}
    if kind == "categories":
        icon = str(base.get("icon") or "").strip()[:8] or guess_emoji(name)
        color = str(base.get("color") or "").strip()
        out.update(icon=icon, color=color if color in CATEGORY_COLORS else None)
    if kind == "units":
        out["name_plural"] = (str(base.get("name_plural") or "").strip()[:60]) or None
    return out


def _check_unique(conn, kind: str, name: str, exclude_id: int | None = None) -> None:
    """O SQLite só ignora maiúsculas em ASCII; aqui também apanha 'água' vs 'Água'."""
    key = name.casefold()
    for r in conn.execute(f"SELECT id, name FROM {kind}"):  # noqa: S608
        if r["id"] != exclude_id and str(r["name"]).casefold() == key:
            raise ApiError("duplicate_name", 409)


def create_lookup(kind: str, data: dict) -> int:
    with _db_lock, db() as conn:
        v = _lookup_values(kind, data)
        _check_unique(conn, kind, v["name"])
        if kind == "categories" and not v["color"]:
            count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
            v["color"] = CATEGORY_COLORS[count % len(CATEGORY_COLORS)]
        cols = ", ".join(v)
        try:
            cur = conn.execute(
                f"INSERT INTO {kind}({cols}) VALUES({', '.join('?' * len(v))})",  # noqa: S608
                tuple(v.values()),
            )
        except sqlite3.IntegrityError as exc:
            raise ApiError("duplicate_name", 409) from exc
        return cur.lastrowid


def update_lookup(kind: str, ref: int, data: dict) -> None:
    with _db_lock, db() as conn:
        row = conn.execute(f"SELECT * FROM {kind} WHERE id=?", (ref,)).fetchone()  # noqa: S608
        if not row:
            raise ApiError("not_found", 404)
        v = _lookup_values(kind, data, dict(row))
        _check_unique(conn, kind, v["name"], ref)
        if kind == "categories" and not v["color"]:
            v["color"] = row["color"]
        sets = ", ".join(f"{k}=?" for k in v)
        try:
            conn.execute(f"UPDATE {kind} SET {sets} WHERE id=?", (*v.values(), ref))  # noqa: S608
        except sqlite3.IntegrityError as exc:
            raise ApiError("duplicate_name", 409) from exc
    _sensor_dirty.set()


def delete_lookup(kind: str, ref: int) -> None:
    with _db_lock, db() as conn:
        cur = conn.execute(f"DELETE FROM {kind} WHERE id=?", (ref,))  # noqa: S608
        if cur.rowcount == 0:
            raise ApiError("not_found", 404)


# ---------------------------------------------------------------------------
# Cópia de segurança (exportar / restaurar)
# ---------------------------------------------------------------------------

def export_data() -> dict:
    with db() as conn:
        return {
            "app": "kit_sos",
            "format": 1,
            "version": VERSION,
            "exported_at": iso_now(),
            "categories": rows(conn, "SELECT * FROM categories"),
            "locations": rows(conn, "SELECT * FROM locations"),
            "units": rows(conn, "SELECT * FROM units"),
            "items": rows(conn, "SELECT * FROM items"),
        }


def restore_data(payload: dict) -> dict:
    if not isinstance(payload, dict) or payload.get("app") != "kit_sos":
        raise ApiError("invalid_backup")
    with _db_lock, db() as conn:
        conn.execute("DELETE FROM items")
        for kind in LOOKUPS:
            conn.execute(f"DELETE FROM {kind}")  # noqa: S608
        for kind, cols in (("categories", ("id", "name", "icon", "color", "sort")),
                           ("locations", ("id", "name", "sort")),
                           ("units", ("id", "name", "name_plural", "sort"))):
            for r in payload.get(kind) or []:
                conn.execute(
                    f"INSERT INTO {kind}({', '.join(cols)}) VALUES({', '.join('?' * len(cols))})",  # noqa: S608
                    tuple(r.get(c) if c != "sort" else (r.get(c) or 0) for c in cols),
                )
        cols = ("id", "name", "category_id", "location_id", "unit_id", "quantity", "min_quantity", "expiry",
                "notes", "notified_for", "source", "source_id", "created_at", "updated_at")
        for r in payload.get("items") or []:
            values = []
            for c in cols:
                val = r.get(c)
                if c == "expiry":
                    try:
                        val = normalize_expiry(val)
                    except ValueError:
                        val = None
                values.append(val)
            conn.execute(
                f"INSERT INTO items({', '.join(cols)}) VALUES({', '.join('?' * len(cols))})",  # noqa: S608
                tuple(values),
            )
        counts = {k: conn.execute(f"SELECT COUNT(*) FROM {k}").fetchone()[0]  # noqa: S608
                  for k in ("items", "categories", "locations", "units")}
    _sensor_dirty.set()
    return counts


# ---------------------------------------------------------------------------
# Importação do Grocy
# ---------------------------------------------------------------------------

def _grocy_base(url: str) -> str:
    url = (url or "").strip().rstrip("/")
    if not url:
        raise ApiError("grocy_url_missing")
    if not re.match(r"^https?://", url):
        url = "http://" + url
    if url.endswith("/api"):
        url = url[:-4]
    return url


def grocy_get(base: str, api_key: str, path: str):
    req = urllib.request.Request(
        f"{base}/api{path}",
        headers={"GROCY-API-KEY": api_key, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise ApiError("grocy_auth", 400) from exc
        raise ApiError("grocy_http", 400, f"HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ApiError("grocy_unreachable", 400, str(getattr(exc, "reason", exc))) from exc
    except json.JSONDecodeError as exc:
        raise ApiError("grocy_invalid", 400) from exc


def build_grocy_plan(url: str, api_key: str) -> dict:
    base = _grocy_base(url)
    if not api_key:
        raise ApiError("grocy_key_missing")
    products = grocy_get(base, api_key, "/objects/products")
    groups = grocy_get(base, api_key, "/objects/product_groups")
    locations = grocy_get(base, api_key, "/objects/locations")
    units = grocy_get(base, api_key, "/objects/quantity_units")
    stock = grocy_get(base, api_key, "/objects/stock")
    if not all(isinstance(x, list) for x in (products, groups, locations, units, stock)):
        raise ApiError("grocy_invalid")

    def active(obj):
        return str(obj.get("active", 1)) not in ("0", "false", "False")

    prod_by_id = {str(p["id"]): p for p in products}
    items: list[dict] = []
    skipped_inactive = 0
    merged: dict[tuple, dict] = {}
    for entry in stock:
        prod = prod_by_id.get(str(entry.get("product_id")))
        if not prod:
            continue
        if not active(prod):
            continue
        bbd = (entry.get("best_before_date") or "")[:10]
        expiry = None if (not bbd or bbd >= NO_EXPIRY_GROCY) else bbd
        loc = entry.get("location_id") or prod.get("location_id")
        key = (str(prod["id"]), expiry, str(loc))
        try:
            amount = float(entry.get("amount") or 0)
        except (TypeError, ValueError):
            amount = 0.0
        note = (entry.get("note") or "").strip()
        if key in merged:
            merged[key]["quantity"] += amount
            if note and note not in (merged[key]["_notes"]):
                merged[key]["_notes"].append(note)
        else:
            merged[key] = {"product": prod, "expiry": expiry, "location": loc, "quantity": amount,
                           "_notes": [note] if note else [], "source_id": str(entry.get("id"))}

    with_stock = {k[0] for k in merged}
    for k, m in merged.items():
        items.append(m)
    no_stock = 0
    for p in products:
        if not active(p):
            skipped_inactive += 1
            continue
        if str(p["id"]) not in with_stock:
            no_stock += 1
            items.append({"product": p, "expiry": None, "location": p.get("location_id"), "quantity": 0.0,
                          "_notes": [], "source_id": None})

    return {
        "groups": [g for g in groups if active(g)],
        "locations": [l for l in locations if active(l)],
        "units": [u for u in units if active(u)],
        "items": items,
        "summary": {
            "products": sum(1 for p in products if active(p)),
            "items": len(items),
            "with_expiry": sum(1 for i in items if i["expiry"]),
            "without_stock": no_stock,
            "categories": sum(1 for g in groups if active(g)),
            "locations": sum(1 for l in locations if active(l)),
            "units": sum(1 for u in units if active(u)),
            "skipped_inactive": skipped_inactive,
        },
    }


def import_grocy(url: str, api_key: str, dry_run: bool = True) -> dict:
    plan = build_grocy_plan(url, api_key)
    if dry_run:
        with db() as conn:
            existing = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        return {"dry_run": True, "summary": plan["summary"], "existing_items": existing}

    now = iso_now()
    with _db_lock, db() as conn:
        conn.execute("DELETE FROM items")
        for kind in LOOKUPS:
            conn.execute(f"DELETE FROM {kind}")  # noqa: S608
        cat_map, loc_map, unit_map = {}, {}, {}
        for i, g in enumerate(sorted(plan["groups"], key=lambda x: sort_key(x.get("name", "")))):
            name = str(g.get("name") or "").strip()[:60] or f"Grupo {g['id']}"
            cur = conn.execute(
                "INSERT OR IGNORE INTO categories(name, icon, color, sort) VALUES(?,?,?,?)",
                (name, guess_emoji(name), CATEGORY_COLORS[i % len(CATEGORY_COLORS)], i),
            )
            cat_map[str(g["id"])] = cur.lastrowid or conn.execute(
                "SELECT id FROM categories WHERE name=?", (name,)).fetchone()[0]
        for i, l in enumerate(plan["locations"]):
            name = str(l.get("name") or "").strip()[:60] or f"Local {l['id']}"
            cur = conn.execute("INSERT OR IGNORE INTO locations(name, sort) VALUES(?,?)", (name, i))
            loc_map[str(l["id"])] = cur.lastrowid or conn.execute(
                "SELECT id FROM locations WHERE name=?", (name,)).fetchone()[0]
        for i, u in enumerate(plan["units"]):
            name = str(u.get("name") or "").strip()[:60] or f"Unidade {u['id']}"
            plural = str(u.get("name_plural") or "").strip()[:60] or None
            cur = conn.execute("INSERT OR IGNORE INTO units(name, name_plural, sort) VALUES(?,?,?)",
                               (name, plural, i))
            unit_map[str(u["id"])] = cur.lastrowid or conn.execute(
                "SELECT id FROM units WHERE name=?", (name,)).fetchone()[0]

        count = 0
        for it in plan["items"]:
            p = it["product"]
            notes = [strip_html(p.get("description"))] + it["_notes"]
            notes_txt = "\n".join(n for n in notes if n) or None
            try:
                min_q = float(p.get("min_stock_amount") or 0) or None
            except (TypeError, ValueError):
                min_q = None
            conn.execute(
                "INSERT INTO items(name, category_id, location_id, unit_id, quantity, min_quantity, expiry, notes, "
                "source, source_id, created_at, updated_at) VALUES(?,?,?,?,?,?,?,?, 'grocy', ?, ?, ?)",
                (
                    str(p.get("name") or "?").strip()[:120],
                    cat_map.get(str(p.get("product_group_id"))),
                    loc_map.get(str(it["location"])),
                    unit_map.get(str(p.get("qu_id_stock"))),
                    round(it["quantity"], 3),
                    min_q,
                    it["expiry"],
                    notes_txt,
                    it["source_id"],
                    now,
                    now,
                ),
            )
            count += 1
    log.info("Importação do Grocy concluída: %d artigos", count)
    _sensor_dirty.set()
    return {"dry_run": False, "summary": plan["summary"], "imported": count}


# ---------------------------------------------------------------------------
# Home Assistant: serviços, eventos e sensores
# ---------------------------------------------------------------------------

def ha_request(method: str, path: str, payload=None, timeout: int = 15):
    if not SUPERVISOR_TOKEN:
        raise ApiError("ha_unavailable", 503)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        f"{HA_API}{path}",
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {SUPERVISOR_TOKEN}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            body = resp.read().decode("utf-8") or "null"
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise ApiError("ha_error", 502, f"HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ApiError("ha_unavailable", 503, str(exc)) from exc


def fetch_ha_config() -> None:
    """Lê fuso horário e idioma do Home Assistant (com tentativas no arranque)."""
    global _tz, _ha_language
    tz_name = os.environ.get("TZ", "")
    if SUPERVISOR_TOKEN:
        for attempt in range(6):
            try:
                cfg = ha_request("GET", "/config", timeout=10) or {}
                tz_name = cfg.get("time_zone") or tz_name
                _ha_language = cfg.get("language") or ""
                break
            except ApiError as exc:
                log.debug("HA ainda não responde (%s), tentativa %d", exc.detail or exc.code, attempt + 1)
                time.sleep(5)
    try:
        _tz = ZoneInfo(tz_name) if tz_name else timezone.utc
    except ZoneInfoNotFoundError:
        _tz = timezone.utc
    log.info("Fuso horário: %s | idioma: %s", tz_name or "UTC", resolve_language())
    _ready.set()


T = {
    "pt": {
        "title": "Kit SOS",
        "header": "validade a aproximar-se",
        "header_expired": "artigo fora de validade",
        "in_days": "expira daqui a {n} dias",
        "tomorrow": "expira amanhã",
        "today": "expira hoje",
        "ago": "expirou há {n} dias",
        "ago1": "expirou ontem",
        "qty": "Quantidade",
        "loc": "Local",
        "test": "✅ *Kit SOS* — aviso de teste. Se estás a ler isto, os avisos estão a funcionar.",
        "s_expiring": "Kit SOS a expirar",
        "s_expired": "Kit SOS expirados",
        "s_missing": "Kit SOS em falta",
        "s_total": "Kit SOS artigos",
        "unit": "artigos",
    },
    "en": {
        "title": "Kit SOS",
        "header": "expiry coming up",
        "header_expired": "item past its expiry date",
        "in_days": "expires in {n} days",
        "tomorrow": "expires tomorrow",
        "today": "expires today",
        "ago": "expired {n} days ago",
        "ago1": "expired yesterday",
        "qty": "Quantity",
        "loc": "Location",
        "test": "✅ *Kit SOS* — test notification. If you can read this, notifications work.",
        "s_expiring": "Kit SOS expiring",
        "s_expired": "Kit SOS expired",
        "s_missing": "Kit SOS low stock",
        "s_total": "Kit SOS items",
        "unit": "items",
    },
}


def md_escape(text: str) -> str:
    return re.sub(r"([_*`\[])", r"\\\1", text or "")


def fmt_expiry(expiry: str, lang: str) -> str:
    m = EXPIRY_RE.match(expiry or "")
    if not m:
        return expiry or ""
    if m.group(3):
        return f"{m.group(3)}/{m.group(2)}/{m.group(1)}"
    return f"{m.group(2)}/{m.group(1)}"


def when_text(days: int, lang: str) -> str:
    t = T[lang]
    if days > 1:
        return t["in_days"].format(n=days)
    if days == 1:
        return t["tomorrow"]
    if days == 0:
        return t["today"]
    if days == -1:
        return t["ago1"]
    return t["ago"].format(n=-days)


def build_message(item: dict, days: int, lang: str, markdown: bool) -> str:
    t = T[lang]
    esc = md_escape if markdown else (lambda s: s or "")
    bold = (lambda s: f"*{s}*") if markdown else (lambda s: s)
    head = t["header_expired"] if days < 0 else t["header"]
    icon = "⛔️" if days < 0 else "⏰"
    unit = item.get("unit_plural") if (item.get("quantity") or 0) != 1 and item.get("unit_plural") else item.get("unit")
    lines = [
        f"{icon} {bold('Kit SOS')} — {head}",
        "",
        f"{bold(esc(item['name']))} {when_text(days, lang)} ({fmt_expiry(item['expiry'], lang)}).",
        f"{t['qty']}: {fmt_qty(item.get('quantity'))}{(' ' + esc(unit)) if unit else ''}",
    ]
    if item.get("location"):
        lines.append(f"{t['loc']}: {esc(item['location'])}")
    return "\n".join(lines)


def send_notification(message_md: str, message_plain: str) -> None:
    opts = load_options()
    service = str(opts.get("notify_service") or "").strip()
    if "." not in service:
        raise ApiError("invalid_service")
    domain, name = service.split(".", 1)
    payload: dict = {}
    if domain == "telegram_bot":
        payload = {"message": message_md, "parse_mode": "markdown"}
    else:
        payload = {"message": message_plain}
        if domain in ("notify", "persistent_notification"):
            payload["title"] = "Kit SOS"
    target = str(opts.get("notify_target") or "").strip()
    if target:
        targets = [t.strip() for t in target.split(",") if t.strip()]
        parsed = [int(t) if re.fullmatch(r"-?\d+", t) else t for t in targets]
        payload["target"] = parsed if len(parsed) > 1 or domain == "telegram_bot" else parsed[0]
    ha_request("POST", f"/services/{domain}/{name}", payload)


def run_expiry_check() -> dict:
    """Envia um aviso por artigo quando faltam <= notify_days dias (uma vez por validade)."""
    opts = load_options()
    lang = resolve_language(opts)
    nd = opts["notify_days"]
    today = today_local()
    sent, failed = 0, 0
    with db() as conn:
        candidates = rows(conn, """
            SELECT i.*, l.name AS location, u.name AS unit, u.name_plural AS unit_plural, c.name AS category
            FROM items i
            LEFT JOIN locations l ON l.id = i.location_id
            LEFT JOIN units u ON u.id = i.unit_id
            LEFT JOIN categories c ON c.id = i.category_id
            WHERE i.expiry IS NOT NULL AND i.quantity > 0
              AND (i.notified_for IS NULL OR i.notified_for <> i.expiry)
        """)
    for it in candidates:
        d = days_left(it["expiry"], today)
        if d is None or d > nd:
            continue
        try:
            send_notification(build_message(it, d, lang, True), build_message(it, d, lang, False))
        except ApiError as exc:
            failed += 1
            log.warning("Falhou o aviso de '%s': %s %s", it["name"], exc.code, exc.detail)
            continue
        sent += 1
        with _db_lock, db() as conn:
            conn.execute("UPDATE items SET notified_for=? WHERE id=?", (it["expiry"], it["id"]))
        try:
            ha_request("POST", "/events/kit_sos_expiring", {
                "id": it["id"], "name": it["name"], "expiry": it["expiry"], "days_left": d,
                "quantity": it["quantity"], "unit": it.get("unit"), "location": it.get("location"),
                "category": it.get("category"),
            })
        except ApiError:
            pass
    if sent or failed:
        log.info("Verificação de validades: %d avisos enviados, %d falharam", sent, failed)
    return {"sent": sent, "failed": failed}


def push_sensors() -> None:
    opts = load_options()
    if not SUPERVISOR_TOKEN or not opts.get("sensors", True):
        return
    lang = resolve_language(opts)
    t = T[lang]
    st = get_state()
    cats = {c["id"]: c["name"] for c in st["categories"]}
    locs = {loc["id"]: loc["name"] for loc in st["locations"]}

    def brief(it):
        return {"name": it["name"], "expiry": it["expiry"], "days_left": it["days_left"],
                "quantity": it["quantity"], "category": cats.get(it["category_id"]),
                "location": locs.get(it["location_id"])}

    soon = sorted((i for i in st["items"] if i["status"] == "soon"), key=lambda i: i["days_left"])
    expired = sorted((i for i in st["items"] if i["status"] == "expired"), key=lambda i: i["days_left"])
    missing = [i for i in st["items"] if i["status"] in ("missing", "low")]
    sensors = [
        ("sensor.kit_sos_expiring", len(soon), t["s_expiring"], "mdi:clock-alert-outline",
         {"items": [brief(i) for i in soon[:50]], "days": opts["notify_days"]}),
        ("sensor.kit_sos_expired", len(expired), t["s_expired"], "mdi:alert-octagon-outline",
         {"items": [brief(i) for i in expired[:50]]}),
        ("sensor.kit_sos_low_stock", len(missing), t["s_missing"], "mdi:package-variant-remove",
         {"items": [brief(i) for i in missing[:50]]}),
        ("sensor.kit_sos_items", st["stats"]["total"], t["s_total"], "mdi:medical-bag", {}),
    ]
    for entity, value, fname, icon, attrs in sensors:
        try:
            ha_request("POST", f"/states/{entity}", {
                "state": value,
                "attributes": {"friendly_name": fname, "icon": icon, "unit_of_measurement": t["unit"],
                               "state_class": "measurement", **attrs},
            })
        except ApiError as exc:
            log.debug("Não consegui atualizar %s: %s", entity, exc.detail or exc.code)
            return


def scheduler_loop() -> None:
    _ready.wait(90)  # espera pelo fuso horário do HA antes de decidir "que dia é hoje"
    last_sensor = 0.0
    while not _stop.is_set():
        try:
            opts = load_options()
            now = now_local()
            today = now.date().isoformat()
            if opts["notify_enabled"] and SUPERVISOR_TOKEN and now.strftime("%H:%M") >= opts["notify_time"] \
                    and meta_get("last_check_date") != today:
                meta_set("last_check_date", today)
                run_expiry_check()
            if _sensor_dirty.is_set() or time.monotonic() - last_sensor > 600 or \
                    meta_get("sensor_day") != today:
                _sensor_dirty.clear()
                last_sensor = time.monotonic()
                meta_set("sensor_day", today)
                push_sensors()
        except Exception:  # noqa: BLE001
            log.exception("Erro no ciclo de tarefas")
        _stop.wait(2 if _sensor_dirty.is_set() else 20)


# ---------------------------------------------------------------------------
# Servidor HTTP
# ---------------------------------------------------------------------------

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".json": "application/json",
    ".ico": "image/x-icon",
}

ROUTE_ITEM = re.compile(r"^/api/items/(\d+)$")
ROUTE_ADJUST = re.compile(r"^/api/items/(\d+)/adjust$")
ROUTE_LOOKUP = re.compile(r"^/api/(categories|locations|units)$")
ROUTE_LOOKUP_ID = re.compile(r"^/api/(categories|locations|units)/(\d+)$")


class Handler(BaseHTTPRequestHandler):
    server_version = f"KitSOS/{VERSION}"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # silencia o log de cada pedido
        log.debug("%s - %s", self.client_address[0], fmt % args)

    # -- utilitários ------------------------------------------------------
    def _allowed(self) -> bool:
        if DEV_MODE or self.client_address[0] == INGRESS_IP:
            return True
        self._send_json({"error": "forbidden"}, 403)
        return False

    def _send(self, status: int, body: bytes, ctype: str, extra: dict | None = None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_json(self, data, status: int = 200, extra: dict | None = None):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8", {"Cache-Control": "no-store", **(extra or {})})

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise ApiError("too_large", 413)
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ApiError("invalid_json") from exc
        if not isinstance(data, dict):
            raise ApiError("invalid_json")
        return data

    def _path(self) -> str:
        return urllib.parse.urlsplit(self.path).path

    def _dispatch(self, method: str):
        if not self._allowed():
            return
        path = self._path()
        try:
            if path.startswith("/api/"):
                return self._api(method, path)
            if method not in ("GET", "HEAD"):
                raise ApiError("not_found", 404)
            return self._static(path)
        except ApiError as exc:
            self._send_json({"error": exc.code, "detail": exc.detail}, exc.status)
        except Exception:  # noqa: BLE001
            log.exception("Erro a tratar %s %s", method, path)
            self._send_json({"error": "internal"}, 500)

    def do_GET(self):
        self._dispatch("GET")

    def do_HEAD(self):
        self._dispatch("HEAD")

    def do_POST(self):
        self._dispatch("POST")

    def do_PUT(self):
        self._dispatch("PUT")

    def do_DELETE(self):
        self._dispatch("DELETE")

    # -- ficheiros estáticos ----------------------------------------------
    def _static(self, path: str):
        rel = "index.html" if path in ("", "/") else path.lstrip("/")
        full = os.path.realpath(os.path.join(STATIC_DIR, rel))
        if not full.startswith(os.path.realpath(STATIC_DIR) + os.sep) or not os.path.isfile(full):
            raise ApiError("not_found", 404)
        with open(full, "rb") as fh:
            body = fh.read()
        ext = os.path.splitext(full)[1].lower()
        if ext == ".html":
            body = body.replace(b"__VERSION__", VERSION.encode())
            cache = "no-cache"
        else:
            cache = "public, max-age=86400"
        self._send(200, body, CONTENT_TYPES.get(ext, "application/octet-stream"), {"Cache-Control": cache})

    # -- API -------------------------------------------------------------
    def _api(self, method: str, path: str):
        if path == "/api/health":
            return self._send_json({"ok": True, "version": VERSION})
        if path == "/api/state" and method == "GET":
            return self._send_json(get_state())
        if path == "/api/items" and method == "POST":
            new_id = create_item(self._body())
            return self._send_json({"id": new_id}, 201)
        m = ROUTE_ITEM.match(path)
        if m:
            item_id = int(m.group(1))
            if method == "PUT":
                update_item(item_id, self._body())
                return self._send_json({"ok": True})
            if method == "DELETE":
                delete_item(item_id)
                return self._send_json({"ok": True})
        m = ROUTE_ADJUST.match(path)
        if m and method == "POST":
            adjust_item(int(m.group(1)), self._body().get("delta", 0))
            return self._send_json({"ok": True})
        m = ROUTE_LOOKUP.match(path)
        if m and method == "POST":
            return self._send_json({"id": create_lookup(m.group(1), self._body())}, 201)
        m = ROUTE_LOOKUP_ID.match(path)
        if m:
            kind, ref = m.group(1), int(m.group(2))
            if method == "PUT":
                update_lookup(kind, ref, self._body())
                return self._send_json({"ok": True})
            if method == "DELETE":
                delete_lookup(kind, ref)
                return self._send_json({"ok": True})
        if path == "/api/import/grocy" and method == "POST":
            b = self._body()
            return self._send_json(import_grocy(b.get("url", ""), str(b.get("api_key", "")).strip(),
                                                dry_run=bool(b.get("dry_run", True))))
        if path == "/api/export" and method == "GET":
            stamp = today_local().isoformat()
            return self._send_json(export_data(), extra={
                "Content-Disposition": f'attachment; filename="kit-sos-{stamp}.json"'})
        if path == "/api/import/backup" and method == "POST":
            return self._send_json({"ok": True, "counts": restore_data(self._body())})
        if path == "/api/notify/test" and method == "POST":
            lang = resolve_language()
            msg = T[lang]["test"]
            send_notification(msg, msg.replace("*", ""))
            return self._send_json({"ok": True})
        if path == "/api/notify/check" and method == "POST":
            return self._send_json(run_expiry_check())
        raise ApiError("not_found", 404)


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):  # ligações cortadas não são erros
        import sys
        if isinstance(sys.exc_info()[1], (ConnectionResetError, BrokenPipeError, TimeoutError)):
            return
        super().handle_error(request, client_address)


def main() -> None:
    log.info("Kit SOS %s a arrancar (porta %d%s)", VERSION, PORT, ", modo DEV" if DEV_MODE else "")
    init_db()
    threading.Thread(target=fetch_ha_config, daemon=True).start()
    threading.Thread(target=scheduler_loop, daemon=True).start()
    httpd = Server(("0.0.0.0", PORT), Handler)  # noqa: S104
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        _stop.set()
        httpd.server_close()


if __name__ == "__main__":
    main()
