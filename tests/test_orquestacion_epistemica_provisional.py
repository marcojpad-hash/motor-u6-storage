"""Contract tests for provisional epistemic orchestration v0.1.

These tests execute a small reference model of the protocol. They do NOT import
or execute U6/V15.3 and do NOT measure predictive accuracy of the real engine.
"""
from dataclasses import dataclass, field
import unittest


@dataclass
class Case:
    case_id: str
    domain: str
    model: str
    ranked: tuple
    true_label: str                 # sealed evaluator-only field
    unresolved: bool = False
    pending: tuple = ()
    contradiction: bool = False
    fresh_signal: str | None = None
    guardian_flags: tuple = ()
    benign_terms: tuple = ()


@dataclass
class Config:
    guardians: bool = True
    closure_gate: bool = True
    open_set: bool = True
    memory: bool = True
    adaptive: bool = True


@dataclass
class Memory:
    rows: dict = field(default_factory=dict)

    def write(self, case_id, payload, source_sha):
        self.rows.setdefault((case_id, source_sha), payload)

    def read(self, case_id):
        return [(sha, payload) for (cid, sha), payload in self.rows.items()
                if cid == case_id]


def classify_profile_term(term: str, independent_context_cue: bool) -> str | None:
    """A term alone is not an alert; require an independent contextual cue."""
    neutral = {"elegido", "delegado", "pública"}
    if term.lower() in neutral and not independent_context_cue:
        return None
    return f"PROFILE_CONTEXT:{term}" if independent_context_cue else None


def run_protocol(case: Case, cfg: Config, memory: Memory | None = None):
    """Reference controller; truth label is never read by this function."""
    ranking = list(case.ranked)
    marks = list(case.guardian_flags) if cfg.guardians else []
    before_guard = tuple(ranking)
    after_guard = tuple(ranking)  # guardian stage is observational only

    retrieved = memory.read(case.case_id) if cfg.memory and memory else []

    adaptive_steps = 0
    if cfg.adaptive and (case.unresolved or case.contradiction):
        adaptive_steps = 1
        if case.fresh_signal and case.fresh_signal in ranking:
            ranking.remove(case.fresh_signal)
            ranking.insert(0, case.fresh_signal)

    candidate_set = tuple(ranking[:3]) if cfg.open_set else tuple(ranking[:1])
    blockers = tuple(case.pending)
    closure_allowed = not blockers if cfg.closure_gate else True

    return {
        "ranking": tuple(ranking),
        "H1": ranking[0] if ranking else None,
        "candidate_set": candidate_set,
        "marks": tuple(marks),
        "ranking_unchanged_by_guardians": before_guard == after_guard,
        "closure_allowed": closure_allowed,
        "blockers": blockers if cfg.closure_gate else (),
        "retrieved_memory": tuple(retrieved),
        "adaptive_steps": adaptive_steps,
        "operation_count": 1 + len(marks) + len(retrieved) + adaptive_steps
                           + int(cfg.closure_gate),
    }


class TestGuardianAblation(unittest.TestCase):
    def test_guardians_mark_without_changing_prediction(self):
        c = Case("g1", "biography", "model-A", ("A", "B", "C"), "B",
                 guardian_flags=("CONTRADICTION",))
        on = run_protocol(c, Config(guardians=True))
        off = run_protocol(c, Config(guardians=False))
        self.assertEqual(on["H1"], off["H1"])
        self.assertEqual(on["candidate_set"], off["candidate_set"])
        self.assertEqual(on["marks"], ("CONTRADICTION",))
        self.assertEqual(off["marks"], ())
        self.assertTrue(on["ranking_unchanged_by_guardians"])

    def test_neutral_words_alone_do_not_trigger_profile_guard(self):
        marks = [classify_profile_term(t, False)
                 for t in ("elegido", "delegado", "pública")]
        self.assertEqual(marks, [None, None, None])

    def test_profile_guard_requires_independent_context_cue(self):
        self.assertIsNone(classify_profile_term("elegido", False))
        self.assertEqual(classify_profile_term("elegido", True),
                         "PROFILE_CONTEXT:elegido")


class TestClosureGateAblation(unittest.TestCase):
    def test_unresolved_pending_blocks_only_when_gate_on(self):
        c = Case("gate1", "event", "model-A", ("A", "B"), "B",
                 pending=("EVIDENCE_GAP",))
        on = run_protocol(c, Config(closure_gate=True))
        off = run_protocol(c, Config(closure_gate=False))
        self.assertFalse(on["closure_allowed"])
        self.assertTrue(off["closure_allowed"])
        self.assertEqual(on["blockers"], ("EVIDENCE_GAP",))

    def test_no_pending_allows_closure(self):
        c = Case("gate2", "science", "model-B", ("A",), "A")
        self.assertTrue(run_protocol(c, Config(closure_gate=True))["closure_allowed"])


class TestOpenSetAblation(unittest.TestCase):
    def test_open_set_increases_coverage_but_costs_precision(self):
        c = Case("set1", "biography", "model-A", ("A", "B", "C"), "C")
        single = run_protocol(c, Config(open_set=False))
        open_ = run_protocol(c, Config(open_set=True))
        self.assertNotIn(c.true_label, single["candidate_set"])
        self.assertIn(c.true_label, open_["candidate_set"])
        self.assertEqual(len(single["candidate_set"]), 1)
        self.assertEqual(len(open_["candidate_set"]), 3)
        self.assertEqual(1 / len(open_["candidate_set"]), 1 / 3)

    def test_open_set_does_not_claim_probability(self):
        c = Case("set2", "science", "model-B", ("A", "B"), "A")
        out = run_protocol(c, Config(open_set=True))
        self.assertFalse(any("prob" in k.lower() for k in out))


class TestMemoryAblation(unittest.TestCase):
    def test_memory_is_provenance_context_not_predictor_vote(self):
        c = Case("mem1", "event", "model-A", ("A", "B"), "B")
        mem = Memory()
        mem.write("mem1", {"note": "prior observation"}, "sha-case-1")
        on = run_protocol(c, Config(memory=True), mem)
        off = run_protocol(c, Config(memory=False), mem)
        self.assertEqual(on["H1"], off["H1"])
        self.assertEqual(len(on["retrieved_memory"]), 1)
        self.assertEqual(off["retrieved_memory"], ())

    def test_memory_is_idempotent_and_case_scoped(self):
        mem = Memory()
        mem.write("case-A", {"v": 1}, "same-sha")
        mem.write("case-A", {"v": 1}, "same-sha")
        mem.write("case-B", {"v": 2}, "other-sha")
        self.assertEqual(len(mem.rows), 2)
        self.assertEqual(len(mem.read("case-A")), 1)
        self.assertEqual(len(mem.read("case-B")), 1)


class TestAdaptiveAblation(unittest.TestCase):
    def test_adaptive_reruns_only_on_unresolved_state_and_can_resolve(self):
        c = Case("ad1", "science", "model-A", ("A", "B", "C"), "B",
                 unresolved=True, fresh_signal="B")
        fixed = run_protocol(c, Config(adaptive=False))
        adaptive = run_protocol(c, Config(adaptive=True))
        self.assertEqual(fixed["H1"], "A")
        self.assertEqual(adaptive["H1"], "B")
        self.assertEqual(adaptive["adaptive_steps"], 1)
        self.assertGreater(adaptive["operation_count"], fixed["operation_count"])

    def test_adaptive_does_not_run_without_trigger(self):
        c = Case("ad2", "event", "model-B", ("A", "B"), "A")
        out = run_protocol(c, Config(adaptive=True))
        self.assertEqual(out["adaptive_steps"], 0)


class TestThreeCrossControls(unittest.TestCase):
    def test_false_positive_control_across_neutral_domains(self):
        cases = [
            Case("n1", "biography", "model-A", ("A",), "A",
                 benign_terms=("elegido",)),
            Case("n2", "science", "model-B", ("A",), "A",
                 benign_terms=("pública",)),
            Case("n3", "event", "model-C", ("A",), "A",
                 benign_terms=("delegado",)),
        ]
        false_alarms = sum(classify_profile_term(term, False) is not None
                           for c in cases for term in c.benign_terms)
        self.assertEqual(false_alarms, 0)

    def test_compute_budget_is_bounded(self):
        c = Case("cost1", "science", "model-A", ("A", "B"), "B",
                 unresolved=True, contradiction=True, fresh_signal="B",
                 guardian_flags=("CHECK_1", "CHECK_2"))
        out = run_protocol(c, Config(), Memory())
        self.assertLessEqual(out["operation_count"], 10)

    def test_protocol_invariants_across_domains_and_models(self):
        cases = [
            Case("x1", "biography", "model-A", ("A", "B"), "B",
                 pending=("GAP",)),
            Case("x2", "science", "model-B", ("A", "B"), "A",
                 unresolved=True),
            Case("x3", "event", "model-C", ("B", "A"), "B",
                 contradiction=True),
        ]
        for c in cases:
            out = run_protocol(c, Config())
            self.assertEqual(out["H1"], out["ranking"][0])
            self.assertTrue(set(out["candidate_set"]).issubset(set(out["ranking"])))
            self.assertEqual(out["closure_allowed"], not bool(c.pending))


if __name__ == "__main__":
    unittest.main(verbosity=2)
