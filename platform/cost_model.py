#!/usr/bin/env python3
"""Offline scenario calculator, not a bill, quote, budget enforcer, or AWS client."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, fields
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

D = Decimal
MONTH_HOURS = D("730")  # Comparison convention, not an AWS billing-month definition.
RATE_DATE = "2026-09-06"
SOURCES = {
    "eks": "https://aws.amazon.com/eks/pricing/",
    "network": "https://aws.amazon.com/vpc/pricing/",
    "alb": "https://aws.amazon.com/elasticloadbalancing/pricing/",
    "storage": "https://aws.amazon.com/ebs/pricing/",
}


def number(value: object) -> Decimal:
    """Reject non-finite/negative values instead of producing misleading estimates."""
    try:
        result = D(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Inputs must be finite, non-negative numbers") from None
    if not result.is_finite() or result < 0 or result > D("1000000"):
        raise ValueError("Inputs must be finite numbers between zero and one million")
    return result


@dataclass(frozen=True)
class Scenario:
    baseline: Decimal = D("160")
    cluster_hours: Decimal = D("48")
    worker_hours: Decimal = D("48")
    network_hours: Decimal = D("48")
    volume_hours: Decimal = D("48")
    nodes: Decimal = D("2")
    node_hourly: Decimal = D("0.05")  # Explicit allowance; NOT a verified instance quote.
    nat_gateways: Decimal = D("1")
    albs: Decimal = D("1")
    public_ips: Decimal = D("3")  # One NAT IP plus two baseline internet-facing ALB IPs.
    ebs_gb_per_node: Decimal = D("20")
    retained_monthly: Decimal = D("5")  # Allowance: state, images, retained logs/storage.
    usage_reserve: Decimal = D("10")  # Not an upper bound on traffic or telemetry costs.
    extended_support: bool = False


def estimate(s: Scenario) -> dict[str, Decimal]:
    for field in fields(s):
        if field.name != "extended_support":
            value = getattr(s, field.name)
            if not isinstance(value, Decimal):
                raise ValueError("Scenario numeric fields must be Decimal values")
            number(value)
    if not isinstance(s.extended_support, bool):
        raise ValueError("extended_support must be boolean")
    for name in ("cluster_hours", "worker_hours", "network_hours", "volume_hours"):
        if getattr(s, name) > MONTH_HOURS:
            raise ValueError("Hours must not exceed the 730-hour comparison window")
    for name in ("nodes", "nat_gateways", "albs", "public_ips"):
        if getattr(s, name) != getattr(s, name).to_integral_value():
            raise ValueError("Resource counts must be whole numbers")
    if s.worker_hours > s.cluster_hours or s.worker_hours > s.volume_hours:
        raise ValueError("Worker hours cannot exceed cluster or root-volume hours")
    if s.network_hours and s.public_ips < s.nat_gateways + D("2") * s.albs:
        raise ValueError("This IPv4 model requires one IP per NAT and at least two per ALB")
    rows = {
        "eks_control_plane": s.cluster_hours * (D("0.60") if s.extended_support else D("0.10")),
        "workers_allowance": s.worker_hours * s.nodes * s.node_hourly,
        "nat_hourly": s.network_hours * s.nat_gateways * D("0.045"),
        "alb_hourly": s.network_hours * s.albs * D("0.0225"),
        "public_ipv4": s.network_hours * s.public_ips * D("0.005"),
        "root_ebs_estimate": s.volume_hours / MONTH_HOURS * s.nodes * s.ebs_gb_per_node * D("0.08"),
        "retained_monthly_allowance": s.retained_monthly,
        "variable_usage_reserve": s.usage_reserve,
    }
    rows["incremental_total"] = sum(rows.values(), D("0"))
    rows["ecosystem_total"] = s.baseline + rows["incremental_total"]
    return rows


def dollars(value: Decimal) -> str:
    return str(value.quantize(D("0.01"), rounding=ROUND_HALF_UP))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for field in fields(Scenario):
        flag = "--" + field.name.replace("_", "-")
        if field.name == "extended_support":
            parser.add_argument(flag, action="store_true")
        else:
            parser.add_argument(flag, type=number, default=field.default)
    args = parser.parse_args()
    try:
        rows = estimate(Scenario(**vars(args)))
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps({
        "status": "planning_estimate_not_measured_spend",
        "region": "us-east-1 illustrative IPv4 scenario",
        "rate_review_date": RATE_DATE,
        "comparison_hours": str(MONTH_HOURS),
        "sources": SOURCES,
        "inputs": {k: v if isinstance(v, bool) else str(v) for k, v in vars(args).items()},
        "usd": {key: dollars(value) for key, value in rows.items()},
        "exclusions": [
            "Taxes, credits, support subscriptions and third-party bills",
            "Usage beyond the reserve: ALB LCUs, NAT GB, transfer, logs, API calls, builds",
            "CPU surplus credits, paid EKS add-ons and expanded node/IP/storage counts",
            "Orphaned resources beyond the explicitly supplied lifetime assumptions",
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
