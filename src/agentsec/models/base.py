"""The provider-independent model adapter contract.

Capabilities are reported **explicitly**. A provider that does not honour a
parameter (temperature, seed, tools) must say so; callers then raise
``UnsupportedParameter`` instead of silently defaulting. This keeps traces
honest about what was actually controlled.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict

from .schema import Message, ModelResponse, ToolSpec


class Capabilities(BaseModel):
    """Which request parameters a concrete adapter actually honours."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    supports_temperature: bool
    supports_seed: bool
    supports_tools: bool
    supports_forced_thinking: bool | None = None


class ModelInfo(BaseModel):
    """Identity of a concrete model backing an adapter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: str
    model_id: str
    revision: str = "unpinned"
    notes: str | None = None


@runtime_checkable
class ModelAdapter(Protocol):
    """The only interface the rest of the lab uses to reach a model."""

    def complete(
        self,
        messages: list[Message],
        *,
        temperature: float | None = None,
        seed: int | None = None,
        tools: list[ToolSpec] | None = None,
    ) -> ModelResponse:
        """Return a normalized response for ``messages``.

        Raises ``UnsupportedParameter`` when a supplied argument is not
        advertised by :meth:`capabilities`.
        """
        ...

    def capabilities(self) -> Capabilities:
        """Report which parameters this adapter honours."""
        ...

    def describe(self) -> ModelInfo:
        """Report provider/model identity for the trace."""
        ...
