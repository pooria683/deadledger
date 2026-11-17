"""Adapter registry: the extension point.

An adapter is any object with ``ecosystem``, ``lockfile_names`` and
``gather(name, version) -> PackageEvidence``.  To support a new ecosystem you
write one module, register it in :data:`ADAPTERS`, and add a fixture profile
to the tests.  Nothing else in DeadLedger needs to change -- the mortality
engine is ecosystem-agnostic because it only reads
:class:`~deadledger.evidence.PackageEvidence`.

Adapters are *collectors*.  They must not make verdict decisions; that
belongs in ``mortality.py`` where it can be reviewed by people who argue
about thresholds rather than about HTTP.
"""

from __future__ import annotations

from .base import Adapter, AdapterCapabilities
from .crates import CratesAdapter
from .npm import NpmAdapter
from .pypi import PyPIAdapter

ADAPTERS: dict[str, Adapter] = {
    "pypi": PyPIAdapter(),
    "npm": NpmAdapter(),
    "crates": CratesAdapter(),
}

__all__ = [
    "ADAPTERS",
    "Adapter",
    "AdapterCapabilities",
    "CratesAdapter",
    "NpmAdapter",
    "PyPIAdapter",
    "get_adapter",
    "adapter_for_lockfile",
]


def get_adapter(ecosystem: str) -> Adapter:
    try:
        return ADAPTERS[ecosystem]
    except KeyError:
        raise KeyError(
            f"no adapter for {ecosystem!r}; available: {', '.join(sorted(ADAPTERS))}"
        ) from None


def adapter_for_lockfile(filename: str) -> Adapter | None:
    lowered = filename.lower()
    for adapter in ADAPTERS.values():
        for candidate in adapter.lockfile_names:
            if lowered.endswith(candidate.lower()):
                return adapter
    return None
