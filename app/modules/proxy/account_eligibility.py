from __future__ import annotations

from collections.abc import Collection

from app.core.auth import token_expiry_epoch_ms
from app.core.crypto import TokenEncryptor
from app.db.models import Account, AccountStatus

ROUTABLE_STATUSES = (AccountStatus.ACTIVE,)
"""Statuses eligible for new requests and live bridge reuse."""

HARD_OWNER_UNAVAILABLE_STATUSES = frozenset(
    {
        AccountStatus.PAUSED,
        AccountStatus.DEACTIVATED,
        AccountStatus.RATE_LIMITED,
        AccountStatus.QUOTA_EXCEEDED,
        AccountStatus.REAUTH_REQUIRED,
    }
)
"""Statuses a hard continuity owner can sit in while it cannot serve its thread.

Usable directly in SQL. Recovery still requires each caller's ownership and
complete-history checks; this set never authorizes blind cross-account replay.
"""


def stored_access_token_expires_at(
    encrypted_access_token: bytes | None,
    encryptor: TokenEncryptor,
) -> float | None:
    """Return the stored access token's JWT expiry in epoch seconds when known."""
    if not encrypted_access_token:
        return None
    try:
        access_token = encryptor.decrypt(encrypted_access_token)
    except Exception:
        return None
    expires_ms = token_expiry_epoch_ms(access_token)
    return None if expires_ms is None else expires_ms / 1000.0


def account_access_token_expires_at(account: Account, encryptor: TokenEncryptor) -> float | None:
    """Return an account snapshot's known access-token expiry."""
    encrypted_access_token = getattr(account, "access_token_encrypted", None)
    return stored_access_token_expires_at(encrypted_access_token, encryptor)


def all_accounts_require_reauthentication(
    accounts: Collection[Account],
    encryptor: TokenEncryptor,
    *,
    now: float,
) -> bool:
    """Return whether every candidate requires new authentication.

    Keep the existing call contract; credential expiry no longer overrides a
    persisted authentication failure.
    """
    return bool(accounts) and all(account.status == AccountStatus.REAUTH_REQUIRED for account in accounts)
