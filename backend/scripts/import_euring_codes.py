#!/usr/bin/env python3
"""
Import valori EURING da libreria 'euring' in ECES via API.

Popola valid_values e valid_values_descriptions per:
  - place_code          (2052 voci)
  - current_place_code  (2052 voci, stesso dizionario)
  - ringing_scheme      (~50 voci)
  - circumstances       (~80 voci)

Uso:
    python3 import_euring_codes.py [--base-url http://localhost:8000] [--version 2020]
"""

import argparse
import requests
import sys

try:
    import euring.codes as ec
except ImportError:
    sys.exit(
        "Libreria 'euring' non trovata. Installa con:\n"
        "  pip install euring\n"
        "oppure, per il venv ECES:\n"
        "  /opt/eces/venv/bin/pip install euring"
    )


def get_token(base_url: str) -> str:
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "admin"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def update_field(base_url: str, token: str, field_name: str, version: str, payload: dict) -> dict:
    r = requests.put(
        f"{base_url}/api/euring/field/{field_name}",
        params={"version": version},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def reload(base_url: str, token: str) -> dict:
    r = requests.post(
        f"{base_url}/api/euring/reload",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser(description="Import codici EURING in ECES")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--version", default="2020")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    version = args.version

    print(f"Connessione a {base_url} (versione EURING {version})")
    token = get_token(base_url)
    print("Token OK")

    # 1. Place Code e Current Place Code
    places = ec.load_place_map()
    place_payload = {
        "valid_values_type": "external_reference",
        "valid_values": list(places.keys()),
        "valid_values_descriptions": places,
        "valid_values_source": "euring_place_codes",
        "valid_values_lookup_tool": "eces_field_info",
    }
    print(f"Importing place_code ({len(places)} voci)...")
    print(update_field(base_url, token, "place_code", version, place_payload))
    print("Importing current_place_code...")
    print(update_field(base_url, token, "current_place_code", version, place_payload))

    # 2. Ringing Scheme
    schemes = ec.load_scheme_map()
    scheme_payload = {
        "valid_values_type": "external_reference",
        "valid_values": list(schemes.keys()),
        "valid_values_descriptions": schemes,
        "valid_values_source": "euring_ringing_schemes",
        "valid_values_lookup_tool": "eces_field_info",
    }
    print(f"Importing ringing_scheme ({len(schemes)} voci)...")
    print(update_field(base_url, token, "ringing_scheme", version, scheme_payload))

    # 3. Circumstances (enumeration, lista corta e stabile)
    circs = dict(ec.LOOKUP_CIRCUMSTANCES)
    circ_payload = {
        "valid_values_type": "enumeration",
        "valid_values": list(circs.keys()),
        "valid_values_descriptions": circs,
        "valid_values_source": None,
        "valid_values_lookup_tool": None,
    }
    print(f"Importing circumstances ({len(circs)} voci)...")
    print(update_field(base_url, token, "circumstances", version, circ_payload))

    # Hot reload
    print("Hot reload ECES...")
    print(reload(base_url, token))
    print("Import completato.")


if __name__ == "__main__":
    main()
