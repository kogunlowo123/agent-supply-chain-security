"""LangGraph agent state definitions."""
from __future__ import annotations

from typing import Annotated, Any

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class SBOMAnalyzerState(BaseModel):
    """State for the SBOM analyzer agent."""

    messages: Annotated[list[Any], add_messages] = Field(default_factory=list)
    sbom_id: str = ""
    sbom_content: dict[str, Any] = Field(default_factory=dict)
    policy_violations: list[str] = Field(default_factory=list)
    policy_warnings: list[str] = Field(default_factory=list)
    rag_context: str = ""
    report: str = ""
    citations: list[str] = Field(default_factory=list)
    error: str | None = None


class ProvenanceVerifierState(BaseModel):
    """State for the provenance verifier agent."""

    messages: Annotated[list[Any], add_messages] = Field(default_factory=list)
    image_digest: str = ""
    provenance_data: dict[str, Any] | None = None
    slsa_level: int = 0
    violations: list[str] = Field(default_factory=list)
    report: str = ""
    error: str | None = None


class DependencyAuditorState(BaseModel):
    """State for the dependency auditor agent."""

    messages: Annotated[list[Any], add_messages] = Field(default_factory=list)
    packages: list[dict[str, Any]] = Field(default_factory=list)
    vulnerability_findings: list[dict[str, Any]] = Field(default_factory=list)
    policy_decision: str = "ALLOW"
    remediations: list[str] = Field(default_factory=list)
    report: str = ""
    error: str | None = None
