"""
Archive Service for ECES
=========================
Orchestrazione dell'archivio deduplicato + a faccette per le stringhe
EURING gestite da ECES (recognize/convert/parse).

Flusso per ogni stringa:
  1. Se non e' gia' in formato euring_2020, prova la conversione semantica
     a euring_2020 (riusando EuringConversionService, la stessa logica gia'
     usata da /api/euring/convert).
  2. Se la conversione fallisce, l'archiviazione si ferma qui (la stringa
     resta comunque nel log normale user_queries, come oggi).
  3. Parsa la stringa 2020 con Euring2020PositionParser (basato su
     euring_2020.json, non su un parser separato -- vedi quel modulo per
     il perche').
  4. Solo se il parsing e' "pulito" (esattamente 64/64 campi -- verificato
     su 12 stringhe reali il 23/07/2026, non tutte le stringhe reali lo
     sono: alcuni centri esportano un sottoinsieme di campi diverso, per
     motivi non ancora noti) la stringa entra nell'archivio a faccette.
     Niente parsing "best effort"/euristico per i casi non puliti --
     deciso esplicitamente il 23/07/2026 per non rischiare di produrre
     faccette con campi mappati male.

L'archiviazione non deve MAI far fallire la richiesta principale
(recognize/convert/parse): ogni eccezione viene loggata e inghiottita.
"""
import logging
from typing import Any, Dict, Optional

from .conversion_service import EuringConversionService
from .skos_manager import SKOSManagerImpl
from .parsers.euring_2020_position_parser import Euring2020PositionParser
from .database_service import database_service

logger = logging.getLogger(__name__)


class ArchiveService:
    def __init__(self):
        # Istanze proprie di conversion_service/skos_manager, non condivise con
        # quelle create in euring_api.py -- stesso pattern di instanziazione
        # gia' in uso nel resto del codice (non c'e' oggi una vera dependency
        # injection). Costo noto e accettato: la cache interna di
        # SKOSManagerImpl viene popolata una seconda volta (dati read-only,
        # nessun problema di correttezza, solo un parse JSON in piu' all'avvio).
        self._conversion_service = EuringConversionService()
        self._skos_manager = SKOSManagerImpl()
        self._parser: Optional[Euring2020PositionParser] = None

    async def _get_parser(self) -> Euring2020PositionParser:
        if self._parser is None:
            version_model = await self._skos_manager.load_version_model()
            euring_2020 = next(v for v in version_model.versions if v.id == "euring_2020")
            self._parser = Euring2020PositionParser(euring_2020)
        return self._parser

    async def archive_string(self, euring_string: str, source_version: str) -> Optional[int]:
        """
        Tenta di archiviare una stringa nell'archivio canonico 2020 a faccette.

        Args:
            euring_string: la stringa cosi' come ricevuta, in source_version
            source_version: uno tra 'euring_1966', 'euring_1979',
                'euring_2000', 'euring_2020'

        Returns:
            canonical_id se archiviata con successo, altrimenti None.
            None NON e' un errore: significa solo che questa stringa non e'
            entrata nell'archivio a faccette (conversione non pulita, o
            parsing non a 64 campi esatti) -- resta comunque nel log
            normale (user_queries), nessun dato viene perso.
        """
        print(f"[DEBUG-ARCHIVE] archive_string chiamata: source_version={source_version!r}", flush=True)
        try:
            euring_string = (euring_string or "").strip()
            if not euring_string:
                return None

            # FIX MINIMO 24/07/2026 (vedi stesso commento in euring_api.py
            # /parse e TODO "Indagine #2" in design_archivio_faccette.md):
            # euring_2020_official e' un secondo file di definizione versione
            # incompleto che a volte viene rilevato al posto di euring_2020
            # per vere stringhe 2020. Qui lo trattiamo come alias solo per
            # non perdere archiviazione quando arriva da /recognize.
            if source_version == "euring_2020_official":
                source_version = "euring_2020"

            if source_version == "euring_2020":
                canonical_string = euring_string
            else:
                result = self._conversion_service.convert_semantic(
                    euring_string, source_version, "euring_2020"
                )
                if not result.get("success") or not result.get("converted_string"):
                    logger.info(
                        f"Archiviazione saltata: conversione {source_version}->euring_2020 "
                        f"non riuscita ({result.get('error', 'motivo sconosciuto')})"
                    )
                    return None
                canonical_string = result["converted_string"].strip()

            parser = await self._get_parser()
            parsed = parser.parse(canonical_string)

            if not parsed["is_clean"]:
                logger.info(
                    f"Archiviazione saltata: parsing non pulito "
                    f"({parsed['field_count']}/{parsed['expected_field_count']} campi) "
                    f"-- {parsed['errors']}"
                )
                return None

            field_positions = {f.name: f.position for f in parser.fields_by_position}

            print(
                f"[DEBUG-ARCHIVE] parsing pulito ({parsed['field_count']} campi), "
                f"chiamo upsert_euring_2020_canonical. is_enabled={getattr(database_service, 'is_enabled', 'N/A')!r}",
                flush=True,
            )
            canonical_id = await database_service.upsert_euring_2020_canonical(
                canonical_string=canonical_string,
                parsed_fields=parsed["fields"],
                field_count=parsed["field_count"],
                field_positions=field_positions,
            )
            print(f"[DEBUG-ARCHIVE] upsert_euring_2020_canonical ha restituito canonical_id={canonical_id!r}", flush=True)

            if canonical_id is not None:
                await database_service.link_unique_string_to_canonical(
                    euring_string, canonical_id
                )

            return canonical_id

        except Exception as e:
            import traceback
            print(f"[DEBUG-ARCHIVE] ECCEZIONE in archive_string: {e!r}", flush=True)
            traceback.print_exc()
            logger.error(f"Errore durante l'archiviazione della stringa: {e}")
            return None


# Istanza globale del servizio
archive_service = ArchiveService()
