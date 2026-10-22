"""Regression tests for cost assumptions, especially resources left running."""
import unittest
from dataclasses import replace
from decimal import Decimal as D
from cost_model import Scenario, dollars, estimate, number


class CostModelTests(unittest.TestCase):
    def test_default_48_hours(self):
        rows = estimate(Scenario())
        self.assertEqual(dollars(rows["incremental_total"]), "28.77")
        self.assertEqual(dollars(rows["ecosystem_total"]), "188.77")

    def test_80_hours(self):
        s = replace(Scenario(), cluster_hours=D(80), worker_hours=D(80),
                    network_hours=D(80), volume_hours=D(80))
        self.assertEqual(dollars(estimate(s)["ecosystem_total"]), "197.95")

    def test_always_on(self):
        s = replace(Scenario(), cluster_hours=D(730), worker_hours=D(730),
                    network_hours=D(730), volume_hours=D(730))
        self.assertEqual(dollars(estimate(s)["ecosystem_total"]), "384.43")

    def test_zero_workers_does_not_stop_control_plane(self):
        s = replace(Scenario(), cluster_hours=D(730), worker_hours=D(0))
        self.assertEqual(estimate(s)["eks_control_plane"], D(73))
        self.assertEqual(estimate(s)["workers_allowance"], D(0))

    def test_retained_network_has_independent_lifetime(self):
        s = replace(Scenario(), network_hours=D(730))
        self.assertEqual(estimate(s)["nat_hourly"], D("32.85"))
        self.assertEqual(estimate(s)["public_ipv4"], D("10.95"))

    def test_extended_support_is_explicit(self):
        s = replace(Scenario(), cluster_hours=D(730), extended_support=True)
        self.assertEqual(estimate(s)["eks_control_plane"], D(438))

    def test_destroyed_does_not_erase_retained_allowance(self):
        s = replace(Scenario(), cluster_hours=D(0), worker_hours=D(0),
                    network_hours=D(0), volume_hours=D(0))
        self.assertEqual(estimate(s)["incremental_total"], D(15))

    def test_invalid_numbers(self):
        for value in ("NaN", "Infinity", "-1", "bad", True, "1000001"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                number(value)

    def test_invalid_resource_counts(self):
        with self.assertRaises(ValueError):
            estimate(replace(Scenario(), nodes=D("1.5")))

    def test_invalid_lifetimes(self):
        for changes in ({"worker_hours": D(49)}, {"volume_hours": D(20)},
                        {"cluster_hours": D(731)}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                estimate(replace(Scenario(), **changes))

    def test_missing_ip_cost_rejected(self):
        with self.assertRaises(ValueError):
            estimate(replace(Scenario(), public_ips=D(0)))

    def test_zero_baseline_is_not_overridden(self):
        rows = estimate(replace(Scenario(), baseline=D(0)))
        self.assertEqual(rows["ecosystem_total"], rows["incremental_total"])

    def test_totals_sum_unrounded_rows(self):
        rows = estimate(Scenario())
        total = sum((v for k, v in rows.items() if not k.endswith("total")), D(0))
        self.assertEqual(rows["incremental_total"], total)

    def test_two_nat_gateways_have_explicit_ip_cost(self):
        a = estimate(Scenario())
        b = estimate(replace(Scenario(), nat_gateways=D(2), public_ips=D(4)))
        self.assertEqual(b["incremental_total"] - a["incremental_total"], D("2.400"))


if __name__ == "__main__":
    unittest.main()
