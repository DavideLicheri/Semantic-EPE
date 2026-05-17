"""
ISPRA SPARQL Service
Query live sul triplestore ISPRA EPE (dati.isprambiente.it)
Modello Darwin-SW 1.0 + Darwin Core + ISPRA Inspire-MF

Architettura dei grafi:
  obs/  → occurrence, identification, event  (predicati DSW/DWC)
  org/  → organism  (join key cross-graph, solo rdf:type Entity)
  taxon/→ taxon (specie EURING)
"""
import requests
from typing import List, Dict, Optional

ENDPOINT = "https://dati.isprambiente.it/sparql"

G_OBS   = "https://w3id.org/italia/env/ld/euring/obs/"
G_ORG   = "https://w3id.org/italia/env/ld/euring/org/"
G_TAXON = "https://w3id.org/italia/env/ld/euring/taxon/"

FIRST_CAPTURE_URI = "https://w3id.org/italia/env/vocab/euring/capture_types/first_capture"
RECAPTURE_URI     = "https://w3id.org/italia/env/vocab/euring/capture_types/recapture"

PREFIXES = """\
PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dwc:    <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri: <http://rs.tdwg.org/dwc/iri/>
PREFIX dsw:    <http://purl.org/dsw/>
PREFIX sem:    <http://semanticweb.cs.vu.nl/2009/11/sem/>
"""


def _run(query: str) -> List[Dict]:
    resp = requests.get(
        ENDPOINT,
        params={"query": query, "format": "application/sparql-results+json"},
        timeout=45,
    )
    resp.raise_for_status()
    return resp.json().get("results", {}).get("bindings", [])


def _v(binding: Dict, key: str) -> Optional[str]:
    b = binding.get(key)
    return b["value"] if b else None


def _local(uri: str) -> str:
    return uri.split("/")[-1]


# ──────────────────────────────────────────────────────────
# 1. Schemi di inanellamento
# ──────────────────────────────────────────────────────────

def get_ringing_schemes() -> List[Dict]:
    """Schemi (organizzazioni) che hanno eseguito almeno un first_capture."""
    query = PREFIXES + f"""
SELECT DISTINCT ?scheme ?label
WHERE {{
  GRAPH <{G_OBS}> {{
    ?occ dwciri:recordedBy ?scheme .
    ?occ dsw:atEvent       ?event .
    ?event sem:eventType   <{FIRST_CAPTURE_URI}> .
  }}
  OPTIONAL {{ ?scheme rdfs:label ?label }}
}}
ORDER BY ?scheme
"""
    rows = _run(query)
    result = []
    for b in rows:
        uri = _v(b, "scheme")
        if not uri:
            continue
        result.append({
            "uri": uri,
            "code": _local(uri),
            "label": _v(b, "label") or _local(uri),
        })
    return result


# ──────────────────────────────────────────────────────────
# 2. Specie per schema (cross-graph: obs + org)
# ──────────────────────────────────────────────────────────

def get_species_for_scheme(scheme_uri: str) -> List[Dict]:
    """
    Specie degli individui inanellati dallo schema indicato.
    Join cross-graph: identification (obs) → organism (condiviso) ← occurrence (obs)
    """
    query = PREFIXES + f"""
SELECT DISTINCT ?taxon
FROM <{G_OBS}>
WHERE {{
  ?ringOcc dwciri:recordedBy <{scheme_uri}> .
  ?ringOcc dsw:atEvent       ?ringEvent .
  ?ringEvent sem:eventType   <{FIRST_CAPTURE_URI}> .
  ?ringOcc dsw:occurrenceOf  ?organism .
  ?ident dsw:identifies      ?organism .
  ?ident dwciri:toTaxon      ?taxon .
}}
ORDER BY ?taxon
"""
    rows = _run(query)
    result = []
    seen = set()
    for b in rows:
        uri = _v(b, "taxon")
        if not uri or uri in seen:
            continue
        seen.add(uri)
        code = _local(uri)
        result.append({"uri": uri, "code": code, "label": code})
    return result


# ──────────────────────────────────────────────────────────
# 3. Anni disponibili per schema + specie
# ──────────────────────────────────────────────────────────

def get_years_for_scheme_species(scheme_uri: str, taxon_uri: str) -> List[int]:
    """Anni con almeno una occorrenza per individui (schema + specie)."""
    query = PREFIXES + f"""
SELECT DISTINCT (YEAR(?date) AS ?year)
FROM <{G_OBS}>
WHERE {{
  ?ringOcc dwciri:recordedBy <{scheme_uri}> .
  ?ringOcc dsw:atEvent       ?ringEvent .
  ?ringEvent sem:eventType   <{FIRST_CAPTURE_URI}> .
  ?ringOcc dsw:occurrenceOf  ?organism .
  ?ident dsw:identifies      ?organism .
  ?ident dwciri:toTaxon      <{taxon_uri}> .
  ?occ dsw:occurrenceOf      ?organism .
  ?occ dsw:atEvent           ?event .
  ?event dwc:eventDate       ?date .
}}
ORDER BY ?year
"""
    rows = _run(query)
    return [int(_v(b, "year")) for b in rows if _v(b, "year")]


# ──────────────────────────────────────────────────────────
# 4. Record: inanellamento + occorrenze nell'anno target
# ──────────────────────────────────────────────────────────

def query_records(scheme_uri: str, taxon_uri: str, year: int) -> List[Dict]:
    """
    Per ogni individuo (schema + specie) con almeno una occorrenza nell'anno,
    restituisce dati di inanellamento + occorrenze di quell'anno.
    """
    query = PREFIXES + f"""
SELECT ?organism ?ringDate ?ringPlace ?occDate ?occEventType ?occPlace
FROM <{G_OBS}>
WHERE {{
  ?ringOcc dsw:occurrenceOf  ?organism .
  ?ringOcc dsw:atEvent       ?ringEvent .
  ?ringEvent sem:eventType   <{FIRST_CAPTURE_URI}> .
  ?ringEvent dwc:eventDate   ?ringDate .
  ?ringOcc dwciri:recordedBy <{scheme_uri}> .
  OPTIONAL {{ ?ringEvent dwc:locatedAt ?ringPlace }}

  ?ident dsw:identifies      ?organism .
  ?ident dwciri:toTaxon      <{taxon_uri}> .

  ?occ dsw:occurrenceOf      ?organism .
  ?occ dsw:atEvent           ?occEvent .
  ?occEvent dwc:eventDate    ?occDate .
  ?occEvent sem:eventType    ?occEventType .
  OPTIONAL {{ ?occEvent dwc:locatedAt ?occPlace }}
  FILTER(YEAR(?occDate) = {year})
}}
ORDER BY ?organism ?occDate
LIMIT 2000
"""
    rows = _run(query)

    organisms: Dict[str, Dict] = {}
    seen_occs: Dict[str, set] = {}  # org_uri → set of (date, place) già viste

    for b in rows:
        org_uri = _v(b, "organism")
        if not org_uri:
            continue

        if org_uri not in organisms:
            ring_place_uri = _v(b, "ringPlace")
            org_local = _local(org_uri)
            parts = org_local.split("_", 1)
            ring_id = parts[1] if len(parts) == 2 else org_local

            organisms[org_uri] = {
                "organism_uri": org_uri,
                "ring_id": ring_id,
                "scheme_code": _local(scheme_uri),
                "species_code": _local(taxon_uri),
                "ring_date": _v(b, "ringDate"),
                "ring_place_code": _local(ring_place_uri) if ring_place_uri else None,
                "occurrences": [],
            }
            seen_occs[org_uri] = set()

        occ_date = _v(b, "occDate")
        evt_type_uri = _v(b, "occEventType")
        occ_place_uri = _v(b, "occPlace")
        occ_key = (occ_date, occ_place_uri)

        if occ_date and occ_key not in seen_occs[org_uri]:
            seen_occs[org_uri].add(occ_key)
            organisms[org_uri]["occurrences"].append({
                "date": occ_date,
                "event_type": (
                    "first_capture" if evt_type_uri and "first_capture" in evt_type_uri
                    else "recapture"
                ),
                "place_code": _local(occ_place_uri) if occ_place_uri else None,
            })

    return list(organisms.values())
