"""
Rate limiting essenziale per l'account 'lizzy' (priorita' #5 del punch-list,
completata 05/09/2026 -- vedi HANDOFF.md).

Contesto/decisioni (checkpoint esplicito con Davide, 05/09/2026 -- nessuna
scelta qui non discussa):

- Minacce da coprire (entrambe scelte da Davide): (a) Lizzy (qwen2.5 via
  Open WebUI) che richiama uno strumento ripetutamente per errore di
  ragionamento, sovraccaricando ECES/la VM; (b) abuso esterno generico di
  questi endpoint, che accettano credenziali facoltative
  (get_current_user_optional).
- Ambito ESPLICITAMENTE limitato al solo account 'lizzy': NON un limite
  generale per tutti gli utenti loggati, NON un limite per IP per le
  chiamate anonime. Scelta consapevole di Davide tra le opzioni proposte
  (solo lizzy / per IP su tutta l'API / entrambi) -- se in futuro emergesse
  davvero abuso anonimo, va riaperta la discussione, non estesa qui
  unilateralmente.
- Soglia: 30 richieste/minuto.
- Budget CONDIVISO tra i 4 endpoint che Lizzy chiama davvero (recognize,
  convert, field info, field lookup -- vedi CLAUDE.md, tabella "Strumenti
  Open WebUI configurati": eces_species_lookup legge un CSV locale e
  ispra_species_lookup interroga SPARQL esterno, nessuno dei due passa da
  qui) -- un unico contatore, non uno per endpoint, per proteggere dal
  carico complessivo piuttosto che permettere di aggirare il limite
  distribuendo le chiamate tra endpoint diversi.

Implementazione in memoria di processo (nessun Redis nello stack ECES,
vedi requirements.txt) -- adeguata a un singolo processo uvicorn su una
VM. Limite noto, accettato: NON persiste tra riavvii del processo e NON
sarebbe condiviso se in futuro ECES girasse su piu' worker/processi
(nessuno dei due casi si applica oggi).
"""
import time
from collections import deque
from typing import Deque, Optional

from fastapi import Depends, HTTPException, status

from .dependencies import get_current_user_optional
from .models import User

# Solo il traffico di questo utente viene conteggiato/limitato.
_LIMITED_USERNAME = "lizzy"
_MAX_REQUESTS = 30
_WINDOW_SECONDS = 60.0

# Timestamp (time.monotonic()) delle richieste recenti di 'lizzy' verso
# uno qualsiasi degli endpoint che usano questa dependency -- budget
# condiviso, non un dict per-endpoint.
_recent_requests: Deque[float] = deque()


async def enforce_lizzy_rate_limit(
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Optional[User]:
    """
    Da usare AL POSTO di get_current_user_optional (non in aggiunta) sui
    4 endpoint che Lizzy chiama davvero. Per chiunque non sia autenticato
    come 'lizzy' (altri utenti reali, o anonimo) e' un no-op: restituisce
    current_user invariato, nessun conteggio, nessun impatto su di loro.
    """
    if current_user is None or current_user.username != _LIMITED_USERNAME:
        return current_user

    now = time.monotonic()
    cutoff = now - _WINDOW_SECONDS

    while _recent_requests and _recent_requests[0] < cutoff:
        _recent_requests.popleft()

    if len(_recent_requests) >= _MAX_REQUESTS:
        retry_after = max(1, int(_recent_requests[0] + _WINDOW_SECONDS - now) + 1)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Limite di {_MAX_REQUESTS} richieste/minuto superato per "
                f"l'account 'lizzy'. Riprova tra {retry_after} secondi."
            ),
            headers={"Retry-After": str(retry_after)},
        )

    _recent_requests.append(now)
    return current_user
