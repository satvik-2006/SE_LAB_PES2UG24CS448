"""Property-based checks for the Lab 7 input validation functions."""

from decimal import Decimal

import pytest
from hypothesis import example, given, strategies as st

from processor import (
    compute_compression_ratio,
    lookup_bandwidth_tier_rate,
    parse_storage_quota,
)


@given(st.text(max_size=512) | st.none())
@example(None)
@example("")
@example("-1GB")
@example("1PB")
def test_parse_storage_quota_no_crash(s):
    try:
        result = parse_storage_quota(s)
    except Exception as exc:
        pytest.fail(f"parse_storage_quota crashed for {s!r}: {exc!r}")
    assert isinstance(result, str)


@given(
    value=st.integers(min_value=0, max_value=10**9),
    unit=st.sampled_from(["MB", "GB", "TB"]),
)
@example(value=205, unit="MB")
def test_parse_storage_quota_valid_values(value, unit):
    multiplier = {"MB": Decimal("0.001"), "GB": Decimal(1), "TB": Decimal(1000)}[unit]
    expected = f"Quota: {Decimal(value) * multiplier:.2f} GB"
    assert parse_storage_quota(f"  {value}{unit.lower()}  ") == expected


@pytest.mark.parametrize("bad", [None, "", "-1GB", "1PB", "1.5GB", "GB"])
def test_parse_storage_quota_invalid_values(bad):
    assert parse_storage_quota(bad) == "Invalid storage quota"


@given(st.text(max_size=512) | st.none())
@example(None)
@example("")
@example("1:0")
@example("nan:1")
def test_compute_compression_ratio_safe(s):
    try:
        result = compute_compression_ratio(s)
    except Exception as exc:
        pytest.fail(f"compute_compression_ratio crashed for {s!r}: {exc!r}")
    assert result is None or isinstance(result, float)


@given(
    raw=st.integers(min_value=0, max_value=10**9),
    compressed=st.integers(min_value=1, max_value=10**9),
)
def test_compute_compression_ratio_valid_values(raw, compressed):
    assert compute_compression_ratio(f"{raw}:{compressed}") == round(
        raw / compressed, 2
    )


@pytest.mark.parametrize(
    "bad", [None, "", "1:0", "-1:2", "1:-2", "nan:1", "inf:1", "1:2:3"]
)
def test_compute_compression_ratio_invalid_values(bad):
    assert compute_compression_ratio(bad) is None


@given(st.text(max_size=512) | st.none())
@example(None)
@example("")
@example("UNKNOWN")
def test_lookup_bandwidth_tier_rate_safe(s):
    try:
        result = lookup_bandwidth_tier_rate(s)
    except Exception as exc:
        pytest.fail(f"lookup_bandwidth_tier_rate crashed for {s!r}: {exc!r}")
    assert result is None or result in {0.08, 0.05, 0.02}


@given(st.sampled_from(["HOT_TIER", "COLD", "ARCHIVE"]))
def test_lookup_bandwidth_tier_rate_valid_values(tier):
    expected = {"HOT_TIER": 0.08, "COLD": 0.05, "ARCHIVE": 0.02}[tier]
    assert lookup_bandwidth_tier_rate(f"  {tier.lower()}  ") == expected


@pytest.mark.parametrize("bad", [None, "", "  ", "WARM", "HO"])
def test_lookup_bandwidth_tier_rate_invalid_values(bad):
    assert lookup_bandwidth_tier_rate(bad) is None
