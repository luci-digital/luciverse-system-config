#!/usr/bin/env python3
"""
FoundationDB hardware ledger schema initializer.

This script creates the key namespaces used to index hardware issuance files
and their associated Hedera sequence logs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    import fdb
except ImportError:  # pragma: no cover - exercised on hosts without bindings
    fdb = None

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_FILE = REPO_ROOT / "schemas" / "foundationdb" / "hardware-ledger.schema.json"
DEFAULT_CLUSTER_FILE = REPO_ROOT / "configs" / "foundationdb" / "fdb.cluster"


def load_schema(schema_file: Path) -> Dict[str, Any]:
    with schema_file.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def normalize_mac(mac: str) -> str:
    return mac.strip().lower().replace("-", ":")


def ensure_fdb():
    if fdb is None:
        raise RuntimeError(
            "The FoundationDB Python bindings are required for init and index operations."
        )


def record_key(*parts: str):
    return fdb.tuple.pack(tuple(parts))


class HardwareLedgerSchema:
    def __init__(self, schema_file: Path, cluster_file: Path):
        self.schema_file = schema_file
        self.cluster_file = cluster_file
        self.schema = load_schema(schema_file)

    def static_verify(self) -> None:
        required_top_level = {"directories", "indexes", "record_types", "schema_name", "version"}
        missing = sorted(required_top_level - set(self.schema))
        if missing:
            raise SystemExit(f"Schema file is missing required keys: {', '.join(missing)}")

        def validate_collection(name: str, required_keys: set[str]) -> None:
            value = self.schema[name]
            if not isinstance(value, list) or not value:
                raise SystemExit(f"Schema section '{name}' must be a non-empty list")
            for index, entry in enumerate(value):
                if not isinstance(entry, dict):
                    raise SystemExit(f"Schema section '{name}' entry {index} must be an object")
                missing_keys = sorted(required_keys - set(entry))
                if missing_keys:
                    raise SystemExit(
                        f"Schema section '{name}' entry {index} is missing: {', '.join(missing_keys)}"
                    )

        validate_collection("directories", {"path", "description"})
        validate_collection("indexes", {"name", "path", "description"})
        validate_collection("record_types", {"name", "description", "required", "fields"})

        print(f"schema: {self.schema['schema_name']} v{self.schema['version']}")
        print(f"directories: {len(self.schema['directories'])}")
        print(f"indexes: {len(self.schema['indexes'])}")
        print(f"record types: {len(self.schema['record_types'])}")

    def _db(self):
        ensure_fdb()
        fdb.api_version(730)
        return fdb.open(str(self.cluster_file))

    def init(self) -> None:
        db = self._db()

        directories = [tuple(entry["path"]) for entry in self.schema["directories"]]
        manifest_key = record_key("luciverse", "hardware", "schema", "manifest")
        manifest_value = json.dumps(
            {
                "schema_name": self.schema["schema_name"],
                "version": self.schema["version"],
                "initialized_at": datetime.now(timezone.utc).isoformat(),
                "source_file": str(self.schema_file),
                "directory_count": len(directories),
                "index_count": len(self.schema["indexes"]),
            },
            indent=2,
        ).encode("utf-8")

        @fdb.transactional
        def _init(tr):
            for path in directories:
                tr[record_key(*path)] = json.dumps(
                    {
                        "path": list(path),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "schema_name": self.schema["schema_name"],
                    }
                ).encode("utf-8")
            tr[manifest_key] = manifest_value

        _init(db)
        print(f"initialized {len(directories)} hardware ledger directories")

    def _store_hardware_record(self, tr, record: Dict[str, Any], source_file: Path) -> None:
        hardware_id = record["hardware_id"]
        serial_number = record["serial_number"]
        mac_addresses = [normalize_mac(mac) for mac in record.get("mac_addresses", [])]
        checksum = record.get("checksum") or sha256_bytes(source_file.read_bytes())
        record["checksum"] = checksum
        record["source_file"] = str(source_file)
        record.setdefault("indexed_at", datetime.now(timezone.utc).isoformat())
        record.setdefault("payload_hash", sha256_text(json.dumps(record, sort_keys=True)))

        tr[record_key("luciverse", "hardware", "issued", hardware_id)] = json.dumps(record, indent=2).encode("utf-8")
        tr[record_key("luciverse", "hardware", "indexes", "by_hardware_id", hardware_id)] = b""
        tr[record_key("luciverse", "hardware", "indexes", "by_serial", serial_number, hardware_id)] = b""

        for mac in mac_addresses:
            tr[record_key("luciverse", "hardware", "indexes", "by_mac", mac, hardware_id)] = b""

        tr[record_key("luciverse", "hardware", "artifacts", checksum)] = json.dumps(
            {
                "hardware_id": hardware_id,
                "source_file": str(source_file),
                "checksum": checksum,
                "record_type": "hardware_issue",
                "indexed_at": record["indexed_at"],
            },
            indent=2,
        ).encode("utf-8")

    def _store_sequence_record(self, tr, record: Dict[str, Any], source_file: Path) -> None:
        sequence_id = record["sequence_id"]
        hardware_id = record["hardware_id"]
        transaction_id = record.get("transaction_id")

        record["source_file"] = str(source_file)
        record.setdefault("indexed_at", datetime.now(timezone.utc).isoformat())
        record.setdefault("payload_hash", sha256_text(json.dumps(record, sort_keys=True)))

        tr[record_key("luciverse", "hardware", "hedera", sequence_id)] = json.dumps(record, indent=2).encode("utf-8")
        tr[record_key("luciverse", "hardware", "indexes", "by_sequence_id", sequence_id)] = b""
        tr[record_key("luciverse", "hardware", "indexes", "by_hardware_id", hardware_id, sequence_id)] = b""

        if transaction_id:
            tr[record_key("luciverse", "hardware", "indexes", "by_transaction_id", transaction_id, sequence_id)] = b""

    def _index_json_file(self, tr, file_path: Path) -> None:
        raw = file_path.read_text(encoding="utf-8")
        payload = json.loads(raw)

        if isinstance(payload, dict) and "hardware_id" in payload and "serial_number" in payload:
            self._store_hardware_record(tr, payload, file_path)
            return

        if isinstance(payload, dict) and "sequence_id" in payload and "hardware_id" in payload:
            self._store_sequence_record(tr, payload, file_path)
            return

        # Unknown JSON structure: preserve the raw artifact with a stable hash.
        digest = sha256_text(raw)
        tr[record_key("luciverse", "hardware", "artifacts", digest)] = json.dumps(
            {
                "source_file": str(file_path),
                "checksum": digest,
                "record_type": "unknown_json",
                "indexed_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        ).encode("utf-8")

    def _index_log_file(self, tr, file_path: Path) -> None:
        raw = file_path.read_text(encoding="utf-8", errors="replace")
        digest = sha256_text(raw)
        record = {
            "sequence_id": file_path.stem,
            "hardware_id": file_path.parent.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "observed",
            "source_file": str(file_path),
            "payload_hash": digest,
            "notes": "Indexed as raw Hedera sequence log text",
            "raw_preview": raw[:1000],
        }
        tr[record_key("luciverse", "hardware", "hedera", record["sequence_id"])] = json.dumps(record, indent=2).encode("utf-8")
        tr[record_key("luciverse", "hardware", "indexes", "by_sequence_id", record["sequence_id"])] = b""
        tr[record_key("luciverse", "hardware", "indexes", "by_hardware_id", record["hardware_id"], record["sequence_id"])] = b""

    def index(self, hardware_dir: Path, hedera_log_dir: Path) -> None:
        db = self._db()
        hardware_files = sorted(
            [path for path in hardware_dir.rglob("*") if path.is_file() and path.suffix.lower() == ".json"]
        )
        log_files = sorted(
            [path for path in hedera_log_dir.rglob("*") if path.is_file() and path.suffix.lower() in {".json", ".jsonl", ".log", ".txt"}]
        )

        @fdb.transactional
        def _index(tr):
            for file_path in hardware_files:
                self._index_json_file(tr, file_path)
            for file_path in log_files:
                if file_path.suffix.lower() == ".json":
                    payload = json.loads(file_path.read_text(encoding="utf-8"))
                    if isinstance(payload, dict) and "sequence_id" in payload and "hardware_id" in payload:
                        self._store_sequence_record(tr, payload, file_path)
                        continue
                self._index_log_file(tr, file_path)

        _index(db)
        print(f"indexed {len(hardware_files)} hardware files and {len(log_files)} Hedera logs")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize and index the LuciVerse hardware ledger schema.")
    parser.add_argument(
        "--schema-file",
        type=Path,
        default=DEFAULT_SCHEMA_FILE,
        help="Path to the hardware ledger schema manifest",
    )
    parser.add_argument(
        "--cluster-file",
        type=Path,
        default=Path(os.environ.get("FDB_CLUSTER_FILE", str(DEFAULT_CLUSTER_FILE))),
        help="Path to the FoundationDB cluster file",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("verify", help="Validate the schema manifest without connecting to FoundationDB")
    subparsers.add_parser("init", help="Create the FoundationDB key namespaces and schema manifest")

    index_parser = subparsers.add_parser("index", help="Index hardware manifests and Hedera logs into FoundationDB")
    index_parser.add_argument("--hardware-dir", type=Path, required=True, help="Directory of hardware JSON manifests")
    index_parser.add_argument("--hedera-log-dir", type=Path, required=True, help="Directory of Hedera sequence logs")

    return parser


def main() -> int:
    args = build_parser().parse_args()
    schema = HardwareLedgerSchema(args.schema_file, args.cluster_file)

    if args.command == "verify":
        schema.static_verify()
        return 0

    if args.command == "init":
        schema.init()
        return 0

    if args.command == "index":
        schema.index(args.hardware_dir, args.hedera_log_dir)
        return 0

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
