"""Unit tests for SLSA provenance verification."""
from __future__ import annotations

import sys
import os

import pytest


def _setup_path():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api"))


class TestProvenanceVerification:
    """Tests for SLSA provenance verification logic."""

    def test_missing_provenance_fails_verification(self):
        """No provenance data results in verification failure."""
        _setup_path()
        from src.api.routes.v1.provenance import verify_slsa_provenance

        result = verify_slsa_provenance("sha256:" + "a" * 64, None)

        assert result.verified is False
        assert result.slsa_level == 0
        assert len(result.violations) > 0

    def test_found_provenance_passes_verification(self):
        """Valid provenance data passes verification at SLSA level 3."""
        _setup_path()
        from src.api.routes.v1.provenance import verify_slsa_provenance

        provenance_data = {"found": True, "digest": "sha256:" + "a" * 64}
        result = verify_slsa_provenance("sha256:" + "a" * 64, provenance_data)

        assert result.verified is True
        assert result.slsa_level == 3
        assert len(result.violations) == 0

    def test_not_found_provenance_fails_verification(self):
        """Provenance data with found=False fails verification."""
        _setup_path()
        from src.api.routes.v1.provenance import verify_slsa_provenance

        provenance_data = {"found": False}
        result = verify_slsa_provenance("sha256:" + "b" * 64, provenance_data)

        assert result.verified is False
        assert len(result.violations) > 0

    def test_invalid_digest_format_raises_error(self):
        """Invalid digest format raises HTTP 422."""
        _setup_path()
        import asyncio
        from fastapi import HTTPException
        from src.api.routes.v1.provenance import get_provenance

        with pytest.raises(HTTPException) as exc_info:
            asyncio.get_event_loop().run_until_complete(get_provenance("invalid-digest"))

        assert exc_info.value.status_code == 422
