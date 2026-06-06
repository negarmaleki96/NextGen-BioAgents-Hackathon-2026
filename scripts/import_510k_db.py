#!/usr/bin/env python3
"""Stream openFDA 510(k) JSON into SQLite with FTS5 indexes."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

import ijson

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from fda_510k.config import settings  # noqa: E402

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS devices_510k (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    k_number TEXT UNIQUE NOT NULL,
    device_name TEXT,
    applicant TEXT,
    product_code TEXT,
    decision_code TEXT,
    decision_date TEXT,
    clearance_type TEXT,
    statement_or_summary TEXT,
    advisory_committee TEXT,
    regulation_number TEXT,
    device_class TEXT,
    openfda_device_name TEXT
);

CREATE INDEX IF NOT EXISTS idx_product_code ON devices_510k(product_code);
CREATE INDEX IF NOT EXISTS idx_regulation_number ON devices_510k(regulation_number);
CREATE INDEX IF NOT EXISTS idx_device_class ON devices_510k(device_class);
CREATE INDEX IF NOT EXISTS idx_advisory_committee ON devices_510k(advisory_committee);
CREATE INDEX IF NOT EXISTS idx_decision_date ON devices_510k(decision_date);

CREATE VIRTUAL TABLE IF NOT EXISTS devices_510k_fts USING fts5(
    k_number,
    device_name,
    applicant,
    statement_or_summary,
    openfda_device_name,
    content='devices_510k',
    content_rowid='id'
);
"""


def _extract_record(item: dict) -> tuple | None:
    k_number = item.get("k_number")
    if not k_number:
        return None
    openfda = item.get("openfda") or {}
    return (
        k_number,
        item.get("device_name"),
        item.get("applicant"),
        item.get("product_code"),
        item.get("decision_code"),
        item.get("decision_date"),
        item.get("clearance_type"),
        item.get("statement_or_summary"),
        item.get("advisory_committee"),
        openfda.get("regulation_number"),
        openfda.get("device_class"),
        openfda.get("device_name"),
    )


def import_json(json_path: Path, db_path: Path, batch_size: int = 5000) -> int:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)

    insert_sql = """
        INSERT OR REPLACE INTO devices_510k (
            k_number, device_name, applicant, product_code, decision_code,
            decision_date, clearance_type, statement_or_summary,
            advisory_committee, regulation_number, device_class, openfda_device_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    count = 0
    batch: list[tuple] = []

    with json_path.open("rb") as f:
        for item in ijson.items(f, "results.item"):
            row = _extract_record(item)
            if row is None:
                continue
            batch.append(row)
            count += 1
            if len(batch) >= batch_size:
                conn.executemany(insert_sql, batch)
                conn.commit()
                batch.clear()
                print(f"  imported {count:,} records...", flush=True)

    if batch:
        conn.executemany(insert_sql, batch)
        conn.commit()

    # Rebuild FTS index
    conn.execute("INSERT INTO devices_510k_fts(devices_510k_fts) VALUES('rebuild')")
    conn.commit()
    conn.close()
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Import openFDA 510(k) JSON to SQLite")
    parser.add_argument(
        "--json",
        type=Path,
        default=settings.fda_510k_json_path,
        help="Path to openFDA JSON file",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=settings.fda_510k_db_path,
        help="Output SQLite database path",
    )
    parser.add_argument("--batch-size", type=int, default=5000)
    args = parser.parse_args()

    if not args.json.exists():
        print(f"Error: JSON file not found: {args.json}", file=sys.stderr)
        sys.exit(1)

    print(f"Importing {args.json} -> {args.db}")
    total = import_json(args.json, args.db, args.batch_size)
    print(f"Done. Imported {total:,} records.")


if __name__ == "__main__":
    main()
