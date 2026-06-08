from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from .defaults import DEFAULT_DATA
from .paths import user_path

DB_PATH = user_path("document_records.sqlite3")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS document_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                display_name TEXT,
                document_title TEXT,
                product_sku TEXT,
                batch_number TEXT,
                data_json TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def _field_value(data: Dict[str, Any], *names: str) -> str:
    lookup = {str(k).strip().lower(): str(v).strip() for k, v in data.get("product_fields", [])}
    for name in names:
        value = lookup.get(name.lower())
        if value:
            return value
    return ""


def _display_name(data: Dict[str, Any]) -> str:
    product = _field_value(data, "Common Name", "Product Name") or "Untitled Product"
    sku = _field_value(data, "Product SKU#", "Product SKU", "SKU")
    batch = _field_value(data, "Batch #", "Batch Number")
    doc = data.get("document_title", "DOCUMENT")
    parts = [doc, sku, batch, product]
    return " | ".join([p for p in parts if p])


def save_record(data: Dict[str, Any]) -> int:
    payload = dict(data)
    payload.pop("id", None)
    sku = _field_value(data, "Product SKU#", "Product SKU", "SKU")
    batch = _field_value(data, "Batch #", "Batch Number")
    display_name = _display_name(data)
    data_json = json.dumps(payload, ensure_ascii=False, indent=2)

    with get_connection() as conn:
        existing_id = data.get("id")
        if existing_id:
            conn.execute(
                """
                UPDATE document_records
                SET display_name=?, document_title=?, product_sku=?, batch_number=?, data_json=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
                """,
                (display_name, data.get("document_title", ""), sku, batch, data_json, existing_id),
            )
            conn.commit()
            return int(existing_id)

        cur = conn.execute(
            """
            INSERT INTO document_records (display_name, document_title, product_sku, batch_number, data_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (display_name, data.get("document_title", ""), sku, batch, data_json),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_records() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, display_name, document_title, product_sku, batch_number, updated_at
            FROM document_records
            ORDER BY updated_at DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def load_record(record_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM document_records WHERE id=?", (record_id,)).fetchone()
    if not row:
        return None
    data = json.loads(row["data_json"])
    merged = dict(DEFAULT_DATA)
    merged.update(data)
    merged["id"] = int(row["id"])
    return merged
