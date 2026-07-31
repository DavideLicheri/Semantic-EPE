#!/usr/bin/env python3
"""
Backfill una tantum di alias_id per le righe di euring_2020_canonical
precedenti alla migrazione 003 (backend/app/database/migrations/003_ownership_alias_consent.sql).

Contesto: quella migrazione aggiunge alias_id/owner_username/visibility ma
NON puo' popolare alias_id in puro SQL, perche' richiede di estrarre
'ringing scheme' + 'identification number' dal JSONB parsed_fields e fare
upsert su ring_alias per ciascuna riga -- logica piu' naturale in Python
(vedi commento nella migrazione stessa).

Sicuro da rieseguire piu' volte: agisce solo sulle righe con alias_id IS NULL,
quindi una seconda esecuzione non trova nulla da fare.

Uso (sulla VM, dopo aver applicato la migrazione 003 via psql):
    /opt/eces/venv/bin/python backend/scripts/backfill_ring_alias.py [--dry-run]

Richiede le stesse variabili d'ambiente usate da database_service.py
(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, PGSSLMODE) -- riusa
DatabaseService._get_database_url() per non duplicare quella logica.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Permette di eseguire lo script sia da backend/ che da backend/scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncpg

from app.services.database_service import DatabaseService


async def backfill(dry_run: bool) -> None:
    db_url = DatabaseService()._get_database_url()
    conn = await asyncpg.connect(db_url)

    try:
        rows = await conn.fetch(
            """
            SELECT id, canonical_string, parsed_fields
            FROM euring_2020_canonical
            WHERE alias_id IS NULL
            ORDER BY id
            """
        )

        if not rows:
            print("Nessuna riga con alias_id NULL -- niente da fare.")
            return

        print(f"Trovate {len(rows)} righe senza alias_id.")

        updated = 0
        skipped = 0

        for row in rows:
            parsed_fields = row["parsed_fields"]
            if isinstance(parsed_fields, str):
                parsed_fields = json.loads(parsed_fields)

            ringing_scheme = ((parsed_fields or {}).get("ringing scheme") or "").strip()
            identification_number = ((parsed_fields or {}).get("identification number") or "").strip()

            if not ringing_scheme or not identification_number:
                print(
                    f"  [SKIP] id={row['id']}: 'ringing scheme'/'identification number' "
                    f"mancanti o vuoti nei campi parsati."
                )
                skipped += 1
                continue

            if dry_run:
                print(
                    f"  [DRY-RUN] id={row['id']}: assegnerei alias per "
                    f"({ringing_scheme}, {identification_number})"
                )
                updated += 1
                continue

            async with conn.transaction():
                alias_id = await conn.fetchval(
                    """
                    INSERT INTO ring_alias (ringing_scheme, identification_number)
                    VALUES ($1, $2)
                    ON CONFLICT (ringing_scheme, identification_number)
                    DO UPDATE SET ringing_scheme = EXCLUDED.ringing_scheme
                    RETURNING alias_id
                    """,
                    ringing_scheme,
                    identification_number,
                )
                await conn.execute(
                    "UPDATE euring_2020_canonical SET alias_id = $1 WHERE id = $2",
                    alias_id,
                    row["id"],
                )
            print(f"  [OK] id={row['id']} -> alias_id={alias_id}")
            updated += 1

        print(f"\nCompletato: {updated} aggiornate, {skipped} saltate (campi mancanti).")
        if dry_run:
            print("Nessuna modifica scritta (--dry-run). Rilanciare senza --dry-run per applicare.")

    finally:
        await conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Mostra cosa verrebbe fatto senza scrivere nulla sul database."
    )
    args = parser.parse_args()

    asyncio.run(backfill(dry_run=args.dry_run))
