"""
ISPRA EPE API
Endpoint REST per interrogazioni live sul triplestore ISPRA
(dati.isprambiente.it/sparql) — modello Darwin-SW 1.0
"""
from fastapi import APIRouter, HTTPException, Query
from ..services import ispra_sparql_service as sparql

router = APIRouter(prefix="/api/ispra", tags=["ispra-epe"])


@router.get("/schemes", summary="Schemi di inanellamento")
async def get_schemes():
    """
    Restituisce tutti gli schemi di inanellamento presenti nel dataset ISPRA EPE,
    cioè le organizzazioni che hanno eseguito almeno un primo inanellamento.
    """
    try:
        return sparql.get_ringing_schemes()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SPARQL error: {e}")


@router.get("/species", summary="Specie per schema")
async def get_species(
    scheme: str = Query(..., description="URI dello schema di inanellamento")
):
    """
    Restituisce le specie (codice EURING 5 cifre) degli individui
    inanellati dallo schema indicato.
    """
    try:
        return sparql.get_species_for_scheme(scheme)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SPARQL error: {e}")


@router.get("/years", summary="Anni disponibili per schema + specie")
async def get_years(
    scheme: str = Query(..., description="URI dello schema di inanellamento"),
    taxon: str = Query(..., description="URI del taxon (specie EURING)"),
):
    """
    Anni in cui almeno una occorrenza di un individuo
    (schema + specie) è registrata nel dataset.
    """
    try:
        return sparql.get_years_for_scheme_species(scheme, taxon)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SPARQL error: {e}")


@router.get("/records", summary="Record inanellamento + ricatture")
async def get_records(
    scheme: str = Query(..., description="URI dello schema di inanellamento"),
    taxon: str = Query(..., description="URI del taxon (specie EURING)"),
    year: int = Query(..., description="Anno di almeno una delle occorrenze"),
):
    """
    Per ogni individuo che soddisfa i 3 filtri (schema, specie, anno),
    restituisce il dato di primo inanellamento e le occorrenze nell'anno
    selezionato (che possono essere primo inanellamento o ricatture).
    """
    try:
        return sparql.query_records(scheme, taxon, year)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SPARQL error: {e}")
