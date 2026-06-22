"""Policy Intelligence Platform — enterprise RAG for insurance policies."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from policy_intel.pipeline import PolicyPipeline

__all__ = ["PolicyPipeline"]


def __getattr__(name: str):
    if name == "PolicyPipeline":
        from policy_intel.pipeline import PolicyPipeline

        return PolicyPipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
