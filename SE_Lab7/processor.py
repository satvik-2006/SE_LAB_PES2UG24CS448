"""Input processing functions for cloud storage tiers."""

import math
import re
from decimal import Decimal, localcontext


def parse_storage_quota(quota_str):
    """Return a nonnegative MB/GB/TB quota in GB, or an error message."""
    if not isinstance(quota_str, str) or len(quota_str) > 64:
        return "Invalid storage quota"
    match = re.fullmatch(r"([0-9]+)(MB|GB|TB)", quota_str.strip().upper())
    if match is None:
        return "Invalid storage quota"
    multipliers = {"MB": Decimal("0.001"), "GB": Decimal(1), "TB": Decimal(1000)}
    with localcontext() as context:
        context.prec = max(28, len(match.group(1)) + 5)
        value = Decimal(match.group(1))
        gb_total = value * multipliers[match.group(2)]
        return f"Quota: {gb_total:.2f} GB"

def compute_compression_ratio(size_metric_str):
    """Return a finite raw/compressed ratio, or None for invalid measurements."""
    if not isinstance(size_metric_str, str) or len(size_metric_str) > 128:
        return None
    parts = size_metric_str.split(":")
    if len(parts) != 2:
        return None
    try:
        raw_bytes, comp_bytes = (float(part.strip()) for part in parts)
    except ValueError:
        return None
    if not (math.isfinite(raw_bytes) and math.isfinite(comp_bytes)):
        return None
    if raw_bytes < 0 or comp_bytes <= 0:
        return None
    ratio = raw_bytes / comp_bytes
    return round(ratio, 2) if math.isfinite(ratio) else None

def lookup_bandwidth_tier_rate(tier_descriptor):
    """Return the rate for a known tier prefix, or None for an unknown tier."""
    if not isinstance(tier_descriptor, str) or len(tier_descriptor) > 128:
        return None
    prefix = tier_descriptor.strip().upper()[:3]
    tier_rates = {
        "HOT": 0.08,
        "COL": 0.05,
        "ARC": 0.02
    }
    return tier_rates.get(prefix)

def main():
    print("==== Running parse_storage_quota ====")
    q_input = _read_input("Enter quota (e.g. 500MB, 10GB, 2TB): ")
    print(parse_storage_quota(q_input))

    print("\n==== Running compute_compression_ratio ====")
    c_input = _read_input("Enter raw:compressed bytes (e.g. 1024:256): ")
    ratio = compute_compression_ratio(c_input)
    print("Compression Ratio:", ratio if ratio is not None else "Invalid measurement")

    print("\n==== Running lookup_bandwidth_tier_rate ====")
    t_input = _read_input("Enter tier descriptor (e.g. HOT_TIER, COLD, ARCHIVE): ")
    rate = lookup_bandwidth_tier_rate(t_input)
    print("Rate per GB: $", rate if rate is not None else "Unknown tier")


def _read_input(prompt):
    try:
        return input(prompt)
    except EOFError:
        return None

if __name__ == "__main__":
    main()
