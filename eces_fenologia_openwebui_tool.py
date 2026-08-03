"""
title: ECES - Statistiche fenologiche Lizzy (specie/luogo/periodo)
author: ECES
description: Interroga i contatori aggregati e anonimi di ECES per sapere quante volte una combinazione specie+luogo+periodo dell'anno è già stata osservata nei dati storici EURING, e da quanti schemi di inanellamento distinti proviene il dato (dichiarazione di provenienza, non un giudizio di plausibilità).
"""
import requests
from pydantic import BaseModel, Field

# Giorni per mese, calendario di riferimento NON bisestile (fisso, sempre 28
# per febbraio) -- stessa convenzione di backend/app/services/phenology_utils.py:
# 73 pentadi/anno, il 29 febbraio viene fuso nella stessa pentade del 28.
_DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def _date_to_pentad(day: int, month: int) -> int:
    if not (1 <= month <= 12):
        raise ValueError(f"Mese non valido: {month}")
    if month == 2 and day == 29:
        day = 28  # fusione 29/2 -> stessa pentade del 28/2
    if not (1 <= day <= _DAYS_IN_MONTH[month - 1]):
        raise ValueError(f"Giorno non valido per il mese {month}: {day}")
    day_of_year = sum(_DAYS_IN_MONTH[: month - 1]) + day
    return ((day_of_year - 1) // 5) + 1


class Tools:
    class Valves(BaseModel):
        eces_base_url: str = Field(
            default="http://100.77.89.72:8000",
            description="URL base del backend ECES raggiungibile da Open WebUI (Tailscale)",
        )

    def __init__(self):
        self.valves = self.Valves()

    def eces_fenologia(self, species_code: str, place_code: str, day: int, month: int) -> str:
        """
        Restituisce i conteggi storici EURING per una combinazione di specie
        (codice EURING a 5 cifre, es. "12000"), luogo (place_code EURING,
        es. "ES71") e periodo dell'anno (giorno+mese, es. 21 e 8 per il 21
        agosto). Usa questo strumento per domande di fenologia (svernamento,
        migrazione, riproduzione di una specie in un dato luogo/periodo). Il
        risultato include SEMPRE il numero di schemi di inanellamento
        distinti che hanno contribuito al dato: con pochi schemi (es. 1) il
        dato riflette solo l'esperienza di quel/quei paese/i, NON un giudizio
        definitivo di rarità o impossibilità. Dichiara sempre questa
        provenienza nella risposta finale all'utente.
        :param species_code: codice EURING della specie (5 cifre, es. "12000")
        :param place_code: place_code EURING del luogo (es. "ES71", "IT12")
        :param day: giorno del mese (1-31)
        :param month: mese (1-12)
        :return: conteggio totale di osservazioni storiche e numero di schemi di inanellamento distinti coinvolti
        """
        try:
            pentad = _date_to_pentad(int(day), int(month))
        except (ValueError, TypeError) as e:
            return f"Errore nel calcolo del periodo dell'anno: {e}"

        try:
            r = requests.get(
                f"{self.valves.eces_base_url}/api/euring/lizzy/species-place-pentad-stats",
                params={"species_code": species_code, "place_code": place_code, "pentad": pentad},
                timeout=10,
            )
            data = r.json()
        except Exception as e:
            return f"Errore nella chiamata a ECES: {e}"

        if not data.get("success"):
            return "Errore: il servizio ECES non ha restituito un risultato valido."

        total = data.get("total_occurrences", 0)
        distinct_schemes = data.get("distinct_schemes", 0)
        schemes = data.get("schemes", [])

        if total == 0:
            return (
                f"Nessuna osservazione storica trovata in ECES per la specie {species_code} "
                f"nel luogo {place_code} in questo periodo dell'anno (giorno {day}/{month}). "
                f"Questo NON significa che la specie non possa essere presente: riflette solo "
                f"l'assenza di dati storici già raccolti da ECES per questa combinazione."
            )

        schemes_str = ", ".join(f"{s['ringing_scheme']} ({s['count']})" for s in schemes)
        return (
            f"ECES ha registrato {total} osservazione/i storica/che per la specie {species_code} "
            f"nel luogo {place_code} in questo periodo dell'anno (giorno {day}/{month}), "
            f"provenienti da {distinct_schemes} schema/i di inanellamento distinto/i: {schemes_str}. "
            f"Dichiara sempre questo numero di schemi come misura della provenienza del dato: "
            f"con pochi schemi il dato riflette solo l'esperienza di quel/quei paese/i, non una "
            f"conclusione definitiva sulla fenologia della specie."
        )
