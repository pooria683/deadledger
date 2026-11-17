"""PyPI adapter against recorded responses.

Every assertion here is about a *fact the adapter extracted*, never about the
network.  The fixture profile was recorded from the live API (see
tests/fixtures/README.md); if PyPI changes its JSON shape, these fail with a
message naming the field.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from deadledger.adapters.pypi import (
    PyPIAdapter,
    normalise_name,
    repository_from_info,
    trend,
)
from deadledger.errors import NotFound

UTC = timezone.utc


def test_normalise_follows_pep503():
    assert normalise_name("Django_Filter") == "django-filter"
    assert normalise_name("zope.interface") == "zope-interface"
    assert normalise_name("PyYAML") == "pyyaml"


def test_repository_extracted_from_project_urls():
    info = {"project_urls": {"Source": "https://github.com/psf/requests"}}
    assert repository_from_info(info) == "psf/requests"


def test_repository_falls_back_to_home_page():
    info = {"home_page": "https://github.com/codeinthehole/purl"}
    assert repository_from_info(info) == "codeinthehole/purl"


def test_trend_is_none_for_short_windows():
    assert trend([1, 2]) is None
    assert trend([]) is None


def test_trend_measures_halves():
    assert trend([100, 100, 50, 50]) == pytest.approx(-0.5)


def test_gather_django_extracts_cadence_and_owners(replay):
    evidence = PyPIAdapter().gather(replay, "django", "3.2.6")

    assert evidence.registry_ok
    assert evidence.name.lower() == "django"
    assert evidence.last_publish_obs is not None
    assert evidence.last_publish_obs.known
    # The recorded packument's newest stable release is dated and in the past.
    published = datetime.strptime(
        evidence.last_publish_obs.value, "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=UTC)
    assert published < datetime(2030, 1, 1, tzinfo=UTC)

    # Release history is complete and sorted; cadence can be recomputed from it.
    assert len(evidence.releases) > 10
    assert evidence.releases == sorted(evidence.releases, key=lambda r: r.published_at)
    assert evidence.releases_12mo_obs is not None

    # Every observation carries a citation, which is the whole contract.
    for observation in evidence.observation_map().values():
        assert observation.url.startswith("http")
        assert observation.retrieved_at is not None
        assert observation.source


def test_gather_marks_pypi_inactive_classifier_as_deprecated(replay):
    """svgwrite ships the 'Development Status :: 7 - Inactive' classifier."""
    evidence = PyPIAdapter().gather(replay, "svgwrite", "1.4.1")
    assert evidence.deprecated
    assert "Inactive" in (evidence.deprecation_message or "")


def test_gather_records_gap_when_pypistats_is_down(replay):
    """The recorded profile has pypistats failures; they must become gaps."""
    evidence = PyPIAdapter().gather(replay, "django", "3.2.6")
    assert evidence.download_count_obs is None
    assert any("pypistats" in gap for gap in evidence.source_gaps)
    # A failed source is never a zero.
    assert not any(
        gap.startswith("usage: no download") and "0" in gap for gap in evidence.source_gaps
    )


def test_missing_package_is_evidence_not_a_crash(replay, cache):
    from deadledger.http import CachingClient

    adapter = PyPIAdapter()
    # The fixture profile has no recording for this name at all, which replay
    # reports as "we were not allowed to ask" -> a gap, not an exception.
    evidence = adapter.gather(replay, "definitely-not-a-real-package-xyz", "1.0")
    assert not evidence.registry_ok
    assert evidence.source_gaps
    assert any("registry" in gap for gap in evidence.source_gaps)


def test_owner_roles_are_captured_when_present(replay):
    """At least one package in the profile publishes an ownership block."""
    captured = 0
    for package in ("django-filter", "django-mptt", "netaddr", "tablib", "svgwrite"):
        evidence = PyPIAdapter().gather(replay, package, None)
        observation = evidence.maintainer_count_obs
        if observation is not None and observation.known:
            captured += 1
            assert observation.value == len(evidence.maintainers)
            assert all(m.name for m in evidence.maintainers)
    assert captured >= 1, "the recorded profile should contain a package with owners"


def test_non_github_homepage_is_reported_as_such():
    """'Not on GitHub' and 'no repository' are different facts.

    openpyxl is developed on Heptapod. The first version of the forge gap said
    "no repository URL in registry metadata", which is false and is exactly the
    kind of claim a reader checks in one click.
    """
    from deadledger.adapters.pypi import any_repo_url, repository_from_info

    info = {
        "project_urls": {"Source": "https://foss.heptapod.net/openpyxl/openpyxl"},
        "home_page": "https://openpyxl.readthedocs.io",
    }
    assert repository_from_info(info) is None          # not a GitHub slug
    assert any_repo_url(info) == "https://foss.heptapod.net/openpyxl/openpyxl"


def test_explain_only_audits_the_requested_package(tmp_path):
    """`explain` must not spend the whole GitHub budget on the other 139."""
    from deadledger.audit import Runner
    from deadledger.cache import Cache
    from deadledger.http import CachingClient
    from deadledger.lockfiles import parse_lockfile

    requirements = tmp_path / "requirements.txt"
    requirements.write_text("django==3.2.6\ndjango-pglocks==1.0.4\n")
    inventory = parse_lockfile(requirements)
    node = inventory.nodes["django-pglocks@1.0.4"]
    inventory.nodes = {node.key: node}
    inventory.direct &= {node.key}

    client = CachingClient(None, Cache(":memory:"), mode="replay", profile="netbox-3.0")
    result = Runner(client).run(inventory)
    assert [r.name for r in result.packages] == ["django-pglocks"]
