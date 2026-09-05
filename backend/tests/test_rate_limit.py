"""
Test per il rate limiting dell'account 'lizzy' (priorita' #5, 05/09/2026).

Logica pura in memoria (nessun Postgres/rete necessari, a differenza delle
verifiche di visibilita' a livelli) -- si presta a un test permanente qui,
non solo a uno script manuale una tantum.
"""
from datetime import datetime

import pytest
from fastapi import HTTPException

from backend.app.auth import rate_limit as rl
from backend.app.auth.models import User, UserRole


def _mk_user(username: str, role: UserRole = UserRole.VIEWER) -> User:
    return User(
        id=username,
        username=username,
        email=f"{username}@example.com",
        full_name=username,
        role=role,
        is_active=True,
        created_at=datetime.now(),
    )


@pytest.fixture(autouse=True)
def _reset_rate_limit_state():
    """Ogni test parte da un contatore pulito -- lo stato e' un modulo-level
    deque condiviso, senza reset esploderebbe l'ordine di esecuzione dei test."""
    rl._recent_requests.clear()
    yield
    rl._recent_requests.clear()


class TestLizzyRateLimit:
    @pytest.mark.asyncio
    async def test_anonymous_and_other_users_are_never_limited(self):
        """Solo 'lizzy' e' soggetta al limite -- chiunque altro (inclusi
        anonimi) deve passare invariato anche ben oltre la soglia di lizzy,
        e non deve incrementare il contatore condiviso."""
        other = _mk_user("test_user", UserRole.USER)

        for _ in range(rl._MAX_REQUESTS * 2):
            result = await rl.enforce_lizzy_rate_limit(other)
            assert result is other

        for _ in range(rl._MAX_REQUESTS * 2):
            result = await rl.enforce_lizzy_rate_limit(None)
            assert result is None

        assert len(rl._recent_requests) == 0, (
            "il traffico di utenti diversi da 'lizzy' non deve mai "
            "incrementare il contatore di rate limit"
        )

    @pytest.mark.asyncio
    async def test_lizzy_allowed_up_to_the_limit(self):
        lizzy = _mk_user("lizzy")

        for _ in range(rl._MAX_REQUESTS):
            result = await rl.enforce_lizzy_rate_limit(lizzy)
            assert result is lizzy

    @pytest.mark.asyncio
    async def test_lizzy_blocked_with_429_after_limit(self):
        lizzy = _mk_user("lizzy")

        for _ in range(rl._MAX_REQUESTS):
            await rl.enforce_lizzy_rate_limit(lizzy)

        with pytest.raises(HTTPException) as exc_info:
            await rl.enforce_lizzy_rate_limit(lizzy)

        assert exc_info.value.status_code == 429
        assert "Retry-After" in exc_info.value.headers
        assert int(exc_info.value.headers["Retry-After"]) > 0

    @pytest.mark.asyncio
    async def test_lizzy_recovers_after_window_slides(self, monkeypatch):
        """Simula il passare del tempo (senza attendere 60s reali):
        una volta che le richieste piu' vecchie escono dalla finestra
        scorrevole, 'lizzy' deve tornare a poter chiamare."""
        lizzy = _mk_user("lizzy")
        current_time = 1_000_000.0
        monkeypatch.setattr(rl.time, "monotonic", lambda: current_time)

        for _ in range(rl._MAX_REQUESTS):
            await rl.enforce_lizzy_rate_limit(lizzy)

        with pytest.raises(HTTPException):
            await rl.enforce_lizzy_rate_limit(lizzy)

        # Facciamo scorrere il tempo oltre la finestra di 60s.
        current_time += rl._WINDOW_SECONDS + 1
        monkeypatch.setattr(rl.time, "monotonic", lambda: current_time)

        result = await rl.enforce_lizzy_rate_limit(lizzy)
        assert result is lizzy
