"""Check synthetic fixture arithmetic; this is not a live-agent evaluation."""
import csv
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(sys.argv.pop(1)) if len(sys.argv) > 1 else Path("/evaluation")


class FixtureTests(unittest.TestCase):
    def test_population_and_cash_return(self):
        with (ROOT / "inputs/02-active-tape.csv").open() as handle:
            rows = list(csv.DictReader(handle))
        report = json.loads((ROOT / "inputs/03-stored-engine-report.json").read_text())
        m = report["metrics"]
        self.assertEqual(len(rows), 4)
        for column, key in (("funded", "principal_funded"), ("cash_collected", "cash_collected"), ("renewal_credit", "renewal_credits")):
            self.assertEqual(sum(D(r[column]) for r in rows), D(str(m[key])))
        self.assertEqual(D(str(m["cash_collected"])) / D(str(m["principal_funded"])), D("0.5"))
        self.assertEqual((D(str(m["cash_collected"])) + D(str(m["renewal_credits"]))) / D(str(m["principal_funded"])), D(str(m["moic"])))
        self.assertTrue(report["fictional"])
        self.assertTrue(report["not_a_live_run"])
        self.assertFalse(report["ai_review"]["ran"])

    def test_cash_bridge_and_contractual_illustration(self):
        inputs = json.loads((ROOT / "inputs/04-financial-inputs.json").read_text())
        amounts = {key: D(str(value)) for key, value in inputs.items() if type(value) is int}
        movement = (amounts["reported_net_income"] + amounts["noncash_provision"]
                    - amounts["cash_funded_receivables_increase"] - amounts["owner_distribution"]
                    + amounts["other_net_cash_movement"])
        self.assertEqual(amounts["opening_cash"] + movement, amounts["ending_cash"])
        unrestricted = amounts["ending_cash"] - amounts["restricted_ending_cash"]
        self.assertEqual(amounts["debt_service_next_30_days"] - unrestricted, D(70000))
        self.assertFalse(inputs["drawability_verified"])
        self.assertFalse(inputs["covenant_definitions_provided"])
        report = json.loads((ROOT / "inputs/03-stored-engine-report.json").read_text())
        example = report["illustration"]
        gross = (D(str(example["factor"])) - 1) * 365 / example["term_days"]
        net = (D(str(example["factor"])) - 1 - D(str(example["commission_pct"]))) * 365 / example["term_days"]
        self.assertEqual((gross * 100).quantize(D(".01")), D("121.67"))
        self.assertEqual((net * 100).quantize(D(".01")), D("101.39"))

    def test_source_versions_and_unexecuted_rubric(self):
        paths = [ROOT / f"inputs/delivery-{i}/statement.md" for i in (1, 2)]
        hashes = {hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        self.assertEqual(len(hashes), 2)
        rubric = json.loads((ROOT / "rubric.json").read_text())
        self.assertEqual(rubric["status"], "not_run")
        ids = [check["id"] for check in rubric["checks"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 10)
        self.assertTrue(all(c["required"] and c["prohibited"] and c["critical"] for c in rubric["checks"]))


if __name__ == "__main__":
    unittest.main()