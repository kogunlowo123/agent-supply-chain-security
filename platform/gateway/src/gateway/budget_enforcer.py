"""LLM budget enforcement — tracks and limits token usage per tenant."""
from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class BudgetState:
    tokens_used: int = 0
    requests_made: int = 0
    window_start: float = field(default_factory=time.time)


class BudgetEnforcer:
    """Enforces per-tenant LLM token and request budgets."""

    def __init__(
        self,
        max_tokens_per_minute: int = 100_000,
        max_requests_per_minute: int = 100,
    ) -> None:
        self.max_tokens = max_tokens_per_minute
        self.max_requests = max_requests_per_minute
        self._state: dict[str, BudgetState] = defaultdict(BudgetState)

    def _reset_if_stale(self, tenant_id: str) -> None:
        state = self._state[tenant_id]
        if time.time() - state.window_start >= 60:
            self._state[tenant_id] = BudgetState()

    def check_and_consume(self, tenant_id: str, tokens: int) -> bool:
        """
        Check if the tenant has remaining budget and consume tokens.
        Returns True if allowed, False if budget exceeded.
        """
        self._reset_if_stale(tenant_id)
        state = self._state[tenant_id]

        if state.requests_made >= self.max_requests:
            logger.warning("Rate limit exceeded for tenant %s: requests", tenant_id)
            return False

        if state.tokens_used + tokens > self.max_tokens:
            logger.warning("Token budget exceeded for tenant %s", tenant_id)
            return False

        state.tokens_used += tokens
        state.requests_made += 1
        return True

    def get_usage(self, tenant_id: str) -> dict[str, int]:
        self._reset_if_stale(tenant_id)
        state = self._state[tenant_id]
        return {
            "tokens_used": state.tokens_used,
            "requests_made": state.requests_made,
            "tokens_remaining": max(0, self.max_tokens - state.tokens_used),
        }
